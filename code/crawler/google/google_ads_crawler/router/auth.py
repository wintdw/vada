import os
import hashlib
import logging
import aiohttp  # type: ignore
from typing import Dict

from fastapi import APIRouter, HTTPException, Depends, Query  # type: ignore
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
        "message": "Google OAuth API is running. Use /ingest/partner/google/ads/auth to get authorization URL."
    }


async def get_user_info(token: str) -> Dict:
    """Fetch user information from Google API using the provided token"""
    user_info_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            user_info_endpoint,
            headers={"Authorization": f"Bearer {token}"},
        ) as response:
            if response.status == 200:
                user_info = await response.json()
                logging.debug("User info retrieved: %s", user_info)
                return user_info
            else:
                logging.error("Failed to retrieve user info: %s", response.status)
                return {}


# Modify the route to use the dependency
@router.get("/ingest/partner/google/ad/auth")
async def get_auth_url(
    vada_uid: str = Query(..., description="Vada user ID"),
    flows: Dict = Depends(get_flows),
    client_secrets_path: str = Depends(get_app_secret_file),
):
    """Generate and return a Google OAuth authorization URL"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/adwords",
            "openid",
            "email",
            "profile",
        ]

        redirect_uri = f"{settings.API_BASE_URL}/ingest/partner/google/ad/callback"
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
        flows[state] = {
            "flow": flow,
            "vada_uid": vada_uid,
        }
        logging.debug(f"Flows: {flows}")

        # Redirect to authorization URL
        return RedirectResponse(url=authorization_url, status_code=302)

    except Exception as e:
        logging.error(f"Error generating authorization URL: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating authorization URL: {str(e)}"
        )


@router.get("/ingest/partner/google/ad/callback")
async def auth_callback(code: str, state: str, flows: Dict = Depends(get_flows)):
    """Handle the OAuth callback from Google and return comprehensive account information"""
    if state not in flows:
        raise HTTPException(
            status_code=400, detail="Invalid or expired state parameter"
        )

    try:
        # Retrieve the flow object for this session
        flow = flows[state]["flow"]
        vada_uid = flows[state]["vada_uid"]

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
        logging.debug("OAuth flow completed successfully. Credentials: %s", credentials)

        # Get user information
        user_info = await get_user_info(flow.credentials.token)

        # Store the refresh token in the database
        account_id = user_info["id"]
        account_email = user_info["email"]
        index_name = f"data_ggad_default_{user_info['id']}"
        crawl_info = await set_google_ad_crawl_info(
            account_id=account_id,
            account_email=account_email,
            vada_uid=vada_uid,
            index_name=index_name,
            refresh_token=refresh_token,
            crawl_interval=1440,
        )
        logging.debug("Stored Google Ads crawl info: %s", crawl_info)

        # Redirect to the final URL
        friendly_index_name = f"Google Ads - {user_info['email']}"
        fe_redirect_url = f"{settings.CALLBACK_FINAL_URL}?account_id={account_id}&account_email={account_email}&index_name={index_name}&friendly_index_name={friendly_index_name}"
        return RedirectResponse(url=fe_redirect_url, status_code=302)

    except Exception as e:
        logging.error("Error in auth_callback: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
