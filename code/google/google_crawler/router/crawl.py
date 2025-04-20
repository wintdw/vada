import logging
import json
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from datetime import datetime, timedelta

from google.ads.googleads.client import GoogleAdsClient  # type: ignore

from model.google import GoogleCredentials
from handler.google import get_google_ads_reports, get_customer_list
from dependencies.common import get_flows

router = APIRouter()


@router.post("/google/reports")
async def get_google_reports(
    credentials: GoogleCredentials, flows: Dict = Depends(get_flows)
):
    """Fetch Google Ads reports using provided credentials"""
    try:
        # Get client credentials from flows if available
        if not credentials.client_id or not credentials.client_secret:
            if credentials.state and credentials.state in flows:
                flow = flows[credentials.state]
                credentials.client_id = (
                    credentials.client_id or flow.credentials.client_id
                )
                credentials.client_secret = (
                    credentials.client_secret or flow.credentials.client_secret
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Client credentials not provided and no valid flow found",
                )

        # Initialize the Google Ads client
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
