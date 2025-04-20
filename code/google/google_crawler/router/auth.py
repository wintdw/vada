import os
import json
import hashlib
import logging

from datetime import datetime, timedelta
from typing import Dict
from fastapi import APIRouter, HTTPException  # type: ignore

from google_auth_oauthlib.flow import Flow  # type: ignore
from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from handler import get_google_ads_reports, get_customer_list

router = APIRouter()


@router.get("/")
async def root():
    return {
        "message": "Google OAuth API is running. Use /auth/url to get authorization URL."
    }


@router.get("/auth/url")
async def get_auth_url(flows: dict):
    """Generate and return a Google OAuth authorization URL"""
    try:
        scopes = ["https://www.googleapis.com/auth/adwords"]
        client_secrets_path = "client_secret_960285879954-o9dm5719frfvuqd7j4bbvm962gg1577g.apps.googleusercontent.com.json"
        redirect_uri = "https://google.vadata.vn/connector/google/auth"

        # Generate a secure random state value
        passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

        # Create OAuth flow
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


@router.get("/connector/google/auth")
async def auth_callback(flows: Dict, code: str = None, state: str = None):
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
            "developer_token": "3WREvqoZUexzpH_oDUjOPw",
            "use_proto_plus": True,
        }

        # Initialize the Google Ads client
        client = GoogleAdsClient.load_from_dict(credentials)

        # Set date range (last 30 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        # Get both reports and customer list
        customers = await get_customer_list(client)
        campaign_reports = await get_google_ads_reports(client, start_date, end_date)

        auth_info = {
            "refresh_token": refresh_token,
            "access_token": flow.credentials.token,
            "token_expiry": (
                flow.credentials.expiry.isoformat() if flow.credentials.expiry else None
            ),  # Convert datetime to ISO format
            "token_uri": flow.credentials.token_uri,
            "client_id": flow.credentials.client_id,
            "client_secret": flow.credentials.client_secret,
            "scopes": list(flow.credentials.scopes),  # Convert set to list
        }

        response_data = {
            "auth_info": auth_info,
            "customers": {
                "total_customers": len(customers),
                "customer_list": customers,
            },
            "reports": {
                "date_range": {
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d"),
                },
                "campaigns": campaign_reports,
            },
        }

        # Log auth info and response data
        logging.info("Auth Info: %s", json.dumps(auth_info, indent=2))
        logging.info("Response Data: %s", json.dumps(response_data, indent=2))

        return response_data

    except Exception as e:
        logging.error("Error in auth_callback: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )
