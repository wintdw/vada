from fastapi import APIRouter, Query, HTTPException  # type: ignore
import logging

from scheduler.order_processing import scheduled_fetch_all_orders
from handler.mysql import get_crawl_info

router = APIRouter()


@router.get("/ingest/partner/tiktok/shop/crawl")
async def manual_crawl(
    crawl_id: str = Query(..., description="Unique crawl ID to look up crawl info"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD"),
):
    """
    Manually trigger a crawl using crawl_id and a date range.
    """
    try:
        # Fetch token, index_name, etc. from your DB based on crawl_id
        crawl_info = await get_crawl_info(crawl_id=crawl_id)
        if not crawl_info:
            raise HTTPException(
                status_code=404, detail=f"crawl_id '{crawl_id}' not found"
            )

        access_token = crawl_info[0]["access_token"]
        index_name = crawl_info[0]["index_name"]
        crawl_interval = crawl_info[0]["crawl_interval"]

        orders = await scheduled_fetch_all_orders(
            crawl_id=crawl_id,
            access_token=access_token,
            index_name=index_name,
            crawl_interval=crawl_interval,
            start_date=start_date,
            end_date=end_date,
        )
        return {"crawl_id": crawl_id, "orders_fetched": len(orders)}

    except Exception as e:
        logging.error(f"Failed manual crawl for {crawl_id}: {e}", exc_info=True)
        return {"error": str(e)}
