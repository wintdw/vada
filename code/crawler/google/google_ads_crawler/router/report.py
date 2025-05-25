import logging

from fastapi import APIRouter, HTTPException, Query, Request  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

from handler.report import fetch_google_reports


router = APIRouter()


@router.post("/google/reports")
async def fetch_google_reports_router(
    request: Request,
    start_date: str = Query(
        "", description="Start date in YYYY-MM-DD format", example="2025-04-30"
    ),
    end_date: str = Query(
        "", description="End date in YYYY-MM-DD format", example="2025-04-30"
    ),
    persist: bool = Query(False, description="Persist data to insert service"),
    index_name: str = Query(
        "", description="Index name for Elasticsearch", example="google_ads_reports"
    ),
    vada_uid: str = Query(
        "na", description="Vada UID for tracking", example="1234567890"
    ),
    account_email: str = Query(
        "na", description="Account email for tracking", example="abc@example.com"
    ),
):
    """Fetch Google Ads reports using provided credentials

    Args:
        refresh_token: refresh token for Google Ads API
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
    body = await request.json()
    refresh_token = body.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh_token")
    if persist and not index_name:
        raise HTTPException(
            status_code=400, detail="Index name is required when persist is True"
        )

    try:
        response_data = await fetch_google_reports(
            refresh_token=refresh_token,
            start_date=start_date,
            end_date=end_date,
            persist=persist,
            index_name=index_name,
            vada_uid=vada_uid,
            account_email=account_email,
        )

        return JSONResponse(content=response_data, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching Google Ads reports: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
