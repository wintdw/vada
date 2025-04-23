import logging
from fastapi import APIRouter, HTTPException  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from datetime import datetime, timedelta
from typing import Optional

from model.google import GoogleAdsCredentials
from handler.report import get_reports
from handler.customer import get_manager_accounts
from dependency.google import get_google_ads_client

router = APIRouter()


@router.post("/google/reports")
async def fetch_google_reports(
    credentials: GoogleAdsCredentials,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Fetch Google Ads reports using provided credentials

    Args:
        credentials: Google Ads API credentials
        start_date: Start date in YYYY-MM-DD format (default: 7 days ago)
        end_date: End date in YYYY-MM-DD format (default: today)
    """
    try:
        # Initialize client and date range
        ga_client = await get_google_ads_client(credentials)

        end_date = end_date if end_date else datetime.now().date().isoformat()
        start_date = (
            start_date
            if start_date
            else (datetime.now().date() - timedelta(days=7)).isoformat()
        )

        logging.info(f"Fetching reports from {start_date} " f"to {end_date}")

        # Get manager accounts with hierarchy
        manager_accounts = await get_manager_accounts(ga_client)

        # Get campaign reports through hierarchy
        campaign_reports = await get_reports(ga_client, start_date, end_date)

        # Build response with hierarchy information
        response_data = {
            "date_range": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "accounts": {
                "manager_accounts": len(manager_accounts),
                "total_clients": sum(
                    len([c for c in m["child_accounts"] if not c["is_manager"]])
                    for m in manager_accounts
                ),
                "hierarchy": manager_accounts,
            },
            "reports": {
                "total_campaigns": len(
                    set(r["campaign"]["id"] for r in campaign_reports)
                ),
                "total_ad_groups": len(
                    set(r["ad_group"]["id"] for r in campaign_reports)
                ),
                "total_records": len(campaign_reports),
                "data": campaign_reports,
            },
        }

        logging.info(
            f"Returning {len(campaign_reports)} records from "
            f"{response_data['accounts']['total_clients']} client accounts"
        )

        return JSONResponse(content=response_data, status_code=200)

    except Exception as e:
        logging.error(f"Error fetching Google Ads reports: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
