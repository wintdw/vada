from fastapi import APIRouter
from datetime import timedelta

from tools import get_logger
from models import CrawlHistory, CrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.post("/v1/schedule/{crawl_id}/crawl", response_model=CrawlInfoResponse, tags=["Schedule"])
async def post_schedule_crawl(crawl_id: str = None):
    from repositories import select_crawl_info_by_next_crawl_time, update_crawl_info, insert_crawl_history, update_crawl_history
    from handlers.tiktok import crawl_tiktok_business

    try:
        crawl_info = await select_crawl_info_by_next_crawl_time()
        history_id = None

        for item in crawl_info:
            crawl_history = await insert_crawl_history(CrawlHistory(crawl_id=item.crawl_id, crawl_from_date=item.crawl_from_date, crawl_to_date=item.crawl_to_date))
            logger.info(crawl_history)

            history_id = crawl_history.history_id

            crawl_response = await crawl_tiktok_business(item.index_name, item.access_token, item.crawl_from_date.strftime('%Y-%m-%d'), item.crawl_to_date.strftime('%Y-%m-%d'))
            logger.info(crawl_response)

            item.crawl_from_date = item.crawl_to_date
            item.crawl_to_date = item.crawl_to_date + timedelta(minutes=item.crawl_interval)

            item.last_crawl_time = item.next_crawl_time
            item.next_crawl_time = item.next_crawl_time + timedelta(minutes=item.crawl_interval)

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
