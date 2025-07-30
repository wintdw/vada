import json
import logging
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
    window = 14
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

    # end_date shoud be the next day
    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).date().strftime("%Y-%m-%d")

    # Convert start_date and end_date to Unix timestamps
    create_time_ge = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    create_time_lt = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    logging.info(
        "Fetching orders from %s to %s for shop ID: %s",
        start_date,
        end_date,
        shop_info["id"],
    )
    order_reponse = await get_order_list(
        access_token=access_token,
        shop_cipher=shop_info["cipher"],
        create_time_ge=create_time_ge,
        create_time_lt=create_time_lt,
    )
    logging.debug(order_reponse)
    logging.info(f"Got {order_reponse.get('total', 0)} orders")

    orders = order_reponse.get("orders", [])

    # Fetch order details for all orders
    if not orders:
        logging.info("No orders found for the specified date range")
        return []

    insert_response = await post_processing(orders, index_name)
    logging.info("Insert response: %s", insert_response)

    await update_crawl_time(crawl_id=crawl_id, crawl_interval=crawl_interval)

    return orders
