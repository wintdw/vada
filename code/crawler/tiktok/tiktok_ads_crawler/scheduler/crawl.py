import logging
from datetime import datetime, timedelta
from typing import Dict

from model.setting import settings
from handler.ads import crawl_tiktok_business
from handler.persist import post_processing
from repository.crawl_info import update_crawl_time, get_crawl_info
from handler.metrics import insert_success_counter, insert_failure_counter


async def crawl_first_tiktokad(crawl_id: str):
    # Crawl 1 year of data, split into 30-day chunks (from latest to oldest)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    chunk = timedelta(days=30)
    current_end = end_date

    logging.info(
        f"[{crawl_id}] [First Crawl] Crawling from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    )

    while current_end > start_date:
        current_start = max(current_end - chunk, start_date)
        # Call crawl_daily_tiktokad for each chunk
        await crawl_daily_tiktokad(
            crawl_id,
            start_date=current_start.strftime("%Y-%m-%d"),
            end_date=current_end.strftime("%Y-%m-%d"),
        )
        current_end = current_start  # move backward


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
    # Get number of docs to insert
    reports = crawl_response["report"].get("reports", [])
    insert_response = await post_processing(reports, index_name)

    # Update Prometheus metrics for insert success/failure
    insert_success_counter.labels(
        crawl_id=crawl_id,
        app_env=settings.APP_ENV,
    ).inc(insert_response.get("success", 0))
    insert_failure_counter.labels(
        crawl_id=crawl_id,
        app_env=settings.APP_ENV,
    ).inc(insert_response.get("failure", 0))

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
