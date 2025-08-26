import logging
from typing import Dict
from datetime import datetime, timedelta

from model.setting import settings
from handler.crawl_info import update_crawl_time, get_crawl_info
from handler.main import get_tiktokshop
from handler.persist import post_processing
from handler.metrics import insert_success_counter, insert_failure_counter


async def crawl_first_tiktokshop(crawl_id: str):
    """Split the first 1-year crawl into jobs (backward from now)"""
    now = datetime.now()
    days_in_year = 90
    window = 1
    num_jobs = days_in_year // window + (1 if days_in_year % window else 0)

    logging.info(
        f"[First Crawl] Crawling {days_in_year}d backward from {now.strftime('%Y-%m-%d')}"
    )
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
    crawl_id: str,
    start_date: str = "",
    end_date: str = "",
    crawl_type: str = "all",
    manual: bool = False,
) -> Dict:
    """
    start_date and end_date are for manual crawl only.
    For daily run, crawl the last 8 hours using timestamps.

    crawl_type: "all" | "order" | "finance"
      - all: fetch and persist both orders and statements (default)
      - order: fetch orders only and persist orders
      - finance: fetch statements only and persist statements
    """
    if not start_date or not end_date:
        # Crawl the last 8 hours
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(hours=8)
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        start_date = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        end_date = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # Convert date strings to timestamps (date-only expected)
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    crawl_info = await get_crawl_info(crawl_id=crawl_id)
    if not crawl_info:
        logging.error(f"Wrong crawl ID: {crawl_id}")
        return {}

    account_id = crawl_info[0]["account_id"]
    order_index_name = f"data_tiktokshop_{account_id}"
    finance_index_name = f"data_tiktokshop_finance_{account_id}"
    account_name = crawl_info[0]["account_name"]
    access_token = crawl_info[0]["access_token"]
    crawl_interval = crawl_info[0]["crawl_interval"]

    crawl_response = await get_tiktokshop(
        access_token=access_token,
        start_ts=start_ts,
        end_ts=end_ts,
        crawl_type=crawl_type,
    )

    # Send orders to the datastore
    order_insert_response = await post_processing(
        crawl_response.get("orders", []), order_index_name, "order"
    )
    finance_insert_response = await post_processing(
        crawl_response.get("statements", []), finance_index_name, "finance"
    )

    # Update Prometheus metrics for insert success/failure for both order and finance
    total_success = order_insert_response.get(
        "success", 0
    ) + finance_insert_response.get("success", 0)
    total_failure = order_insert_response.get(
        "failure", 0
    ) + finance_insert_response.get("failure", 0)

    insert_success_counter.labels(
        crawl_id=crawl_id,
        app_env=settings.APP_ENV,
    ).inc(total_success)
    insert_failure_counter.labels(
        crawl_id=crawl_id,
        app_env=settings.APP_ENV,
    ).inc(total_failure)

    # Do not update auto crawl time if manual crawl
    if not manual:
        await update_crawl_time(crawl_id, crawl_interval)

    crawl_response.pop("orders", None)
    crawl_response.pop("statements", None)

    logging.info(
        f"[{account_name}] [Daily Crawl] Result from {start_date} to {end_date}: {crawl_response}"
    )

    return crawl_response
