import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta

from handler.shop_apis import get_authorized_shop
from handler.order_apis import get_order_list, get_order_detail
from handler.persist import post_processing


async def scheduled_fetch_all_orders(
    access_token: str,
    start_date: str = "",
    end_date: str = "",
    index_name: str = "",
    vada_uid: str = "",
    account_id: int = 0,
    account_name: str = "",
) -> List[Dict]:
    shop_info = await get_authorized_shop(access_token, account_id)

    logging.info("Shop Info: %s", json.dumps(shop_info, indent=2))

    # Check if shop_info has error
    if "error" in shop_info and shop_info["error"] != "":
        logging.error(
            "Failed to get shop info: %s", shop_info.get("message", "Unknown error")
        )
        return  # Exit early if can't get shop info

    # end_date should be the next day
    if not start_date or not end_date:
        start_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).date().strftime("%Y-%m-%d")

    # Validate date range (Shopee API allows max 15 days)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    if start_dt >= end_dt:
        logging.error("Start date must be earlier than end date")
        return

    date_diff = (end_dt - start_dt).days
    if date_diff > 15:
        logging.warning(
            f"Date range is {date_diff} days, but Shopee API allows max 15 days. Adjusting end date."
        )
        end_date = (start_dt + timedelta(days=15)).strftime("%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Convert start_date and end_date to Unix timestamps
    create_time_ge = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    create_time_lt = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    # Use shop_name from shop_info or account_name as fallback
    shop_name = shop_info.get("shop_name", account_name)

    logging.info(
        "Fetching orders from %s to %s for shop ID: %s (%s)",
        start_date,
        end_date,
        shop_name,
        account_id,
    )

    order_response = await get_order_list(
        access_token=access_token,
        shop_id=account_id,
        create_time_from=create_time_ge,
        create_time_to=create_time_lt,
    )

    logging.info("Order list response: %s", json.dumps(order_response, indent=2))

    orders = order_response.get("orders", [])

    # Fetch order details for all orders
    if not orders:
        logging.info("No orders found for the specified date range.")
        return []

    # Extract order_sn from orders (Shopee API returns order_sn in order list)
    order_sns = []
    for order in orders:
        if "order_sn" in order:
            order_sns.append(order["order_sn"])

    if not order_sns:
        logging.warning("No valid order serial numbers found in orders")
        return orders

    logging.info(f"Fetching details for {len(order_sns)} orders")

    # Shopee API allows max 50 orders per request for get_order_detail
    detailed_orders = []
    batch_size = 50

    for i in range(0, len(order_sns), batch_size):
        batch_sns = order_sns[i : i + batch_size]
        logging.info(f"Processing batch {i//batch_size + 1}: {len(batch_sns)} orders")

        try:
            order_details_response = await get_order_detail(
                access_token=access_token, shop_id=account_id, order_sn_list=batch_sns
            )

            # order_details_response should contain "order_list"
            if "order_list" in order_details_response:
                detailed_orders.extend(order_details_response["order_list"])
                logging.info(
                    f"Successfully fetched details for {len(order_details_response['order_list'])} orders"
                )
            else:
                logging.warning("No order_list in order details response")

        except Exception as e:
            logging.error(
                f"Failed to fetch order details for batch {i//batch_size + 1}: {str(e)}"
            )
            # Continue with next batch even if one fails
            continue

    logging.info(f"Total detailed orders fetched: {len(detailed_orders)}")

    # Use detailed orders for processing instead of basic order list
    orders_to_process = detailed_orders if detailed_orders else orders

    insert_response = await post_processing(orders_to_process, index_name)
    logging.info("Insert response: %s", insert_response)

    return orders_to_process
