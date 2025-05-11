import os
import json
import logging
from fastapi import Request, HTTPException  # type: ignore

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from model.setting import settings


async def get_flows(request: Request):
    """Get flows from application state"""
    return request.app.state.flows


async def get_app_secret_file() -> str:
    """Get Google app secret file path from environment variable"""
    secret_path = settings.GOOGLE_APP_SECRET_FILE
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


async def get_google_ads_client(refresh_token: str) -> GoogleAdsClient:
    ga_credentials = {
        "refresh_token": refresh_token,
        "developer_token": settings.GOOGLE_DEVELOPER_TOKEN,
        "use_proto_plus": True,
    }

    app_secrets_path = await get_app_secret_file()
    with open(app_secrets_path, "r") as f:
        app_config = json.load(f)["web"]
        ga_credentials["client_id"] = app_config["client_id"]
        ga_credentials["client_secret"] = app_config["client_secret"]

    # Initialize the Google Ads client
    logging.debug("Initializing Google Ads client with credentials: %s", ga_credentials)
    ga_client = GoogleAdsClient.load_from_dict(ga_credentials)

    return ga_client
