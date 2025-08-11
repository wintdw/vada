import aiohttp  # type: ignore
import asyncio
import logging

from typing import Dict

from model.settings import settings


async def retry_post(
    url: str, business_id: str, access_token: str, payload: str = ""
) -> Dict:
    oauth_version = "2.0"
    headers = {"Accept": "application/json"}
    data = {
        "version": oauth_version,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
    }
    if payload:
        data["data"] = payload

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
                            f"[Attempt {attempt}] Error querying {url}. Status: {response.status}, Response: {error_text}"
                        )
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1}: Exception with {url}: {e}")
        if attempt < max_retries:
            logging.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    logging.error(f"Failed to query {url} after {max_retries} attempts")
    raise Exception(f"Failed to query {url} after {max_retries} attempts")
