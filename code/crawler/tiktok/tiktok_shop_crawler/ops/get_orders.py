import json
import aiohttp  # type: ignore
import asyncio
import time
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional


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
    path: str,
    params: Dict[str, Any],
    app_secret: str,
    body: Optional[bytes] = b"",
    content_type: str = "",
) -> str:
    """
    Generate the TikTok Shop API signature.

    :param path: API path, e.g. "/api/orders/search".
    :param params: Query parameters (excluding 'sign' and 'access_token').
    :param app_secret: TikTok Shop app secret.
    :param body: Request body as raw bytes (used for POST/PUT).
    :param content_type: Content-Type header.
    :return: HMAC-SHA256 signature string.
    """
    # Filter out 'sign' and 'access_token' if included
    filtered_params = {
        k: v for k, v in params.items() if k not in ("sign", "access_token")
    }

    # Sort and concatenate query parameters
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(filtered_params.items()))
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

    # Calculate signature
    sign = cal_sign(path, params, APP_SECRET)
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

    payload = {
        "create_time_from": create_time_from,
        "create_time_to": create_time_to,
        "page_size": page_size,
    }

    async with aiohttp.ClientSession() as session:
        while True:
            # Prepare query parameters (excluding sign)
            params = {
                "shop_id": shop_id,
                "app_key": APP_KEY,
                "timestamp": int(time.time()),
                "access_token": access_token,
            }

            # Calculate the signature using your cal_sign
            params["sign"] = cal_sign(
                path=path,
                params=params,
                app_secret=APP_SECRET,
                body=json.dumps(payload).encode("utf-8"),
            )

            # Make POST request
            async with session.post(base_url, params=params, json=payload) as response:
                data = await response.json()
                logging.info(f"Response: {data}")

                if data.get("code") == 0:
                    orders = data["data"]["order_list"]
                    all_orders.extend(orders)

                    # Paging
                    if data["data"].get("more"):
                        cursor = data["data"].get("next_cursor", "")
                        payload["cursor"] = cursor
                        logging.info(f"More orders available, next cursor: {cursor}")
                    else:
                        logging.info("No more orders available.")
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"shop_id": shop_id, "total": len(all_orders), "orders": all_orders}


async def get_order_detail(
    access_token: str,
    shop_id: str,
    order_id_list: list[str],
) -> Dict[str, Any]:
    """
    Fetch detailed information for a list of orders from TikTok Shop API.
    """
    path = "/api/orders/detail/query"
    base_url = f"{BASE_URL}{path}"

    payload = {"order_id_list": order_id_list}

    async with aiohttp.ClientSession() as session:
        # Prepare query parameters (excluding sign)
        params = {
            "shop_id": shop_id,
            "app_key": APP_KEY,
            "timestamp": int(time.time()),
            "access_token": access_token,
        }

        # Calculate the signature using your cal_sign
        params["sign"] = cal_sign(
            path=path,
            params=params,
            app_secret=APP_SECRET,
            body=json.dumps(payload).encode("utf-8"),
        )

        # Make POST request
        async with session.post(base_url, params=params, json=payload) as response:
            data = await response.json()
            logging.info(f"Response: {data}")

            if data.get("code") == 0:
                return data["data"]["order_list"]
            else:
                raise Exception(f"Error: {data.get('message')}")


async def main():
    shop_info = await get_authorized_shop(ACCESS_TOKEN)
    logging.info("Shop Info: %s", json.dumps(shop_info, indent=2))

    orders = await get_order_list(
        access_token=ACCESS_TOKEN,
        shop_id=shop_info["id"],
        create_time_from=int(time.time()) - 86400,  # Last 24 hours
        create_time_to=int(time.time()),
    )
    logging.info(
        "Orders: %s, Length: %d", json.dumps(orders, indent=2), len(orders["orders"])
    )

    # Fetch order details for the first order
    order_id_list = [order["order_id"] for order in orders["orders"][:1]]
    order_details = await get_order_detail(
        access_token=ACCESS_TOKEN,
        shop_id=shop_info["id"],
        order_id_list=order_id_list,
    )
    logging.info("Order Details: %s", json.dumps(order_details, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
