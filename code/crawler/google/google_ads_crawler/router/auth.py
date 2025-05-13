import os
import hashlib
import logging
from typing import Dict

from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from google_auth_oauthlib.flow import Flow  # type: ignore
from fastapi.responses import RedirectResponse  # type: ignore

from model.setting import settings
from handler.mysql import set_google_ad_crawl_info
from dependency.google_ad_client import (
    get_flows,
    get_app_secret_file,
)


router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "Google OAuth API is running. Use /auth/url to get authorization URL."
    }


# Modify the route to use the dependency
@router.get("/auth/url")
async def get_auth_url(
    flows: Dict = Depends(get_flows),
    client_secrets_path: str = Depends(get_app_secret_file),
):
    """Generate and return a Google OAuth authorization URL"""
    try:
        scopes = ["https://www.googleapis.com/auth/adwords"]
        redirect_uri = "https://google.vadata.vn/connector/google/auth"

        # Generate a secure random state value
        passthrough_state = hashlib.sha256(os.urandom(1024)).hexdigest()

        # Create OAuth flow using the secret file from dependency
        flow = Flow.from_client_secrets_file(client_secrets_path, scopes=scopes)
        flow.redirect_uri = redirect_uri

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            state=passthrough_state,
            prompt="consent",
            include_granted_scopes="true",
        )

        # Store the flow object using the state as a key
        flows[state] = flow

        # Redirect to authorization URL
        return RedirectResponse(url=authorization_url, status_code=302)

    except Exception as e:
        logging.error(f"Error generating authorization URL: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating authorization URL: {str(e)}"
        )


# Also update the callback route
@router.get("/connector/google/auth")
async def auth_callback(
    flows: Dict = Depends(get_flows), code: str = None, state: str = None
):
    """Handle the OAuth callback from Google and return comprehensive account information"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    if not state or state not in flows:
        raise HTTPException(
            status_code=400, detail="Invalid or expired state parameter"
        )

    try:
        # Retrieve the flow object for this session
        flow = flows[state]

        # Pass the code back into the OAuth module to get a refresh token
        flow.fetch_token(code=code)
        refresh_token = flow.credentials.refresh_token

        # Clean up the flow object
        del flows[state]

        # Configure Google Ads client credentials
        credentials = {
            "refresh_token": refresh_token,
            "client_id": flow.credentials.client_id,
            "client_secret": flow.credentials.client_secret,
            "developer_token": settings.GOOGLE_DEVELOPER_TOKEN,
            "use_proto_plus": True,
        }

        # Store the refresh token in the database
        set_google_ad_crawl_info(
            index_name="google_ad_",
            refresh_token=refresh_token,
            crawl_interval=1440,
        )

        logging.info("OAuth flow completed successfully. Credentials: %s", credentials)
        return RedirectResponse(url=settings.CALLBACK_FINAL_URL, status_code=302)

    except Exception as e:
        logging.error("Error in auth_callback: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
