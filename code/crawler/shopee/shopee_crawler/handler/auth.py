import aiohttp  # type: ignore

from model.setting import settings


async def get_tokens(auth_code: str):
    """Get access and refresh tokens from auth code"""
    
    # app_key = settings.SHOPEE_APP_KEY
    app_secret = settings.TIKTOK_SHOP_APP_SECRET
    auth_base_url = settings.SHOPEE_AUTH_BASEURL

    params = {
        # "app_key": app_key,
        "app_secret": app_secret,
        "auth_code": auth_code,
        "grant_type": "authorized_code",
    }

    url = f"{auth_base_url}/api/v2/auth/token/get"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            result = await response.json()
            if result.get("code") == 0:
                return result["data"]
            else:
                raise Exception(f"Error: {result.get('message')}")


async def refresh_tokens(refresh_token):
    """Refresh access token using refresh token"""
    # app_key = settings.SHOPEE_APP_KEY
    app_secret = settings.TIKTOK_SHOP_APP_SECRET
    auth_base_url = settings.SHOPEE_AUTH_BASEURL

    params = {
        # "app_key": app_key,
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
