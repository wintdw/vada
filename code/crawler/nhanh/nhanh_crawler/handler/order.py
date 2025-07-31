import json
import aiohttp  # type: ignore
import asyncio
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

    max_retries = 10
    retry_delay = 30  # seconds

    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get(product_id, {})
                    else:
                        error_text = await response.text()
                        logging.debug(
                            f"Attempt {attempt + 1}: Failed to get product detail. Status: {response.status}, Response: {error_text}",
                            exc_info=True,
                        )
        except Exception as e:
            logging.debug(
                f"Attempt {attempt + 1}: Exception while getting product detail: {e}",
                exc_info=True,
            )

        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)

    return {}


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

    max_retries = 10
    retry_delay = 30  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {})
                    else:
                        error_text = await response.text()
                        logging.warning(
                            f"[Attempt {attempt}] Error getting orders. "
                            f"Status: {response.status}, Response: {error_text}"
                        )
        except aiohttp.ClientError as e:
            logging.warning(f"[Attempt {attempt}] HTTP client error: {e}")
        except Exception as e:
            logging.warning(f"[Attempt {attempt}] Unexpected error: {e}")

        if attempt < max_retries:
            logging.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    logging.error(f"Failed to get orders after {max_retries} attempts")
    return {}
