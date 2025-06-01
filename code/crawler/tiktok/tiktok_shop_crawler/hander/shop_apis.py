import aiohttp  # type: ignore
import time
import json
import logging
from typing import Dict, Any
from urllib.parse import urlencode


from model.setting import settings
from .sign import cal_sign


async def get_authorized_shop(access_token: str) -> Dict:
    """
    Fetch the shop info associated with the given access token.
    Merchant App only has one shop.
    """
    api_version = "202309"
    path = f"/authorization/{api_version}/shops"
    timestamp = int(time.time())

    params = {"app_key": settings.TIKTOK_SHOP_APP_KEY, "timestamp": timestamp}

    headers = {"x-tts-access-token": access_token, "Content-Type": "application/json"}

    # Construct URL for signing
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    url_with_params = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}?{query_string}"

    # Calculate signature
    sign = cal_sign(url_with_params, settings.TIKTOK_SHOP_APP_SECRET)
    params["sign"] = sign

    url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"

    shop_info = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            print("Response:", json.dumps(data, indent=2))

            if data.get("code") == 0 and "shops" in data.get("data", {}):
                shop_info = data["data"]["shops"][0]  # For Merchant App: 1 shop only
            else:
                print(f"Error: {data.get('message')}")

    return shop_info


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
    cursor = ""

    async with aiohttp.ClientSession() as session:
        while True:
            # Prepare query parameters (excluding sign)
            params = {
                "shop_id": shop_id,
                "app_key": settings.TIKTOK_SHOP_APP_KEY,
                "timestamp": int(time.time()),
                "access_token": access_token,
            }

            # Prepare payload body
            payload = {
                "create_time_from": create_time_from,
                "create_time_to": create_time_to,
                "page_size": page_size,
            }
            if cursor:
                payload["cursor"] = cursor

            # Build URL without sign
            query_string = urlencode(params)
            request_url = f"{base_url}?{query_string}"

            # Content type header
            content_type = "application/json"
            headers = {"Content-Type": content_type}

            # Calculate the signature using your cal_sign
            sign_value = cal_sign(
                url=request_url,
                app_secret=settings.TIKTOK_SHOP_APP_SECRET,
                body=json.dumps(payload).encode("utf-8"),
                content_type=content_type,
            )

            # Add sign param and rebuild final URL
            params["sign"] = sign_value
            final_url = f"{base_url}?{urlencode(params)}"

            # Make POST request
            async with session.post(
                final_url, json=payload, headers=headers
            ) as response:
                data = await response.json()
                logging.info("Response:", data)

                if data.get("code") == 0:
                    orders = data["data"]["order_list"]
                    all_orders.extend(orders)
                    cursor = data["data"].get("next_cursor")
                    print(data["data"]["more"])
                    if not data["data"].get("more"):
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"orders": all_orders}
