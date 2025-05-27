import aiohttp  # type: ignore
import asyncio

from model.setting import settings


class TikTokShopAuth:
    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.token_base_url = settings.TIKTOK_SHOP_AUTH_BASEURL

    async def get_tokens(self, auth_code):
        """Get access and refresh tokens from auth code"""
        params = {
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "auth_code": auth_code,
            "grant_type": "authorized_code",
        }

        url = f"{self.token_base_url}/api/v2/token/get"

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

        url = f"{self.token_base_url}/api/v2/token/refresh"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                result = await response.json()
                if result.get("code") == 0:
                    return result["data"]
                else:
                    raise Exception(f"Error: {result.get('message')}")


# Simple usage example
async def main():
    auth = TikTokShopAuth(settings.TIKTOK_SHOP_APP_KEY, settings.TIKTOK_SHOP_APP_SECRET)

    # Step 1: Get auth code from TikTok Shop authorization page
    auth_code = input("Enter auth_code from callback: ")

    try:
        # Step 2: Exchange auth code for tokens
        tokens = await auth.get_tokens(auth_code)
        print(f"Access Token: {tokens['access_token']}")
        print(f"Refresh Token: {tokens['refresh_token']}")
        print(f"Seller: {tokens['seller_name']}")

        # Step 3: Refresh tokens
        new_tokens = await auth.refresh_tokens(tokens["refresh_token"])
        print(f"New Access Token: {new_tokens['access_token']}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
