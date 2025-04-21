from fastapi import APIRouter, HTTPException
from aiomysql import IntegrityError
from datetime import timedelta

from tools import get_logger
from models import CrawlHistory, CrawlInfo, CrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 20)

@router.post("/v1/schedule/{crawl_id}/crawl", response_model=CrawlInfoResponse, tags=["Schedule"])
async def post_schedule_crawl(crawl_id: str = None):
    from repositories import select_crawl_info_by_next_crawl_time, update_crawl_info, insert_crawl_history, update_crawl_history
    from routers.tiktok import tiktok_business_get

    try:
        crawl_info = await select_crawl_info_by_next_crawl_time()
        crawl_id = None
        for item in crawl_info:
            crawl_id = item.crawl_id
            crawl_history = await insert_crawl_history(CrawlHistory(crawl_id=crawl_id))
            logger.info(crawl_history)

            crawl_response = await tiktok_business_get(item.index_name, item.access_token, item.next_crawl_time.strftime('%Y-%m-%d'), item.next_crawl_time.strftime('%Y-%m-%d'))
            logger.info(crawl_response)

            item.last_crawl_time = item.next_crawl_time
            item.next_crawl_time = item.last_crawl_time + timedelta(minutes=item.crawl_interval)
            crawl_info = await update_crawl_info(crawl_id, item)
            logger.info(crawl_info)
            
            crawl_history = await update_crawl_history(crawl_id, CrawlHistory(
                crawl_id=crawl_id,
                crawl_status="success",
                crawl_duration=crawl_response.get("execution_time"),
                crawl_data_number=crawl_response.get("total_reports")
            ))
            logger.info(crawl_history)

    except Exception as e:
        crawl_history = await update_crawl_history(crawl_id, CrawlHistory(
            crawl_id=crawl_id,
            crawl_status="failed",
            crawl_error=e
        ))
        logger.info(crawl_history)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    logger.info(crawl_info)
    return CrawlInfoResponse(
        status=200,
        message="Success"
    )

@router.post("/v1/schedule/{crawl_id}/auth", response_model=CrawlInfoResponse, tags=["Schedule"])
async def post_schedule_auth(crawl_id: str = None):
    pass
