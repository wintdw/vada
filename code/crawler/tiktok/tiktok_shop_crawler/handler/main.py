import time
import logging
from datetime import datetime
from typing import Dict, List

from tiktok_api.order_api import get_product_detail, get_price_detail, list_order
from tiktok_api.auth_api import get_authorized_shops
from tiktok_api.finance_api import get_transactions_by_statement, get_statements


async def get_orders_combined(
    access_token: str,
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
) -> Dict:
    """
    Fetch orders in the given time range, overcome 5000-order limit by range-splitting,
    then enrich each order with price_detail and product_detail.
    """
    # range-splitting to collect raw orders
    all_raw_orders: List[Dict] = []
    ranges = [(create_time_ge, create_time_lt)]

    while ranges:
        s_ts, e_ts = ranges.pop()
        order_json = await list_order(
            access_token=access_token,
            shop_cipher=shop_cipher,
            create_time_ge=s_ts,
            create_time_lt=e_ts,
        )
        total_orders = order_json.get("total", 0)
        if total_orders == 5000 and e_ts > s_ts:
            mid = (s_ts + e_ts) // 2
            ranges.append((s_ts, mid))
            ranges.append((mid, e_ts))
        else:
            all_raw_orders.extend(order_json.get("orders", []))

    # Enrich each order with price_detail and product_detail
    for order in all_raw_orders:
        order_id = order.get("id", "")
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
            order["price_detail"] = {}

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
                    item["product_detail"] = {}

    return {"total": len(all_raw_orders), "orders": all_raw_orders}


async def get_txns_by_statement(
    access_token: str,
    shop_cipher: str,
    statement_time_ge: int,
    statement_time_lt: int,
) -> Dict:
    """
    Fetch statements in the given time range and attach transactions for each statement.
    Uses finance_api.get_statements and finance_api.get_transactions_by_statement.
    """
    stmt_resp = await get_statements(
        access_token=access_token,
        shop_cipher=shop_cipher,
        statement_time_ge=statement_time_ge,
        statement_time_lt=statement_time_lt,
    )
    statements = stmt_resp.get("statements", [])

    for stmt in statements:
        stmt_id = stmt.get("id")
        try:
            txn_resp = await get_transactions_by_statement(
                access_token=access_token,
                shop_cipher=shop_cipher,
                statement_id=stmt_id,
            )
            stmt["transactions_detail"] = txn_resp
        except Exception as e:
            logging.error(
                "Failed to fetch transactions for statement %s: %s",
                stmt_id,
                e,
                exc_info=True,
            )
            stmt["transactions_detail"] = {}

    return {"total": len(statements), "statements": statements}


async def get_tiktokshop(access_token: str, start_ts: int, end_ts: int) -> Dict:
    """Fetch orders from TikTok Shop API using timestamps (delegates splitting+enrichment)."""
    profiling_start_time = time.time()

    shop_info = await get_authorized_shops(access_token)
    if not shop_info:
        raise Exception("No shop information found. Please check your access token.")

    logging.info(
        "Fetching orders from %s to %s for shop: %s",
        datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S"),
        datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S"),
        shop_info["name"],
    )
    orders_combined = await get_orders_combined(
        access_token=access_token,
        shop_cipher=shop_info["cipher"],
        create_time_ge=start_ts,
        create_time_lt=end_ts,
    )
    all_orders = orders_combined.get("orders", [])

    logging.info(
        "Fetching financial statements from %s to %s for shop: %s",
        datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S"),
        datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S"),
        shop_info["name"],
    )
    txns = await get_txns_by_statement(
        access_token=access_token,
        shop_cipher=shop_info["cipher"],
        statement_time_ge=start_ts,
        statement_time_lt=end_ts,
    )
    all_stmts = txns.get("statements", [])

    return_dict = {
        "status": "success",
        "orders": all_orders,
        "statements": all_stmts,
        "time_start": datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M:%S"),
        "time_end": datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M:%S"),
        "execution_time": time.time() - profiling_start_time,
    }

    return return_dict
