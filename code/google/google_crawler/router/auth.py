import os
import hashlib
import logging
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends  # type: ignore

from google_auth_oauthlib.flow import Flow  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from dependencies.common import get_flows


router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "Google OAuth API is running. Use /auth/url to get authorization URL."
    }


# Modify the route to use the dependency
@router.get("/auth/url")
async def get_auth_url(flows: Dict = Depends(get_flows)):
    """Generate and return a Google OAuth authorization URL"""
    try:
        scopes = ["https://www.googleapis.com/auth/adwords"]

        # Get secret file path from environment variable
        client_secrets_path = os.getenv("GOOGLE_APP_SECRET_FILE")
        if not client_secrets_path:
            raise ValueError("GOOGLE_APP_SECRET_FILE environment variable is not set")

        if not os.path.exists(client_secrets_path):
            raise FileNotFoundError(f"Secret file not found at: {client_secrets_path}")

        redirect_uri = "https://google.vadata.vn/connector/google/auth"

        # Generate a secure random state value
        passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

        # Create OAuth flow using the secret file from environment variable
        flow = Flow.from_client_secrets_file(client_secrets_path, scopes=scopes)
        flow.redirect_uri = redirect_uri

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            state=passthrough_val,
            prompt="consent",
            include_granted_scopes="true",
        )

        # Store the flow object using the state as a key
        flows[state] = flow

        return {"authorization_url": authorization_url, "state": state}

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
            "state": state,
            "refresh_token": refresh_token,
            "client_id": flow.credentials.client_id,
            "client_secret": flow.credentials.client_secret,
            "developer_token": "3WREvqoZUexzpH_oDUjOPw",
            "use_proto_plus": True,
        }

        return JSONResponse(status_code=200, content=credentials)

    except Exception as e:
        logging.error("Error in auth_callback: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
