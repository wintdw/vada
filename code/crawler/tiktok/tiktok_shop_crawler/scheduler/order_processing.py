import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta

from handler.shop_apis import get_authorized_shop
from handler.order_apis import get_order_list
from handler.persist import post_processing


async def scheduled_fetch_all_orders(
    access_token: str,
    start_date: str = "",
    end_date: str = "",
    index_name: str = "",
    vada_uid: str = "",
    account_name: str = "",
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
    logging.info(order_reponse)

    orders = order_reponse.get("orders", [])

    # Fetch order details for all orders
    if not orders:
        logging.info("No orders found for the specified date range.")
        return []

    insert_response = await post_processing(orders, index_name)
    logging.info("Insert response: %s", insert_response)

    return orders
