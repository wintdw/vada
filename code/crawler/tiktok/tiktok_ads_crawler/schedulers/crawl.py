from datetime import datetime, timedelta

from tools.logger import get_logger
from handlers.tiktok import crawl_tiktok_business
from repositories.crawl_info import update_crawl_time

logger = get_logger(__name__)


async def crawl_first_tiktok_ad(
    crawl_id: str, access_token: str, index_name: str, crawl_interval: int
):
    # Crawl 1 year of data, split into 30-day chunks
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    chunk = timedelta(days=30)
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + chunk, end_date)
        crawl_response = await crawl_tiktok_business(
            index_name,
            access_token,
            current_start.strftime("%Y-%m-%d"),
            current_end.strftime("%Y-%m-%d"),
        )
        current_start = current_end
        logger.info(
            f"[First Crawl] CrawlID {crawl_id} from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}: {crawl_response}"
        )

    await update_crawl_time(crawl_id, crawl_interval)


async def crawl_daily_tiktok_ad(
    crawl_id: str, access_token: str, index_name: str, crawl_interval: int
):
    crawl_response = await crawl_tiktok_business(
        index_name,
        access_token,
        (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d"),
    )
    logger.info(
        f"[Daily Crawl] CrawlID {crawl_id} from {(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}: {crawl_response}"
    )

    await update_crawl_time(crawl_id, crawl_interval)
