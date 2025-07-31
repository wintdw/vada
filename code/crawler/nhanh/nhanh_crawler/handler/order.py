import json
import aiohttp  # type: ignore
import logging
from typing import Dict

from model.settings import settings


async def get_product_detail(
    business_id: str,
    access_token: str,
    product_id: str,
) -> Dict:
    url = f"{settings.NHANH_BASE_URL}/product/detail"
    oauth_version = "2.0"
    headers = {"Accept": "application/json"}
    payload = {
        "version": oauth_version,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
        "data": product_id,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {}).get(product_id, {})
                else:
                    error_text = await response.text()
                    logging.debug(
                        f"Error getting product detail. Status: {response.status}, Response: {error_text}",
                        exc_info=True,
                    )
                    return {}
    except Exception as e:
        logging.debug(
            f"Unexpected error while getting product detail: {e}", exc_info=True
        )
        raise


async def get_orders(
    business_id: str, access_token: str, from_date: str, to_date: str, page: int = 1
):
    url = f"{settings.NHANH_BASE_URL}/order/index"
    oauth_version = "2.0"
    headers = {"Accept": "application/json"}
    payload = {"fromDate": from_date, "toDate": to_date, "page": page}
    data = {
        "version": oauth_version,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
        "data": json.dumps(payload),
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {})
                else:
                    error_text = await response.text()
                    logging.debug(
                        f"Error getting orders. Status: {response.status}, Response: {error_text}"
                    )
                    return {}
    except aiohttp.ClientError as e:
        logging.debug(f"HTTP client error while getting orders: {e}")
        raise
    except Exception as e:
        logging.debug(f"Unexpected error while getting orders: {e}")
        raise
