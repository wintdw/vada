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
    Also enrich each line_item with product_detail.
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
                # logging.debug(f"Response: {data}")

                if data.get("code") == 0:
                    orders = data.get("data", {}).get("orders", [])
                    if not orders:
                        break

                    # Enrich each line_item with product_detail
                    for order in orders:
                        line_items = order.get("line_items", [])
                        for item in line_items:
                            product_id = item.get("product_id")
                            if product_id:
                                # Fetch product_detail for each product_id
                                product_detail = await get_product_detail(
                                    access_token=access_token,
                                    shop_cipher=shop_cipher,
                                    product_id=product_id,
                                )
                                item["product_detail"] = product_detail

                    all_orders.extend(orders)

                    page_token = data["data"].get("next_page_token")
                    if page_token:
                        logging.info(
                            f"More orders available, next page_token: {page_token}"
                        )
                    else:
                        logging.info("No more orders available")
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"total": len(all_orders), "orders": all_orders}


async def get_order_detail(
    access_token: str,
    shop_cipher: str,
    order_ids: List[str],
    chunk_size: int = 40,
) -> List[Dict]:
    """
    Fetch order details using the new TikTok Shop API (202309 version).
    Supports chunking for large order lists.
    """
    api_version = "202309"
    path = f"/order/{api_version}/orders"
    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"

    all_order_details: List[Dict] = []

    # Break the order_id_list into chunks
    total_chunks = (len(order_ids) + chunk_size - 1) // chunk_size
    logging.info(f"Total chunks to process: {total_chunks}")

    async with aiohttp.ClientSession() as session:
        for chunk_index, i in enumerate(range(0, len(order_ids), chunk_size), start=1):
            chunk = order_ids[i : i + chunk_size]
            ids_str = ",".join(chunk)
            timestamp = int(time.time())

            query_params = {
                "app_key": settings.TIKTOK_SHOP_APP_KEY,
                "shop_cipher": shop_cipher,
                "timestamp": timestamp,
                "ids": ids_str,
            }

            # Sign calculation (no body, GET request)
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

            logging.info(f"Fetching order detail chunk {chunk_index}/{total_chunks}.")

            async with session.get(
                base_url, params=query_params, headers=headers
            ) as response:
                data = await response.json()
                # logging.info(f"Response for chunk {chunk_index}: {data}")

                if data.get("code") == 0:
                    all_order_details.extend(data["data"]["orders"])
                else:
                    logging.error(
                        f"Error fetching order details for chunk {chunk_index}: {data.get('message')}",
                        exc_info=True,
                    )
                    raise Exception(f"Error: {data.get('message')}")

    logging.info(f"Finished processing all {total_chunks} chunks.")
    return all_order_details


async def get_price_detail(
    access_token: str,
    shop_cipher: str,
    order_id: str,
) -> Dict:
    """
    Fetch price detail of a specific order using TikTok Shop API (202407 version).
    """
    api_version = "202407"
    path = f"/order/{api_version}/orders/{order_id}/price_detail"
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

    async with aiohttp.ClientSession() as session:
        async with session.get(
            base_url, params=query_params, headers=headers
        ) as response:
            data = await response.json()

            if data.get("code") == 0:
                return data["data"]
            else:
                logging.error(
                    f"Failed to fetch price detail for order {order_id}: {data}",
                    exc_info=True,
                )
                raise Exception(f"Error: {data.get('message')}")


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

    async with aiohttp.ClientSession() as session:
        async with session.get(
            base_url, params=query_params, headers=headers
        ) as response:
            data = await response.json()

            if data.get("code") == 0:
                return data["data"]
            else:
                logging.error(
                    f"Failed to fetch product detail for product {product_id}: {data}",
                    exc_info=True,
                )
                raise Exception(f"Error: {data.get('message')}")
