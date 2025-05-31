import time
import aiohttp  # type: ignore
import logging
from typing import Dict

from model.setting import settings
from .sign import sign


async def get_authorized_shop(access_token: str) -> Dict:
    """
    Sample response:
    {
      "cipher": "ROW_nOz1AgAAAADAhxvaZatbaNz6-2ms3Fi2",
      "code": "VNLCFLWLWT",
      "id": "7494530136736368761",
      "name": "Th\u1eddi Trang Trung Ni\u00ean ANCHI",
      "region": "VN",
      "seller_type": "LOCAL"
    }
    """
    api_version = "202309"
    path = f"/authorization/{api_version}/shops"

    headers = {"x-tts-access-token": access_token}
    params = {"app_key": settings.TIKTOK_SHOP_APP_KEY, "timestamp": int(time.time())}
    params["sign"] = sign(path, params, settings.TIKTOK_SHOP_APP_SECRET)

    shop_info = {}

    url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            logging.debug("Response: %s", data)
            if data.get("code") == 0:
                # this will return a list, but as Merchant App, we only have one shop
                shop_info = data["data"]["shops"][0]
            else:
                print(f"Error: {data.get('message')}")

    return shop_info
