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
    ["index_name", "business_id"],
)
nhanh_platform_crawl_success = Counter(
    "nhanh_platform_crawl_success",
    "Total number of successful crawls",
    ["index_name", "business_id"],
)

@router.post("/v1/schedule/{index_name}/crawl", response_model=NhanhCrawlInfoResponse, tags=["Schedule"])
async def post_schedule_crawl(index_name: str = None):
    from repositories import select_crawl_info_by_next_crawl_time, update_crawl_info, insert_crawl_history, update_crawl_history
    from services.nhanh import crawl_nhanh_data

    try:
        crawl_info = await select_crawl_info_by_next_crawl_time()
        history_id = None

        for item in crawl_info:
            crawl_history = await insert_crawl_history(NhanhCrawlHistory(business_id=item.business_id))
            logger.info(crawl_history)

            history_id = crawl_history.history_id
            
            nhanh_platform_crawl.labels(index_name=item.index_name, business_id=item.business_id).inc()

            if not item.last_crawl_time:
                # First crawl - get last 360 days of data
                date_ranges = [
                    (0, 10),
                    (11, 20),
                    (21, 30),
                    (31, 40),
                    (41, 50),
                    (51, 60),
                    (61, 70),
                    (71, 80),
                    (81, 90),
                    (91, 100),
                    (101, 110),
                    (111, 120),
                    (121, 130),
                    (131, 140),
                    (141, 150),
                    (151, 160),
                    (161, 170),
                    (171, 180),
                    (181, 190),
                    (191, 200),
                    (201, 210),
                    (211, 220),
                    (221, 230),
                    (231, 240),
                    (241, 250),
                    (251, 260),
                    (261, 270),
                    (271, 280),
                    (281, 290),
                    (291, 300),
                    (301, 310),
                    (311, 320),
                    (321, 330),
                    (331, 340),
                    (341, 350),
                    (351, 360)
                ]

                for start_offset, end_offset in date_ranges:
                    crawl_response = await crawl_nhanh_data(
                        item.index_name,
                        item.business_id,
                        item.access_token,
                        (datetime.now() - timedelta(days=end_offset)).strftime('%Y-%m-%d'),
                        (datetime.now() - timedelta(days=start_offset)).strftime('%Y-%m-%d')
                    )
                    logger.info(crawl_response)
            else:   
                # Subsequent crawls - get last 0 days of data
                crawl_response = await crawl_nhanh_data(
                    item.index_name,
                    item.business_id,
                    item.access_token, 
                    (datetime.now() - timedelta(days=0)).strftime('%Y-%m-%d'), 
                    datetime.now().strftime('%Y-%m-%d')
                )
                logger.info(crawl_response)

            nhanh_platform_crawl_success.labels(index_name=item.index_name, business_id=item.business_id).inc()

            item.last_crawl_time = item.next_crawl_time
            item.next_crawl_time = item.next_crawl_time + timedelta(minutes=item.crawl_interval)

            crawl_info = await update_crawl_info(item.business_id, item)
            logger.info(crawl_info)

            crawl_history = await update_crawl_history(history_id, NhanhCrawlHistory(
                business_id=item.business_id,
                crawl_status="success",
                crawl_duration=int(crawl_response.get("execution_time")),
                crawl_data_number=crawl_response.get("total_reports")
            ))
            logger.info(crawl_history)

    except Exception as e:
        logger.error(f"Error during crawl: {e}")
        crawl_history = await update_crawl_history(history_id, NhanhCrawlHistory(
            business_id=item.business_id,
            crawl_status="failed",
            crawl_error=str(e)
        ))
        logger.error(crawl_history)

    finally:
        return NhanhCrawlInfoResponse(
            status=200,
            message="Success"
        )