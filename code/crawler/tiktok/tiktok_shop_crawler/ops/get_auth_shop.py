import json
import aiohttp  # type: ignore
import asyncio
import time
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qsl, urlencode


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Load credentials from a file
def load_creds(path: str = "creds.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


creds = load_creds()

APP_KEY = creds["APP_KEY"]
APP_SECRET = creds["APP_SECRET"]
ACCESS_TOKEN = creds["ACCESS_TOKEN"]
BASE_URL = creds.get("BASE_URL", "https://open-api.tiktokglobalshop.com")


def cal_sign(
    url: str,
    app_secret: str,
    body: Optional[bytes] = b"",
    content_type: str = "",
) -> str:
    """
    Generate the TikTok Shop API signature.

    :param url: Full request URL including query string.
    :param app_secret: TikTok Shop app secret.
    :param body: Request body as raw bytes (only for POST/PUT).
    :param content_type: Content-Type header (e.g. application/json).
    :return: HMAC-SHA256 signature string.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path

    # Parse and filter query parameters
    query_params = {
        k: v
        for k, v in parse_qsl(parsed_url.query)
        if k not in ("sign", "access_token")
    }

    # Sort and concatenate query parameters
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(query_params.items()))
    base_string = f"{path}{sorted_params}"

    # Append body if not multipart
    if content_type.lower() != "multipart/form-data" and body:
        base_string += body.decode("utf-8")

    # Final string to sign
    to_sign = f"{app_secret}{base_string}{app_secret}"

    # HMAC-SHA256 hash
    return hmac.new(
        key=app_secret.encode("utf-8"),
        msg=to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


async def get_authorized_shop(access_token: str) -> Dict:
    """
    Fetch the shop info associated with the given access token.
    Merchant App only has one shop.
    """
    api_version = "202309"
    path = f"/authorization/{api_version}/shops"
    timestamp = int(time.time())

    params = {"app_key": APP_KEY, "timestamp": timestamp}

    headers = {"x-tts-access-token": access_token, "Content-Type": "application/json"}

    # Construct URL for signing
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    url_with_params = f"{BASE_URL}{path}?{query_string}"

    # Calculate signature
    sign = cal_sign(url_with_params, APP_SECRET)
    params["sign"] = sign

    url = f"{BASE_URL}{path}"

    shop_info = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            print("Response:", json.dumps(data, indent=2))

            if data.get("code") == 0 and "shops" in data.get("data", {}):
                shop_info = data["data"]["shops"][0]  # For Merchant App: 1 shop only
            else:
                print(f"Error: {data.get('message')}")

    return shop_info


async def get_order_list(
    access_token: str,
    shop_id: str,
    create_time_from: int,
    create_time_to: int,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    Fetch the order list from TikTok Shop API with paging.
    """
    path = "/api/orders/search"
    base_url = f"{BASE_URL}{path}"

    all_orders = []
    cursor = ""

    async with aiohttp.ClientSession() as session:
        while True:
            # Prepare query parameters (excluding sign)
            params = {
                "shop_id": shop_id,
                "app_key": APP_KEY,
                "timestamp": int(time.time()),
                "access_token": access_token,
            }

            # Prepare payload body
            payload = {
                "create_time_from": create_time_from,
                "create_time_to": create_time_to,
                "page_size": page_size,
            }
            if cursor:
                payload["cursor"] = cursor

            # Build URL without sign
            query_string = urlencode(params)
            request_url = f"{base_url}?{query_string}"

            # Content type header
            content_type = "application/json"
            headers = {"Content-Type": content_type}

            # Calculate the signature using your cal_sign
            sign_value = cal_sign(
                url=request_url,
                app_secret=APP_SECRET,
                body=json.dumps(payload).encode("utf-8"),
                content_type=content_type,
            )

            # Add sign param and rebuild final URL
            params["sign"] = sign_value
            final_url = f"{base_url}?{urlencode(params)}"

            # Make POST request
            async with session.post(
                final_url, json=payload, headers=headers
            ) as response:
                data = await response.json()
                logging.info("Response:", data)

                if data.get("code") == 0:
                    orders = data["data"]["order_list"]
                    all_orders.extend(orders)
                    cursor = data["data"].get("next_cursor")
                    print(data["data"]["more"])
                    if not data["data"].get("more"):
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"orders": all_orders}


async def main():
    shop_info = await get_authorized_shop(ACCESS_TOKEN)
    logging.info("Shop Info: %s", json.dumps(shop_info, indent=2))

    orders = await get_order_list(
        access_token=ACCESS_TOKEN,
        shop_id=shop_info["id"],
        create_time_from=int(time.time()) - 864000,  # Last 24 hours
        create_time_to=int(time.time()),
        page_size=100,
    )
    logging.info(
        "Orders: %s, Length: %d", json.dumps(orders, indent=2), len(orders["orders"])
    )


if __name__ == "__main__":
    asyncio.run(main())
