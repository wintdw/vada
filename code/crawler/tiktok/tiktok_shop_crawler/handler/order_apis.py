import time
import json
import logging
from typing import Dict, Any

from model.setting import settings
from .sign import cal_sign
from .request import retry_post, retry_get


async def get_order_all(
    access_token: str,
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
) -> Dict[str, Any]:
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
        order_id = order.get("order_id")
        if order_id:
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


async def list_order(
    access_token: str,
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    Fetch the order list from the new TikTok Shop API (202309 version) with paging.
    Also enrich each line_item with product_detail.

    Limitations:
    - The API supports a maximum of 50 orders per page, 100 pages per request -> max 5k orders
    """
    api_version = "202309"
    path = f"/order/{api_version}/orders/search"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"

    all_orders = []
    page_token = ""

    while True:
        timestamp = int(time.time())

        # Prepare query parameters
        query_params = {
            "app_key": settings.TIKTOK_SHOP_APP_KEY,
            "shop_cipher": shop_cipher,
            "timestamp": timestamp,
            "page_size": page_size,
        }

        if page_token:
            query_params["page_token"] = page_token

        # JSON body (filter conditions)
        payload = {
            "create_time_ge": create_time_ge,
            "create_time_lt": create_time_lt,
        }

        # Sign calculation
        query_params["sign"] = cal_sign(
            path=path,
            params=query_params,
            app_secret=settings.TIKTOK_SHOP_APP_SECRET,
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )

        headers = {
            "x-tts-access-token": access_token,
            "content-type": "application/json",
        }

        # Use retry_post for robust request
        data = await retry_post(
            url=base_url, headers=headers, params=query_params, json_payload=payload
        )

        if data.get("code") == 0:
            orders = data.get("data", {}).get("orders", [])
            if not orders:
                break

            all_orders.extend(orders)

            page_token = data["data"].get("next_page_token")
            if page_token:
                logging.info(f"More orders available, next page_token: {page_token}")
            else:
                logging.info("No more orders available")
                break
        else:
            raise Exception(f"Error: {data.get('message')}")

    return {"total": len(all_orders), "orders": all_orders}


async def get_product_detail(
    access_token: str, shop_cipher: str, product_id: str
) -> Dict:
    """
    Retrieve all properties of a product (DRAFT, PENDING, or ACTIVATE status) from TikTok Shop API (202309 version).
    """
    api_version = "202309"
    path = f"/product/{api_version}/products/{product_id}"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"
    timestamp = int(time.time())

    # Prepare query parameters
    query_params = {
        "app_key": settings.TIKTOK_SHOP_APP_KEY,
        "timestamp": timestamp,
        "shop_cipher": shop_cipher,
    }

    # Sign calculation (GET request, no body)
    query_params["sign"] = cal_sign(
        path=path,
        params=query_params,
        app_secret=settings.TIKTOK_SHOP_APP_SECRET,
        content_type="application/json",
    )

    headers = {
        "x-tts-access-token": access_token,
        "content-type": "application/json",
    }

    # Use retry_get for robust request
    data = await retry_get(url=base_url, headers=headers, params=query_params)

    if data.get("code") == 0:
        return data["data"]
    else:
        logging.error(
            f"Failed to fetch product detail for product {product_id}: {data}",
            exc_info=True,
        )
        raise Exception(f"Error: {data.get('message')}")


async def get_price_detail(access_token: str, shop_cipher: str, order_id: str) -> Dict:
    """
    Fetch price detail for a TikTok Shop order.
    """
    api_version = "202407"

    path = f"/order/{api_version}/orders/{order_id}/price_detail"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"
    timestamp = int(time.time())

    query_params = {
        "app_key": settings.TIKTOK_SHOP_APP_KEY,
        "timestamp": timestamp,
        "shop_cipher": shop_cipher,
    }

    # Sign calculation (GET request, no body)
    query_params["sign"] = cal_sign(
        path=path,
        params=query_params,
        app_secret=settings.TIKTOK_SHOP_APP_SECRET,
        content_type="application/json",
    )

    headers = {
        "x-tts-access-token": access_token,
        "content-type": "application/json",
    }

    data = await retry_get(url=base_url, headers=headers, params=query_params)

    if data.get("code") == 0:
        return data["data"]
    else:
        logging.error(
            f"Failed to fetch price detail for order {order_id}: {data}",
            exc_info=True,
        )
        raise Exception(f"Error: {data.get('message')}")
