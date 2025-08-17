import time
import json
import logging
from typing import Dict

from model.setting import settings
from .sign import cal_sign
from .request import retry_get  # Import retry_get


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

    # Use retry_get for robust request
    data = await retry_get(url=url, headers=headers, params=params)
    logging.info(f"Getting authorized shops: {json.dumps(data, indent=2)}")

    shop_info = {}
    if data.get("code") == 0 and "shops" in data.get("data", {}):
        shop_info = data["data"]["shops"][0]  # For Merchant App: 1 shop only
        # warn if > 1 shops
        if len(data["data"]["shops"]) > 1:
            logging.warning(f"Multiple shops found: {len(data['data']['shops'])}")
    else:
        logging.error(f"Error: {json.dumps(data, indent=2)}", exc_info=True)

    return shop_info
