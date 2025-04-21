import logging
import json
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from datetime import datetime, timedelta

from model.google import GoogleAdsCredentials
from handler.google import get_google_ads_reports
from handler.customer import get_all_accounts
from dependency.common import get_google_ads_client

router = APIRouter()


@router.post("/google/reports")
async def get_google_reports(credentials: GoogleAdsCredentials):
    """Fetch Google Ads reports using provided credentials"""
    try:
        ga_client = await get_google_ads_client(credentials)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        # Get both reports and customer list
        customers = await get_all_accounts(ga_client)
        campaign_reports = await get_google_ads_reports(ga_client, start_date, end_date)

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
