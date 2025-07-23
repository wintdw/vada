import urllib.parse
import aiohttp  # type: ignore
import time
import logging
from model.setting import settings

from model.setting import settings
from utils.utils import _generate_signature_shop, _get_domain


async def get_authorized_shop(
    access_token: str,
    shop_id: int
):
    path = "/api/v2/shop/get_shop_info"
    timestamp = int(time.time())
    sign = _generate_signature_shop(path, timestamp, access_token, shop_id)
    domain = _get_domain(True)
 
    logging.info(f"get_authorized_shop::sign: {sign} and timestamp: {timestamp}")
    
    query = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign
    }
    url = f"https://{domain}{path}?{urllib.parse.urlencode(query)}"
   
    logging.info(f"get_authorized_shop::path: {url}")


    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
