import json
import logging
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta

from handler.mysql import update_crawl_time
from handler.shop_apis import get_authorized_shop
from handler.order_apis import get_order_list
from handler.persist import post_processing


async def crawl_new_client(
    crawl_id: str,
    access_token: str,
    index_name: str,
    crawl_interval: int,
):
    """Split the first 1-year crawl into jobs, each handling 30 days (backward from now)."""
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

        await scheduled_fetch_all_orders(
            crawl_id=crawl_id,
            access_token=access_token,
            index_name=index_name,
            crawl_interval=crawl_interval,
            start_date=start_date,
            end_date=end_date,
        )


async def scheduled_fetch_all_orders(
    crawl_id: str,
    access_token: str,
    index_name: str,
    crawl_interval: int,
    start_date: str = "",
    end_date: str = "",
) -> List[Dict]:
    shop_info = await get_authorized_shop(access_token)
    logging.info("Shop Info: %s", json.dumps(shop_info, indent=2))

    # Default to yesterday → tomorrow if dates not provided
    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).date().strftime("%Y-%m-%d")

    create_time_ge = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    create_time_lt = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    all_orders = []

    async def fetch_orders_range(start_ts: int, end_ts: int) -> None:
        nonlocal all_orders

        # retry 10 times, for 30s
        MAX_RETRIES = 10
        RETRY_DELAY = 30

        logging.info(
            "Fetching orders from %s to %s for shop ID: %s",
            datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S"),
            datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S"),
            shop_info["id"],
        )

        response = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await get_order_list(
                    access_token=access_token,
                    shop_cipher=shop_info["cipher"],
                    create_time_ge=start_ts,
                    create_time_lt=end_ts,
                )
                logging.debug(response)
                break  # Success
            except Exception as e:
                logging.warning(
                    f"[Attempt {attempt}] Failed to fetch orders: {str(e)}",
                    exc_info=True,
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logging.error("Max retries exceeded while fetching orders")
                    return  # Abort this range

        if not response:
            return  # Sanity check, in case response is still None

        total = response.get("total", 0)
        logging.info(f"Got {total} orders for range {start_ts} → {end_ts}")

        if total == 5000:
            # Split range in half to avoid truncation
            mid_ts = (start_ts + end_ts) // 2
            await fetch_orders_range(start_ts, mid_ts)
            await fetch_orders_range(mid_ts, end_ts)
        else:
            orders = response.get("orders", [])
            if orders:
                insert_response = await post_processing(orders, index_name)
                logging.info("Insert response: %s", insert_response)
                all_orders.extend(orders)
            else:
                logging.info("No orders found in this sub-range")

    # Fetch with auto-splitting and retry logic
    await fetch_orders_range(create_time_ge, create_time_lt)

    await update_crawl_time(crawl_id=crawl_id, crawl_interval=crawl_interval)

    return all_orders
