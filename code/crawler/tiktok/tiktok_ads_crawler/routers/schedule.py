from fastapi import APIRouter  # type: ignore
from datetime import datetime, timedelta
from prometheus_client import Counter  # type: ignore
import asyncio

from tools import get_logger
from models import CrawlHistory, CrawlInfoResponse

router = APIRouter()
logger = get_logger(__name__, 10)

tiktok_ad_crawl = Counter(
    "tiktok_ad_crawl",
    "Total number of crawls",
    ["account_name", "vada_uid"],
)
tiktok_ad_crawl_success = Counter(
    "tiktok_ad_crawl_success",
    "Total number of successful crawls",
    ["account_name", "vada_uid"],
)


@router.post(
    "/v1/schedule/{crawl_id}/crawl", response_model=CrawlInfoResponse, tags=["Schedule"]
)
async def post_schedule_crawl(crawl_id: str = ""):
    from repositories import (
        select_crawl_info_by_next_crawl_time,
        update_crawl_info,
        insert_crawl_history,
        update_crawl_history,
    )
    from handlers.tiktok import crawl_tiktok_business

    async def crawl_one(item):
        history_id = None
        try:
            crawl_history = await insert_crawl_history(
                CrawlHistory(crawl_id=item.crawl_id)
            )
            logger.info(crawl_history)
            history_id = crawl_history.history_id

            tiktok_ad_crawl.labels(
                account_name=item.account_name, vada_uid=item.vada_uid
            ).inc()

            if not item.last_crawl_time:
                # Crawl 1 year of data, split into 7-day chunks, run at most 3 at once
                start_date = datetime.now() - timedelta(days=365)
                end_date = datetime.now()
                chunk = timedelta(days=7)
                current_start = start_date

                semaphore = asyncio.Semaphore(3)
                chunk_tasks = []

                async def chunk_crawl(start, end):
                    async with semaphore:
                        crawl_response = await crawl_tiktok_business(
                            item.index_name,
                            item.access_token,
                            start.strftime("%Y-%m-%d"),
                            end.strftime("%Y-%m-%d"),
                        )
                        logger.info(
                            f"Crawled from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}: {crawl_response}"
                        )
                        return crawl_response

                while current_start < end_date:
                    current_end = min(current_start + chunk, end_date)
                    chunk_tasks.append(
                        asyncio.create_task(chunk_crawl(current_start, current_end))
                    )
                    current_start = current_end

                chunk_results = await asyncio.gather(
                    *chunk_tasks, return_exceptions=True
                )
                for idx, result in enumerate(chunk_results):
                    if isinstance(result, Exception):
                        logger.error(f"Chunk {idx} failed: {result}")
                    else:
                        logger.info(f"Chunk {idx} result: {result}")
            else:
                crawl_response = await crawl_tiktok_business(
                    item.index_name,
                    item.access_token,
                    (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                )
                logger.info(crawl_response)

            tiktok_ad_crawl_success.labels(
                account_name=item.account_name, vada_uid=item.vada_uid
            ).inc()

            item.last_crawl_time = item.next_crawl_time
            item.next_crawl_time = item.next_crawl_time + timedelta(
                minutes=item.crawl_interval
            )

            crawl_info = await update_crawl_info(item.crawl_id, item)
            logger.info(crawl_info)

            crawl_history = await update_crawl_history(
                history_id,
                CrawlHistory(
                    crawl_id=item.crawl_id,
                    crawl_status="success",
                    crawl_duration=int(crawl_response.get("execution_time")),
                    crawl_data_number=crawl_response.get("total_reports"),
                ),
            )
            logger.info(crawl_history)
        except Exception as e:
            await update_crawl_history(
                history_id,
                CrawlHistory(
                    crawl_id=item.crawl_id, crawl_status="failed", crawl_error=str(e)
                ),
            )
            logger.error(f"Crawl failed for {item.crawl_id}: {e}")

    try:
        crawl_info = await select_crawl_info_by_next_crawl_time()
        tasks = [asyncio.create_task(crawl_one(item)) for item in crawl_info]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in post_schedule_crawl: {e}")
    finally:
        return CrawlInfoResponse(status=200, message="Success")


@router.post(
    "/v1/schedule/{crawl_id}/auth", response_model=CrawlInfoResponse, tags=["Schedule"]
)
async def post_schedule_auth(crawl_id: str = ""):
    pass
