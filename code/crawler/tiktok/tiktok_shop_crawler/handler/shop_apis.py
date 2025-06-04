import aiohttp  # type: ignore
import time
import json
import logging
from typing import Dict

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

    # Calculate signature
    sign = cal_sign(
        path=path, params=params, app_secret=settings.TIKTOK_SHOP_APP_SECRET
    )
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
