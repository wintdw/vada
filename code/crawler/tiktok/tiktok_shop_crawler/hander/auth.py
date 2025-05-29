import aiohttp  # type: ignore

from model.setting import settings


class TikTokShopAuth:
    def __init__(self):
        self.app_key = settings.TIKTOK_SHOP_APP_KEY
        self.app_secret = settings.TIKTOK_SHOP_APP_SECRET
        self.auth_base_url = settings.TIKTOK_SHOP_AUTH_BASEURL

    async def get_tokens(self, auth_code):
        """Get access and refresh tokens from auth code"""
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "auth_code": auth_code,
            "grant_type": "authorized_code",
        }

        url = f"{self.auth_base_url}/api/v2/token/get"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if result.get("code") == 0:
                    return result["data"]
                else:
                    raise Exception(f"Error: {result.get('message')}")

    async def refresh_tokens(self, refresh_token):
        """Refresh access token using refresh token"""
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        url = f"{self.auth_base_url}/api/v2/token/refresh"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if result.get("code") == 0:
                    return result["data"]
                else:
                    raise Exception(f"Error: {result.get('message')}")
