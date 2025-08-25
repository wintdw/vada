import time
import logging
from datetime import datetime
from typing import Dict, List

from tiktok_api.order_api import get_product_detail, get_price_detail, list_order
from tiktok_api.auth_api import get_authorized_shops
from tiktok_api.finance import get_transactions_by_order


async def get_order_all(
    access_token: str,
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
) -> Dict:
    """
    Fetch all orders from TikTok Shop API with price and product details.
    """
    order_resp = await list_order(
        access_token=access_token,
        shop_cipher=shop_cipher,
        create_time_ge=create_time_ge,
        create_time_lt=create_time_lt,
    )
    orders = order_resp.get("orders", [])

    # Enrich each order with price_detail and each line_item with product_detail
    for order in orders:
        # Attach price_detail
        order_id = order.get("id")
        try:
            price_detail = await get_price_detail(
                access_token=access_token,
                shop_cipher=shop_cipher,
                order_id=order_id,
            )
            order["price_detail"] = price_detail
        except Exception as e:
            logging.error(
                f"Failed to fetch price_detail for order {order_id}: {e}",
                exc_info=True,
            )
            order["price_detail"] = None

        # Attach transaction_detail (SKU-level statement transactions)
        try:
            transaction_detail = await get_transactions_by_order(
                access_token=access_token,
                shop_cipher=shop_cipher,
                order_id=order_id,
            )
            order["transaction_detail"] = transaction_detail
        except Exception as e:
            logging.error(
                f"Failed to fetch transaction_detail for order {order_id}: {e}",
                exc_info=True,
            )
            order["transaction_detail"] = None

        line_items = order.get("line_items", [])
        for item in line_items:
            product_id = item.get("product_id")
            if product_id:
                try:
                    product_detail = await get_product_detail(
                        access_token=access_token,
                        shop_cipher=shop_cipher,
                        product_id=product_id,
                    )
                    item["product_detail"] = product_detail
                except Exception as e:
                    logging.error(
                        f"Failed to fetch product_detail for product {product_id}: {e}",
                        exc_info=True,
                    )
                    item["product_detail"] = None

    return {"total": len(orders), "orders": orders}


async def get_orders(access_token: str, start_ts: int, end_ts: int) -> Dict:
    """Fetch orders from TikTok Shop API using timestamps.

    This function overcomes the TikTok Shop API's 5000 orders per request limit
    by using a range-splitting algorithm:

    - Start with the full requested time range.
    - If the API returns exactly 5000 orders,
      split the range in half and add both halves to the processing queue.
    - Repeat until all ranges return fewer than 5000 orders.
    - Aggregate all orders from all sub-ranges and post-process them.

    Args:
        access_token: TikTok Shop access token
        start_ts: Start timestamp (epoch seconds)
        end_ts: End timestamp (epoch seconds)

    Returns:
        Dict: Orders response after post-processing
    """
    profiling_start_time = time.time()

    shop_info = await get_authorized_shops(access_token)
    if not shop_info:
        raise Exception("No shop information found. Please check your access token.")

    logging.info(
        "Fetching orders from %s to %s for shop ID: %s",
        datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S"),
        datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S"),
        shop_info["id"],
    )

    all_orders: List[Dict] = []
    ranges = [(start_ts, end_ts)]

    # Range-splitting algorithm to overcome 5000 orders limit
    while ranges:
        s_ts, e_ts = ranges.pop()
        order_json = await get_order_all(
            access_token=access_token,
            shop_cipher=shop_info["cipher"],
            create_time_ge=s_ts,
            create_time_lt=e_ts,
        )
        total = order_json.get("total", 0)
        # If we hit the 5000 limit, split the range.
        # This ensures we do not miss any orders, regardless of the range size.
        if total == 5000 and e_ts > s_ts:
            mid = (s_ts + e_ts) // 2
            ranges.append((s_ts, mid))
            ranges.append((mid, e_ts))
        else:
            all_orders.extend(order_json.get("orders", []))

    return_dict = {
        "status": "success",
        "total_orders": len(all_orders),
        "orders": all_orders,
        "time_start": datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S"),
        "time_end": datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time": time.time() - profiling_start_time,
    }

    return return_dict
