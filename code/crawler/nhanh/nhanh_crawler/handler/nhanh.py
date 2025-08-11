import re
import time
import logging

from typing import Dict, Any

from .order import get_orders
from .product import get_products


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def convert_keys_to_snake_case(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            camel_to_snake(k): convert_keys_to_snake_case(v) for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_keys_to_snake_case(item) for item in obj]
    else:
        return obj


# Main function
async def crawl_nhanh_data(
    business_id: str, access_token: str, from_date: str, to_date: str
) -> Dict:
    start_time = time.time()

    # Fetch product cache once
    logging.info(f"[{business_id}] Fetching product cache...")
    products = await get_products(business_id, access_token)
    product_cache = {str(product["idNhanh"]): product for product in products}

    orders = await get_orders(business_id, access_token, from_date, to_date)

    for order in orders:
        # Map saleChannel to saleChannelName
        sale_channel_mapping = {
            "1": "Admin",
            "2": "Website",
            "10": "API",
            "20": "Facebook",
            "21": "Instagram",
            "41": "Lazada.vn",
            "42": "Shopee.vn",
            "43": "Sendo.vn",
            "45": "Tiki.vn",
            "46": "Zalo Shop",
            "47": "1Landing.vn",
            "48": "Tiktok Shop",
            "49": "Zalo OA",
            "50": "Shopee Chat",
            "51": "Lazada Chat",
        }
        sale_channel = str(order.get("saleChannel", ""))
        order["saleChannelName"] = sale_channel_mapping.get(sale_channel, "Unknown")

        # Sanitize fields
        if order.get("packed", {}).get("datetime", "") == "":
            order["packed"]["datetime"] = "2000-01-01 00:00:00"

        # Customize fields
        total_import_money = 0
        for product in order.get("products", []):
            product_id = product.get("productId")
            product_detail = product_cache.get(product_id)
            product["detail"] = product_detail

            if product_detail and product_detail.get("importPrice"):
                product["importMoney"] = int(product_detail["importPrice"]) * int(
                    product["quantity"]
                )
                total_import_money += product["importMoney"]
        order["TotalImportMoney"] = total_import_money

    # Convert all order fields to snake_case
    orders = [convert_keys_to_snake_case(order) for order in orders]

    return_dict = {
        "status": "success",
        "total_orders": len(orders),
        "orders": orders,
        "date_start": from_date,
        "date_end": to_date,
        "execution_time": time.time() - start_time,
    }
    logging.debug(
        f"[{business_id}] Total orders: {len(orders)} in {return_dict['execution_time']} seconds"
    )

    return return_dict
