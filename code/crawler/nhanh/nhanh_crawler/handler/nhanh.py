import time
import logging

from typing import Dict

from .order import get_orders
from .product import get_products


async def crawl_nhanh_data(
    business_id: str, access_token: str, from_date: str, to_date: str
) -> Dict:
    start_time = time.time()

    # Fetch product cache once
    logging.info("Fetching product cache...")
    products = await get_products(business_id, access_token)
    product_cache = {product["idNhanh"]: product for product in products}

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

    return_dict = {
        "status": "success",
        "total_orders": len(orders),
        "orders": orders,
        "date_start": from_date,
        "date_end": to_date,
        "execution_time": time.time() - start_time,
    }
    logging.debug(
        f"Total orders: {len(orders)} in {return_dict['execution_time']} seconds"
    )

    return return_dict
