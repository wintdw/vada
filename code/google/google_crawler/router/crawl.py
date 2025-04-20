import logging
import json
import os
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from datetime import datetime, timedelta

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from model.google import GoogleCredentials
from handler.google import get_google_ads_reports, get_customer_list
from dependencies.common import get_app_secret_file

router = APIRouter()


@router.post("/google/reports")
async def get_google_reports(
    credentials: GoogleCredentials,
    client_secrets_path: str = Depends(get_app_secret_file),
):
    """Fetch Google Ads reports using provided credentials"""
    try:
        # Get client credentials from environment file if not provided
        if not credentials.client_id or not credentials.client_secret:
            with open(client_secrets_path, "r") as f:
                client_config = json.load(f)["web"]
                credentials.client_id = (
                    credentials.client_id or client_config["client_id"]
                )
                credentials.client_secret = (
                    credentials.client_secret or client_config["client_secret"]
                )

        # Initialize the Google Ads client
        logging.info("Initializing Google Ads client with credentials: %s", credentials)
        client = GoogleAdsClient.load_from_dict(credentials.dict())

        # Set date range (last 7 days)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        # Get both reports and customer list
        customers = await get_customer_list(client)
        campaign_reports = await get_google_ads_reports(client, start_date, end_date)

        response_data = {
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

        # Log response data
        logging.info("Response Data: %s", json.dumps(response_data, indent=2))

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        logging.error("Error fetching Google Ads reports: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching Google Ads reports: {str(e)}"
        )
