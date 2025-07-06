from fastapi import APIRouter
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram  # type: ignore

from tools import get_logger
from models import NhanhCrawlHistory, NhanhCrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 20)

nhanh_platform_crawl = Counter(
    "nhanh_platform_crawl",
    "Total number of crawls",
    ["account_name", "vada_uid"],
)
nhanh_platform_crawl_success = Counter(
    "nhanh_platform_crawl_success",
    "Total number of successful crawls",
    ["account_name", "vada_uid"],
)

@router.post("/v1/schedule/{crawl_id}/crawl", response_model=NhanhCrawlInfoResponse, tags=["Schedule"])
async def post_schedule_crawl(crawl_id: str = None):
    from repositories import select_crawl_info_by_next_crawl_time, update_crawl_info, insert_crawl_history, update_crawl_history
    from services.nhanh import crawl_nhanh_data

    try:
        crawl_info = await select_crawl_info_by_next_crawl_time()
        history_id = None

        for item in crawl_info:
            crawl_history = await insert_crawl_history(NhanhCrawlHistory(crawl_id=item.crawl_id))
            logger.info(crawl_history)

            history_id = crawl_history.history_id
            
            nhanh_platform_crawl.labels(account_name=item.account_name, vada_uid=item.vada_uid).inc()

            if not item.last_crawl_time:
                # First crawl - get last 30 days of data
                crawl_response = await crawl_nhanh_data(
                    item.access_token, 
                    (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'), 
                    datetime.now().strftime('%Y-%m-%d')
                )
                logger.info(crawl_response)
            else:
                # Subsequent crawls - get last 2 days of data
                crawl_response = await crawl_nhanh_data(
                    item.access_token, 
                    (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 
                    datetime.now().strftime('%Y-%m-%d')
                )
                logger.info(crawl_response)

            nhanh_platform_crawl_success.labels(account_name=item.account_name, vada_uid=item.vada_uid).inc()

            item.last_crawl_time = item.next_crawl_time
            item.next_crawl_time = item.next_crawl_time + timedelta(minutes=item.crawl_interval)

            crawl_info = await update_crawl_info(item.crawl_id, item)
            logger.info(crawl_info)
            
            crawl_history = await update_crawl_history(history_id, NhanhCrawlHistory(
                crawl_id=item.crawl_id,
                crawl_status="success",
                crawl_duration=int(crawl_response.get("execution_time")),
                crawl_data_number=crawl_response.get("total_reports")
            ))
            logger.info(crawl_history)

    except Exception as e:
        crawl_history = await update_crawl_history(history_id, NhanhCrawlHistory(
            crawl_id=crawl_id,
            crawl_status="failed",
            crawl_error=str(e)
        ))
        logger.error(crawl_history)

    finally:
        return NhanhCrawlInfoResponse(
            status=200,
            message="Success"
        )

@router.post("/v1/schedule/{crawl_id}/auth", response_model=NhanhCrawlInfoResponse, tags=["Schedule"])
async def post_schedule_auth(crawl_id: str = None):
    pass
