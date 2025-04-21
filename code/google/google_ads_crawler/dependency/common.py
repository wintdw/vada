import os
import json
import logging
from fastapi import Request, HTTPException  # type: ignore

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from model.google import GoogleAdsCredentials


async def get_flows(request: Request):
    """Get flows from application state"""
    return request.app.state.flows


async def get_app_secret_file() -> str:
    """Get Google app secret file path from environment variable"""
    secret_path = os.getenv("GOOGLE_APP_SECRET_FILE")
    if not secret_path:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_APP_SECRET_FILE environment variable is not set",
        )

    if not os.path.exists(secret_path):
        raise HTTPException(
            status_code=500, detail=f"Secret file not found at: {secret_path}"
        )

    return secret_path


async def get_google_ads_client(credentials: GoogleAdsCredentials) -> GoogleAdsClient:
    client_secrets_path = await get_app_secret_file()
    # Get client credentials from environment file if not provided
    if not credentials.client_id or not credentials.client_secret:
        with open(client_secrets_path, "r") as f:
            client_config = json.load(f)["web"]
            credentials.client_id = credentials.client_id or client_config["client_id"]
            credentials.client_secret = (
                credentials.client_secret or client_config["client_secret"]
            )

    # Initialize the Google Ads client
    logging.info("Initializing Google Ads client with credentials: %s", credentials)
    ga_client = GoogleAdsClient.load_from_dict(credentials.dict())

    return ga_client
