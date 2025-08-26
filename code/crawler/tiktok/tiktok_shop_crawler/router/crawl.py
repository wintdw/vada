import logging
from fastapi import APIRouter, Query, HTTPException  # type: ignore

from scheduler.crawl import crawl_daily_tiktokshop
from handler.crawl_info import get_crawl_info

router = APIRouter()


@router.get("/ingest/partner/tiktok/shop/crawl")
async def manual_crawl(
    crawl_id: str = Query(..., description="Unique crawl ID to look up crawl info"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
    crawl_type: str = Query(
        "all", description="Crawl type: 'all', 'order', or 'finance'"
    ),
):
    try:
        # Fetch token, index_name, etc. from your DB based on crawl_id
        crawl_info = await get_crawl_info(crawl_id=crawl_id)
        if not crawl_info:
            raise HTTPException(
                status_code=404, detail=f"crawl_id '{crawl_id}' not found"
            )

        crawl_resp = await crawl_daily_tiktokshop(
            crawl_id=crawl_id,
            start_date=start_date,
            end_date=end_date,
            crawl_type=crawl_type,
            manual=True,
        )
        return {"crawl_id": crawl_id, "detail": crawl_resp}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed manual crawl for {crawl_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
