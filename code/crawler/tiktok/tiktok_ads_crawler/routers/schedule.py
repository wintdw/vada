from fastapi import APIRouter
from datetime import timedelta
from prometheus_client import Gauge

from tools import get_logger
from models import CrawlHistory, CrawlInfo, CrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 20)

active_crawl_jobs_gauge = Gauge("active_crawl_jobs", "Number of active jobs")

@router.get("/v1/schedule")
async def update_metrics():
    from repositories import select_crawl_history_by_crawl_status

    try:
        crawl_history = await select_crawl_history_by_crawl_status("in_progress")
        active_crawl_jobs_gauge.set(len(crawl_history))
        logger.info(f"Metrics updated")
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")

@router.post("/v1/schedule/{crawl_id}/crawl", response_model=CrawlInfoResponse, tags=["Schedule"])
async def post_schedule_crawl(crawl_id: str = None):
    from repositories import select_crawl_info_by_next_crawl_time, update_crawl_info, insert_crawl_history, update_crawl_history
    from routers.tiktok import tiktok_business_get

    try:
        crawl_info = await select_crawl_info_by_next_crawl_time()
        history_id = None

        for item in crawl_info:
            crawl_history = await insert_crawl_history(CrawlHistory(crawl_id=item.crawl_id, crawl_from_date=item.last_crawl_time, crawl_to_date=item.next_crawl_time))
            logger.info(crawl_history)

            history_id = crawl_history.history_id

            crawl_response = await tiktok_business_get(item.index_name, item.access_token, item.last_crawl_time.strftime('%Y-%m-%d'), item.next_crawl_time.strftime('%Y-%m-%d'))
            logger.info(crawl_response)

            item.last_crawl_time = item.next_crawl_time
            item.next_crawl_time = item.last_crawl_time + timedelta(minutes=item.crawl_interval)
            crawl_info = await update_crawl_info(item.crawl_id, item)
            logger.info(crawl_info)
            
            crawl_history = await update_crawl_history(history_id, CrawlHistory(
                crawl_id=item.crawl_id,
                crawl_status="success",
                crawl_duration=int(crawl_response.get("execution_time")),
                crawl_data_number=crawl_response.get("total_reports")
            ))
            logger.info(crawl_history)

    except Exception as e:
        crawl_history = await update_crawl_history(history_id, CrawlHistory(
            crawl_id=crawl_id,
            crawl_status="failed",
            crawl_error=str(e)
        ))
        logger.error(crawl_history)

    finally:
        return CrawlInfoResponse(
            status=200,
            message="Success"
        )

@router.post("/v1/schedule/{crawl_id}/auth", response_model=CrawlInfoResponse, tags=["Schedule"])
async def post_schedule_auth(crawl_id: str = None):
    pass
