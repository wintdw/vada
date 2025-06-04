import aiohttp  # type: ignore
import time
import json
import logging
from typing import Dict, Any, List

from model.setting import settings
from .sign import cal_sign


async def get_order_list(
    access_token: str,
    shop_id: str,
    create_time_from: int,
    create_time_to: int,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    Fetch the order list from TikTok Shop API with paging.
    """
    path = "/api/orders/search"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"

    all_orders = []

    payload = {
        "create_time_from": create_time_from,
        "create_time_to": create_time_to,
        "page_size": page_size,
    }

    async with aiohttp.ClientSession() as session:
        while True:
            # Prepare query parameters (excluding sign)
            params = {
                "shop_id": shop_id,
                "app_key": settings.TIKTOK_SHOP_APP_KEY,
                "timestamp": int(time.time()),
                "access_token": access_token,
            }

            # Calculate the signature using your cal_sign
            params["sign"] = cal_sign(
                path=path,
                params=params,
                app_secret=settings.TIKTOK_SHOP_APP_SECRET,
                body=json.dumps(payload).encode("utf-8"),
            )

            # Make POST request
            async with session.post(base_url, params=params, json=payload) as response:
                data = await response.json()
                logging.info(f"Response: {data}")

                if data.get("code") == 0:
                    orders = data["data"]["order_list"]
                    all_orders.extend(orders)

                    # Paging
                    if data["data"].get("more"):
                        cursor = data["data"].get("next_cursor", "")
                        payload["cursor"] = cursor
                        logging.info(f"More orders available, next cursor: {cursor}")
                    else:
                        logging.info("No more orders available.")
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"shop_id": shop_id, "total": len(all_orders), "orders": all_orders}


async def get_order_detail(
    access_token: str,
    shop_id: str,
    order_id_list: List[str],
    chunk_size: int = 40,  # Maximum number of order IDs per request
) -> List[Dict]:
    """
    Fetch detailed information for a list of orders from TikTok Shop API.
    Handles cases where the order_id_list exceeds the API limit by chunking the list.
    """
    path = "/api/orders/detail/query"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"

    all_order_details = []

    # Split the order_id_list into chunks of size <= chunk_size
    for i in range(0, len(order_id_list), chunk_size):
        chunk = order_id_list[i : i + chunk_size]
        payload = {"order_id_list": chunk}

        async with aiohttp.ClientSession() as session:
            # Prepare query parameters (excluding sign)
            params = {
                "shop_id": shop_id,
                "app_key": settings.TIKTOK_SHOP_APP_KEY,
                "timestamp": int(time.time()),
                "access_token": access_token,
            }

            # Calculate the signature using your cal_sign
            params["sign"] = cal_sign(
                path=path,
                params=params,
                app_secret=settings.TIKTOK_SHOP_APP_SECRET,
                body=json.dumps(payload).encode("utf-8"),
            )

            # Make POST request
            async with session.post(base_url, params=params, json=payload) as response:
                data = await response.json()
                # logging.info(f"Response for chunk {i // chunk_size + 1}: {data}")

                if data.get("code") == 0:
                    all_order_details.extend(data["data"]["order_list"])
                else:
                    logging.error(
                        f"Error fetching order details for chunk {i // chunk_size + 1}: {data.get('message')}",
                        exc_info=True,
                    )
                    raise Exception(f"Error: {data.get('message')}")

    return all_order_details
