from datetime import datetime, timedelta

from tools.logger import get_logger
from handlers.tiktok import crawl_tiktok_business
from repositories.crawl_info import update_crawl_time

logger = get_logger(__name__)


async def crawl_first_tiktok_ad(
    crawl_id: str, access_token: str, index_name: str, crawl_interval: int
):
    # Crawl 1 year of data, split into 30-day chunks (from latest to oldest)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    chunk = timedelta(days=30)
    current_end = end_date

    while current_end > start_date:
        current_start = max(current_end - chunk, start_date)

        crawl_response = await crawl_tiktok_business(
            index_name,
            access_token,
            current_start.strftime("%Y-%m-%d"),
            current_end.strftime("%Y-%m-%d"),
        )
        logger.info(
            f"[First Crawl] CrawlID {crawl_id} from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}: {crawl_response}"
        )

        current_end = current_start  # move backward

    await update_crawl_time(crawl_id, crawl_interval)


async def crawl_daily_tiktok_ad(
    crawl_id: str, access_token: str, index_name: str, crawl_interval: int
):
    start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    crawl_response = await crawl_tiktok_business(
        index_name,
        access_token,
        start_date,
        end_date,
    )
    logger.info(
        f"[Daily Crawl] CrawlID {crawl_id} from {start_date} to {end_date}: {crawl_response}"
    )

    await update_crawl_time(crawl_id, crawl_interval)
