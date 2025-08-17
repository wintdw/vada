import json
import logging
import aiohttp  # type: ignore
import asyncio
from typing import Dict, Any, Optional

from model.setting import settings
from .sign import cal_sign


async def tiktok_api_request(
    method: str,
    path: str,
    access_token: str,
    shop_cipher: str,
    params: Dict = {},
    payload: Dict = {},
) -> Dict:
    """
    Common TikTok Shop API request handler.
    """
    import time

    base_url = f"{settings.TIKTOK_SHOP_API_BASEURL}{path}"
    timestamp = int(time.time())
    query_params = {
        "app_key": settings.TIKTOK_SHOP_APP_KEY,
        "timestamp": timestamp,
        "shop_cipher": shop_cipher,
    }
    if params:
        query_params.update(params)

    # Sign calculation
    sign_kwargs = {
        "path": path,
        "params": query_params,
        "app_secret": settings.TIKTOK_SHOP_APP_SECRET,
        "content_type": "application/json",
    }
    if payload:
        sign_kwargs["body"] = json.dumps(payload).encode("utf-8")
    query_params["sign"] = cal_sign(**sign_kwargs)

    headers = {
        "x-tts-access-token": access_token,
        "content-type": "application/json",
    }

    if method == "POST":
        data = await retry_post(
            url=base_url, headers=headers, params=query_params, json_payload=payload
        )
    else:
        data = await retry_get(url=base_url, headers=headers, params=query_params)

    if data.get("code") == 0:
        return data["data"]
    else:
        logging.error(f"Failed TikTok API call {path}: {data}", exc_info=True)
        raise Exception(f"Error: {data.get('message')}")


async def retry_post(
    url: str,
    headers: Dict[str, str],
    params: Optional[Dict[str, Any]] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    max_retries: int = 10,
    retry_delay: int = 30,
) -> Dict:
    """
    Retry POST request for TikTok Shop API.
    Args:
        url: API endpoint
        headers: HTTP headers
        params: Query parameters
        json_payload: JSON body
        max_retries: Number of retries
        retry_delay: Delay between retries (seconds)
    Returns:
        Dict: Response JSON
    Raises:
        Exception if all retries fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, params=params, json=json_payload, headers=headers
                ) as response:
                    data = await response.json()
                    if response.status == 200 and data.get("code") == 0:
                        return data
                    else:
                        logging.warning(
                            f"[Attempt {attempt}] Error querying {url}. Status: {response.status}, Response: {data}"
                        )
        except Exception as e:
            logging.warning(f"[Attempt {attempt}] Exception with {url}: {e}")
        if attempt < max_retries:
            logging.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    logging.error(f"Failed to query {url} after {max_retries} attempts", exc_info=True)
    raise Exception(f"Failed to query {url} after {max_retries} attempts")


async def retry_get(
    url: str,
    headers: Dict[str, str],
    params: Optional[Dict[str, Any]] = None,
    max_retries: int = 10,
    retry_delay: int = 30,
) -> Dict:
    """
    Retry GET request for TikTok Shop API.
    Args:
        url: API endpoint
        headers: HTTP headers
        params: Query parameters
        max_retries: Number of retries
        retry_delay: Delay between retries (seconds)
    Returns:
        Dict: Response JSON
    Raises:
        Exception if all retries fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    data = await response.json()
                    if response.status == 200 and data.get("code") == 0:
                        return data
                    else:
                        logging.warning(
                            f"[Attempt {attempt}] Error querying {url}. Status: {response.status}, Response: {data}"
                        )
        except Exception as e:
            logging.warning(f"[Attempt {attempt}] Exception with {url}: {e}")
        if attempt < max_retries:
            logging.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    logging.error(f"Failed to query {url} after {max_retries} attempts", exc_info=True)
    raise Exception(f"Failed to query {url} after {max_retries} attempts")
