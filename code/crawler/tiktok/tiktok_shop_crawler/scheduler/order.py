import logging
from typing import Dict
from datetime import datetime, timedelta

from model.setting import settings
from handler.crawl_info import update_crawl_time, get_crawl_info
from handler.main import get_orders
from handler.persist import post_processing
from handler.metrics import insert_success_gauge, insert_failure_gauge


async def crawl_first_tiktokshop(crawl_id: str):
    """Split the first 1-year crawl into jobs (backward from now)"""
    now = datetime.now()
    days_in_year = 365
    window = 1
    num_jobs = days_in_year // window + (1 if days_in_year % window else 0)

    for i in range(num_jobs):
        start_offset = i * window
        end_offset = (i + 1) * window

        # Latest to earliest: subtract offsets from now
        start_date = (now - timedelta(days=end_offset)).strftime("%Y-%m-%d")
        if i == 0:
            end_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")  # up to tomorrow
        else:
            end_date = (now - timedelta(days=start_offset)).strftime("%Y-%m-%d")

        await crawl_daily_tiktokshop(
            crawl_id=crawl_id, start_date=start_date, end_date=end_date
        )


async def crawl_daily_tiktokshop(
    crawl_id: str, start_date: str = "", end_date: str = ""
) -> Dict:
    """
    start_date and end_date are for manual crawl only
    """
    if not start_date or not end_date:
        # today -> tmr: this will crawl today only
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return {}

    index_name = crawl_info[0]["index_name"]
    account_name = crawl_info[0]["account_name"]
    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    logging.info(
        f"[{account_name}] [Daily Crawl] Crawling from {start_date} to {end_date}"
    )

    crawl_response = await get_orders(
        access_token=access_token, start_date=start_date, end_date=end_date
    )

    # Send to the datastore
    insert_response = await post_processing(
        crawl_response.get("orders", []),
        index_name,
    )

    # Update Prometheus metrics for insert success/failure
    insert_success_gauge.labels(
        crawl_id=crawl_id,
        index_name=index_name,
        app_env=settings.APP_ENV,
    ).set(insert_response.get("success", 0))
    insert_failure_gauge.labels(
        crawl_id=crawl_id,
        index_name=index_name,
        app_env=settings.APP_ENV,
    ).set(insert_response.get("failure", 0))

    await update_crawl_time(crawl_id, crawl_interval)
    crawl_response.pop("orders", None)

    logging.info(
        f"[{account_name}] [Daily Crawl] Result from {start_date} to {end_date}: {crawl_response}"
    )

    return crawl_response


async def crawl_daily_tiktokshop_scheduler(crawl_id: str):
    """
    This will call crawl_daily_tiktokshop if the time condition is met
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

    crawl_response = await crawl_daily_tiktokshop(crawl_id)
    logging.info(
        f"[{account_name}] [Daily Crawl Scheduler] Finish crawl ID {crawl_id}: {crawl_response}"
    )
