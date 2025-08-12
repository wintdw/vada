import logging
from datetime import datetime, timedelta
from typing import Dict

from handler.tiktok import crawl_tiktok_business
from handler.persist import post_processing
from repository.crawl_info import update_crawl_time, get_crawl_info


async def crawl_first_tiktokad(crawl_id: str):
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    # Crawl 1 year of data, split into 30-day chunks (from latest to oldest)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    chunk = timedelta(days=30)
    current_end = end_date

    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]
    index_name = crawl_info[0]["index_name"]
    account_name = crawl_info[0]["account_name"]

    logging.info(
        f"[{account_name}] [First Crawl] Crawling from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    )

    while current_end > start_date:
        current_start = max(current_end - chunk, start_date)

        crawl_response = await crawl_tiktok_business(
            access_token,
            current_start.strftime("%Y-%m-%d"),
            current_end.strftime("%Y-%m-%d"),
        )
        await post_processing(crawl_response["report"]["reports"], index_name)

        logging.info(
            f"[{account_name}] [First Crawl] CrawlID {crawl_id} from {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}: {crawl_response['report']['total_reports']} reports"
        )

        current_end = current_start  # move backward

    await update_crawl_time(crawl_id, crawl_interval)


async def crawl_daily_tiktokad(
    crawl_id: str, start_date: str = "", end_date: str = ""
) -> Dict:
    """
    start_date and end_date are for manual crawl only
    """
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return {}

    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]
    index_name = crawl_info[0]["index_name"]
    account_name = crawl_info[0]["account_name"]

    logging.info(
        f"[{account_name}] [Daily Crawl] Crawling from {start_date} to {end_date}"
    )

    crawl_response = await crawl_tiktok_business(
        access_token,
        start_date,
        end_date,
    )
    await post_processing(crawl_response["report"]["reports"], index_name)
    await update_crawl_time(crawl_id, crawl_interval)

    # remove unnecessary fields from the response
    crawl_response["report"].pop("reports", None)
    logging.info(
        f"[{account_name}] [Daily Crawl] CrawlID {crawl_id} from {start_date} to {end_date}: {crawl_response}"
    )
    return crawl_response


async def crawl_daily_tiktokad_scheduler(crawl_id: str):
    """
    This will call crawl_daily_tiktokad if the time condition is met
    """
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    account_name = crawl_info[0]["account_name"]

    next_crawl_time = datetime.fromisoformat(crawl_info[0]["next_crawl_time"])
    now = datetime.now()

    # If not yet time for next crawl, skip
    if now < next_crawl_time:
        logging.debug(
            f"[{account_name}] [Daily Crawl Scheduler] CrawlID {crawl_id}: skip (now={now}, next={next_crawl_time})"
        )
        return

    await crawl_daily_tiktokad(crawl_id)
