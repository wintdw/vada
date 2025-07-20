import time
import aiohttp  # type: ignore

from typing import Dict

from model.setting import settings


async def get_tokens(auth_code: str) -> Dict:
    """Get access and refresh tokens from auth code"""
    app_key = settings.TIKTOK_SHOP_APP_KEY
    app_secret = settings.TIKTOK_SHOP_APP_SECRET
    auth_base_url = settings.TIKTOK_SHOP_AUTH_BASEURL

    params = {
        "app_key": app_key,
        "app_secret": app_secret,
        "auth_code": auth_code,
        "grant_type": "authorized_code",
    }

    url = f"{auth_base_url}/api/v2/token/get"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            result = await response.json()
            if result.get("code") == 0:
                return result["data"]
            else:
                raise Exception(f"Error: {result.get('message')}")


async def refresh_tokens(refresh_token: str) -> Dict:
    """Refresh access token using refresh token"""
    app_key = settings.TIKTOK_SHOP_APP_KEY
    app_secret = settings.TIKTOK_SHOP_APP_SECRET
    auth_base_url = settings.TIKTOK_SHOP_AUTH_BASEURL

    params = {
        "app_key": app_key,
        "app_secret": app_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    url = f"{auth_base_url}/api/v2/token/refresh"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            result = await response.json()
            if result.get("code") == 0:
                return result["data"]
            else:
                raise Exception(f"Error: {result.get('message')}")


def check_days_left_to_expiry(expiry_timestamp: int) -> int:
    """
    Returns the number of days left until the given expiry timestamp (in seconds).
    If expiry is in the past, returns 0.
    """
    now = int(time.time())
    seconds_left = expiry_timestamp - now
    days_left = max(0, seconds_left // 86400)

    return days_left
