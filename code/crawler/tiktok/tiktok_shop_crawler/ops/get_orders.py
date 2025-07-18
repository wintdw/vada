import json
import aiohttp  # type: ignore
import asyncio
import time
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional, List


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
    shop_cipher: str,
    create_time_ge: int,
    create_time_lt: int,
    page_size: int = 100,
) -> Dict[str, Any]:
    """
    Fetch the order list from the new TikTok Shop API (202309 version) with paging.
    Also enrich each line_item with product_detail.
    """
    api_version = "202309"
    path = f"/order/{api_version}/orders/search"
    base_url = f"{BASE_URL}{path}"

    all_orders = []
    page_token = ""

    async with aiohttp.ClientSession() as session:
        while True:
            timestamp = int(time.time())

            # Prepare query parameters
            query_params = {
                "app_key": APP_KEY,
                "shop_cipher": shop_cipher,
                "timestamp": timestamp,
                "page_size": page_size,
            }

            if page_token:
                query_params["page_token"] = page_token

            # JSON body (filter conditions)
            payload = {
                "create_time_ge": create_time_ge,
                "create_time_lt": create_time_lt,
            }

            # Sign calculation
            query_params["sign"] = cal_sign(
                path=path,
                params=query_params,
                app_secret=APP_SECRET,
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
            )

            headers = {
                "x-tts-access-token": access_token,
                "content-type": "application/json",
            }

            async with session.post(
                base_url, params=query_params, json=payload, headers=headers
            ) as response:
                data = await response.json()
                # logging.debug(f"Response: {data}")

                if data.get("code") == 0:
                    orders = data["data"]["orders"]

                    # Enrich each line_item with product_detail
                    for order in orders:
                        line_items = order.get("line_items", [])
                        for item in line_items:
                            product_id = item.get("product_id")
                            if product_id:
                                # Fetch product_detail for each product_id
                                product_detail = await get_product_detail(
                                    access_token=access_token,
                                    shop_cipher=shop_cipher,
                                    product_id=product_id,
                                )
                                item["product_detail"] = product_detail

                    all_orders.extend(orders)

                    page_token = data["data"].get("next_page_token")
                    if page_token:
                        logging.info(
                            f"More orders available, next page_token: {page_token}"
                        )
                    else:
                        logging.info("No more orders available.")
                        break
                else:
                    raise Exception(f"Error: {data.get('message')}")

    return {"total": len(all_orders), "orders": all_orders}


async def get_price_detail(
    access_token: str,
    shop_cipher: str,
    order_id: str,
) -> Dict:
    """
    Fetch price detail of a specific order using TikTok Shop API (202407 version).
    """
    api_version = "202407"
    path = f"/order/{api_version}/orders/{order_id}/price_detail"
    base_url = f"{BASE_URL}{path}"
    timestamp = int(time.time())

    # Prepare query parameters
    query_params = {
        "app_key": APP_KEY,
        "timestamp": timestamp,
        "shop_cipher": shop_cipher,
    }

    # Sign calculation (GET request, no body)
    query_params["sign"] = cal_sign(
        path=path,
        params=query_params,
        app_secret=APP_SECRET,
        content_type="application/json",
    )

    headers = {
        "x-tts-access-token": access_token,
        "content-type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            base_url, params=query_params, headers=headers
        ) as response:
            data = await response.json()

            if data.get("code") == 0:
                return data["data"]
            else:
                logging.error(
                    f"Failed to fetch price detail for order {order_id}: {data}",
                    exc_info=True,
                )
                raise Exception(f"Error: {data.get('message')}")


async def get_product_detail(
    access_token: str, shop_cipher: str, product_id: str
) -> Dict:
    """
    Retrieve all properties of a product (DRAFT, PENDING, or ACTIVATE status) from TikTok Shop API (202309 version).
    """
    api_version = "202309"
    path = f"/product/{api_version}/products/{product_id}"
    base_url = f"{BASE_URL}/{path}"
    timestamp = int(time.time())

    # Prepare query parameters
    query_params = {
        "app_key": APP_KEY,
        "timestamp": timestamp,
        "shop_cipher": shop_cipher,
    }

    # Sign calculation (GET request, no body)
    query_params["sign"] = cal_sign(
        path=path,
        params=query_params,
        app_secret=APP_SECRET,
        content_type="application/json",
    )

    headers = {
        "x-tts-access-token": access_token,
        "content-type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            base_url, params=query_params, headers=headers
        ) as response:
            data = await response.json()

            if data.get("code") == 0:
                return data["data"]
            else:
                logging.error(
                    f"Failed to fetch product detail for product {product_id}: {data}",
                    exc_info=True,
                )
                raise Exception(f"Error: {data.get('message')}")


async def main():
    shop_info = await get_authorized_shop(ACCESS_TOKEN)
    logging.info("Shop Info: %s", json.dumps(shop_info, indent=2))

    orders = await get_order_list(
        access_token=ACCESS_TOKEN,
        shop_cipher=shop_info["cipher"],
        create_time_ge=int(time.time()) - 600,  # Last 10m
        create_time_lt=int(time.time()),
    )
    # logging.info(
    #     "Orders: %s, Length: %d", json.dumps(orders, indent=2), len(orders["orders"])
    # )

    for order in orders["orders"]:
        line_items = order.get("line_items", [])
        if line_items:
            for item in line_items:
                product_id = item.get("product_id")
                if product_id:
                    product_detail = await get_product_detail(
                        access_token=ACCESS_TOKEN,
                        shop_cipher=shop_info["cipher"],
                        product_id=product_id,
                    )
                    item["product_detail"] = product_detail

    # Now 'orders' contains all product_details in their line_items
    # You can return, print, or process it as needed:
    print(json.dumps(orders["orders"][-1], indent=2))
    return orders  # If inside a function


if __name__ == "__main__":
    asyncio.run(main())
