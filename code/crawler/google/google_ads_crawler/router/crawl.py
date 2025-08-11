import logging
from fastapi import APIRouter, HTTPException, Query  # type: ignore

from scheduler.crawl import crawl_daily
from handler.mysql import get_crawl_info

router = APIRouter()


@router.get("/ingest/partner/google/ad/crawl")
async def manual_google_ad_crawl(
    crawl_id: str = Query(..., description="Unique crawl ID to look up crawl info"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
):
    """
    Manually trigger a Google Ads crawl using crawl_id and a date range.
    """
    try:
        crawl_info = await get_crawl_info(crawl_id=crawl_id)
        if not crawl_info:
            raise HTTPException(
                status_code=404, detail=f"crawl_id '{crawl_id}' not found"
            )

        crawl_resp = await crawl_daily(
            crawl_id=crawl_id,
            start_date=start_date,
            end_date=end_date,
        )
        return {"crawl_id": crawl_id, "detail": crawl_resp}

    except Exception as e:
        logging.error(f"Failed manual crawl for {crawl_id}: {e}", exc_info=True)
        return {"error": str(e)}
