import aiohttp  # type: ignore
import time
import json
import logging
from typing import Dict, Any, List

from model.setting import settings
from .sign import cal_sign


async def get_order_list(
    access_token: str,
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    Fetch the order list from the new TikTok Shop API (202309 version) with paging.
    """
    api_version = "202309"
    path = f"/order/{api_version}/orders/search"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"

    all_orders = []
    page_token = ""

    async with aiohttp.ClientSession() as session:
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
                # "update_time_ge": create_time_ge,  # Optional
                # "update_time_lt": create_time_lt,  # Optional
                # "shipping_type": "TIKTOK",        # Optional
                # "buyer_user_id": "7213489962827123654",  # Optional
                # "is_buyer_request_cancel": False,
                # "warehouse_ids": ["7000714532876273888", "7000714532876273666"]
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

            async with session.post(
                base_url, params=query_params, json=payload, headers=headers
            ) as response:
                data = await response.json()
                logging.info(f"Response: {data}")

                if data.get("code") == 0:
                    orders = data["data"]["orders"]
                    all_orders.extend(orders)

                    page_token = data["data"].get("next_page_token")
                    if page_token:
                        logging.info(
                            f"More orders available, next page_token: {page_token}"
                        )
                    else:
                        logging.info("No more orders available.")
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"total": len(all_orders), "orders": all_orders}


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

    # Calculate the total number of chunks
    total_chunks = (len(order_id_list) + chunk_size - 1) // chunk_size
    logging.info(f"Total chunks to process: {total_chunks}")

    # Split the order_id_list into chunks of size <= chunk_size
    for chunk_index, i in enumerate(range(0, len(order_id_list), chunk_size), start=1):
        chunk = order_id_list[i : i + chunk_size]
        payload = {"order_id_list": chunk}

        logging.info(
            f"Processing chunk {chunk_index}/{total_chunks} with {len(chunk)} orders."
        )

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
                # logging.info(f"Response for chunk {chunk_index}: {data}")

                if data.get("code") == 0:
                    all_order_details.extend(data["data"]["order_list"])
                else:
                    logging.error(
                        f"Error fetching order details for chunk {chunk_index}: {data.get('message')}",
                        exc_info=True,
                    )
                    raise Exception(f"Error: {data.get('message')}")

    logging.info(f"Finished processing all {total_chunks} chunks.")
    return all_order_details
