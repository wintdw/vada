import logging
from typing import Dict, Any

from .request import tiktok_api_request


async def list_order(
    access_token: str,
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
) -> Dict[str, Any]:
    """
    Fetch the order list from the new TikTok Shop API (202309 version) with paging.
    Also enrich each line_item with product_detail.

    Limitations:
    - The API supports a maximum of 50 orders per page, 100 pages per request -> max 5k orders
    """
    api_version = "202309"
    path = f"/order/{api_version}/orders/search"
    page_size = 100

    all_orders = []
    page_token = ""

    while True:
        query_params = {
            "page_size": page_size,
        }
        if page_token:
            query_params["page_token"] = page_token

        payload = {
            "create_time_ge": create_time_ge,
            "create_time_lt": create_time_lt,
        }

        data = await tiktok_api_request(
            method="POST",
            path=path,
            access_token=access_token,
            shop_cipher=shop_cipher,
            params=query_params,
            payload=payload,
        )

        orders = data.get("orders", [])
        if not orders:
            break

        all_orders.extend(orders)

        page_token = data.get("next_page_token")
        if page_token:
            logging.info(f"More orders available, next page_token: {page_token}")
        else:
            logging.debug("No more orders available")
            break

    return {"total": len(all_orders), "orders": all_orders}


async def get_product_detail(
    access_token: str, shop_cipher: str, product_id: str
) -> Dict:
    """
    Retrieve all properties of a product (DRAFT, PENDING, or ACTIVATE status) from TikTok Shop API (202309 version).
    """
    api_version = "202309"
    path = f"/product/{api_version}/products/{product_id}"

    data = await tiktok_api_request(
        method="GET",
        path=path,
        access_token=access_token,
        shop_cipher=shop_cipher,
    )

    return data


async def get_price_detail(access_token: str, shop_cipher: str, order_id: str) -> Dict:
    """
    Fetch price detail for a TikTok Shop order.
    """
    api_version = "202407"
    path = f"/order/{api_version}/orders/{order_id}/price_detail"

    data = await tiktok_api_request(
        method="GET",
        path=path,
        access_token=access_token,
        shop_cipher=shop_cipher,
    )

    return data
