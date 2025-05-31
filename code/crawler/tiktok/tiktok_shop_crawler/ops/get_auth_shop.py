import json
import aiohttp  # type: ignore
import asyncio
import time
import hmac
import hashlib


# Load credentials from a file
def load_creds(path: str = "creds.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


creds = load_creds()

APP_KEY = creds["APP_KEY"]
APP_SECRET = creds["APP_SECRET"]
ACCESS_TOKEN = creds["ACCESS_TOKEN"]
BASE_URL = creds.get("BASE_URL", "https://open-api.tiktokglobalshop.com")


def sign(path: str, query_params: dict, app_secret: str) -> str:
    sorted_params = dict(sorted(query_params.items()))
    concatenated = "".join(f"{k}{v}" for k, v in sorted_params.items())
    base_string = f"{path}{concatenated}"
    to_sign = f"{app_secret}{base_string}{app_secret}"
    return hmac.new(
        key=app_secret.encode("utf-8"),
        msg=to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


async def get_authorized_shops():
    path = "/authorization/202309/shops"
    timestamp = int(time.time())

    params = {"app_key": APP_KEY, "timestamp": timestamp}
    headers = {"x-tts-access-token": ACCESS_TOKEN}
    params["sign"] = sign(path, params, APP_SECRET)

    url = f"{BASE_URL}{path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            print("Response:", json.dumps(data, indent=2))
            if data.get("code") == 0:
                shops = data["data"]["shops"]
                for shop in shops:
                    print("Shop:", json.dumps(shop, indent=2))
            else:
                print(f"Error: {data.get('message')}")


if __name__ == "__main__":
    asyncio.run(get_authorized_shops())
