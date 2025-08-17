import logging
from datetime import datetime, timedelta
from typing import Dict

from model.settings import settings
from handler.pancake_pos import crawl_pancake_pos_data
from handler.persist import post_processing
from handler.crawl_info import update_crawl_time, get_crawl_info
from handler.metrics import insert_success_counter, insert_failure_counter


async def crawl_first_pancake_pos(crawl_id: str):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    chunk = timedelta(days=2)
    current_end = end_date

    logging.info(
        f"[{crawl_id}] [First Crawl] Crawling from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    )

    while current_end > start_date:
        current_start = max(current_end - chunk, start_date)

        # Use crawl_daily_pancake_pos for each chunk
        await crawl_daily_pancake_pos(
            crawl_id=crawl_id,
            start_date=current_start.strftime("%Y-%m-%d"),
            end_date=current_end.strftime("%Y-%m-%d"),
        )

        current_end = current_start  # move backward


async def crawl_daily_pancake_pos(
    crawl_id: str, start_date: str = "", end_date: str = ""
) -> Dict:
    """
    start_date and end_date are for manual crawl only
    """
    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return {}

    index_name = crawl_info[0]["index_name"]
    api_key = crawl_info[0]["api_key"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    crawl_response = await crawl_pancake_pos_data(
        api_key=api_key,
        from_date=start_date,
        to_date=end_date,
    )

    # Send to the datastore
    insert_response = await post_processing(
        crawl_response.get("orders", []),
        index_name,
    )

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
    crawl_response.pop("orders", None)

    logging.info(
        f"[{api_key}] [Daily Crawl] Result from {start_date} to {end_date}: {crawl_response}"
    )

    return crawl_response


async def crawl_daily_pancake_pos_scheduler(crawl_id: str):
    """
    This will call crawl_daily_pancake_pos if the time condition is met
    """
    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return

    api_key = crawl_info[0]["api_key"]

    next_crawl_time = datetime.fromisoformat(crawl_info[0]["next_crawl_time"])
    now = datetime.now()

    # If not yet time for next crawl, skip
    if now < next_crawl_time:
        logging.debug(
            f"[{api_key}] [Daily Crawl Scheduler] CrawlID {crawl_id}: skip (now={now}, next={next_crawl_time})"
        )
        return

    crawl_response = await crawl_daily_pancake_pos(crawl_id)
    logging.info(
        f"[{api_key}] [Daily Crawl Scheduler] Finish crawling with ID {crawl_id}"
    )
