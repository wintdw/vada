import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta

from handler.shop_apis import get_authorized_shop
from handler.order_apis import get_order_list, get_order_detail
from handler.persist import post_processing


async def fetch_detailed_orders(
    access_token: str,
    start_date: str = "",
    end_date: str = "",
    index_name: str = "",
    vada_uid: str = "",
    account_name: str = "",
) -> List[Dict]:
    shop_info = await get_authorized_shop(access_token)
    logging.info("Shop Info: %s", json.dumps(shop_info, indent=2))

    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        end_date = datetime.now().date().strftime("%Y-%m-%d")

    # Convert start_date and end_date to Unix timestamps
    create_time_from = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    create_time_to = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    logging.info(
        "Fetching orders from %s to %s for shop ID: %s",
        start_date,
        end_date,
        shop_info["id"],
    )
    orders = await get_order_list(
        access_token=access_token,
        shop_id=shop_info["id"],
        create_time_from=create_time_from,
        create_time_to=create_time_to,
    )
    logging.info(
        "Orders: %s, Length: %d", json.dumps(orders, indent=2), len(orders["orders"])
    )

    # Fetch order details for all orders
    order_id_list = [order["order_id"] for order in orders["orders"]]
    if not order_id_list:
        logging.info("No orders found for the specified date range.")
        return []

    order_details = await get_order_detail(
        access_token=access_token,
        shop_id=shop_info["id"],
        order_id_list=order_id_list,
    )
    logging.info("Sample order details: %s", order_details[:1])

    insert_response = await post_processing(order_details, index_name)
    logging.info("Insert response: %s", insert_response)

    return order_details
