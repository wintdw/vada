import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from model.ga_client import GoogleAdsCredentials
from handler.report import get_reports
from handler.account import get_all_account_hierarchies, get_non_manager_accounts
from handler.persist import post_processing
from dependency.google_ad_client import get_google_ads_client

router = APIRouter()


@router.post("/google/reports")
async def fetch_google_reports(
    credentials: GoogleAdsCredentials,
    start_date: str = Query(
        "", description="Start date in YYYY-MM-DD format", example="2025-04-30"
    ),
    end_date: str = Query(
        "", description="End date in YYYY-MM-DD format", example="2025-04-30"
    ),
    persist: bool = Query(
        False,
        description="Persist data to insert service",
    ),
):
    """Fetch Google Ads reports using provided credentials

    Args:
        credentials: Google Ads API credentials in request body
        start_date: Start date in YYYY-MM-DD format as query param
        end_date: End date in YYYY-MM-DD format as query param
        persist: Whether to persist data to insert service

    Returns:
        JSONResponse containing:
            - date_range: Start and end dates
            - accounts: Account hierarchy information
            - reports: Campaign/ad performance data

    Example:
        POST /google/reports?start_date=2025-04-16&end_date=2025-04-23
        Body: {"refresh_token": "..."}

    Raises:
        HTTPException: If dates are invalid or API errors occur
    """
    try:
        # Validate date formats
        try:
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                if start_dt > end_dt:
                    raise HTTPException(
                        status_code=400,
                        detail="start_date cannot be later than end_date",
                    )
            else:
                start_date = datetime.now().date().strftime("%Y-%m-%d")
                end_date = start_date
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Initialize client
        ga_client = await get_google_ads_client(credentials)
        logging.info(f"Fetching reports from {start_date} to {end_date}")

        # Get account hierarchies
        hierarchies = await get_all_account_hierarchies(ga_client)
        customer_ads_accounts = get_non_manager_accounts(hierarchies)

        # Get report data
        ad_reports = await get_reports(
            ga_client, start_date, end_date, customer_ads_accounts
        )

        if persist:
            # Process and send reports to insert service
            index_name = "a_quang_nguyen_google_ad_report"
            insert_response = await post_processing(ad_reports, index_name)
            logging.info(
                "Sending to Insert service. Response: %s",
                insert_response,
            )

        # Build response with hierarchy information
        response_data = {
            "date_range": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "account": {
                "hierarchy": hierarchies,
                "customer_ads_accounts": customer_ads_accounts,
            },
            "report": {
                "total_campaigns": len(set(r["campaign"]["id"] for r in ad_reports)),
                "total_ad_groups": len(set(r["ad_group"]["id"] for r in ad_reports)),
                "total_ads": len(set(r["ad_group_ad"]["ad_id"] for r in ad_reports)),
                "total_reports": len(ad_reports),
                "reports": ad_reports,
            },
        }

        logging.info(f"Returning {len(ad_reports)} reports")

        return JSONResponse(content=response_data, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching Google Ads reports: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
