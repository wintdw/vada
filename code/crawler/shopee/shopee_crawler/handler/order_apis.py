import aiohttp  # type: ignore
import time
import json
import logging
from typing import Dict, Any, List, Optional
from utils import generate_partner_signature

from model.setting import settings

async def get_order_list(
    access_token: str,
    shop_id: int,
    create_time_from: int,
    create_time_to: int,
    page_size: int = 100,
) -> Dict[str, Any]:
    path = "/api/v2/order/get_order_list"
    base_url = f"{settings.SHOPEE_OPEN_API_BASEURL}{path}"

    all_orders = []
    cursor = ""

    async with aiohttp.ClientSession() as session:
        while True:
            timestamp = int(time.time())

            query = {
                "partner_id": settings.SHOPEE_PARTNER_ID,
                "timestamp": timestamp,
                "access_token": access_token,
                "shop_id": shop_id,
            }

            sign = generate_partner_signature(
                path=path,
                timestamp=timestamp,
                access_token=access_token,
                shop_id=shop_id
            )
            query["sign"] = sign

            body = {
                "time_range_field": "create_time",
                "time_from": create_time_from,
                "time_to": create_time_to,
                "page_size": page_size,
            }

            if cursor:
                body["cursor"] = cursor

            async with session.post(
                base_url, params=query, json=body, headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                logging.info(f"[Shopee] Order List Response: {data}")

                if data.get("error") == 0:
                    orders = data["response"]["order_list"]
                    all_orders.extend(orders)
                    cursor = data["response"].get("next_cursor")
                    if not cursor:
                        break
                else:
                    raise Exception(f"[Shopee] API error: {data.get('message')}")

    return {"total": len(all_orders), "orders": all_orders}


async def get_order_detail(
    access_token: str,
    shop_id: int,
    order_sn_list: List[str],
) -> Dict[str, Any]:
    path = "/api/v2/order/get_order_detail"
    base_url = f"{settings.SHOPEE_OPEN_API_BASEURL}{path}"
    timestamp = int(time.time())

    query = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
    }

    sign = generate_partner_signature(
        path=path,
        timestamp=timestamp,
        access_token=access_token,
        shop_id=shop_id
    )
    query["sign"] = sign

    body = {
        "order_sn_list": order_sn_list
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            base_url, params=query, json=body, headers={"Content-Type": "application/json"}
        ) as response:
            data = await response.json()
            if data.get("error") == 0:
                return data["response"]
            else:
                raise Exception(f"[Shopee] Order detail error: {data.get('message')}")


async def get_price_detail(
    access_token: str,
    shop_id: int,
    order_sn: str,
) -> Dict[str, Any]:
    path = f"/api/v2/order/get_invoice_info"
    base_url = f"{settings.SHOPEE_OPEN_API_BASEURL}{path}"
    timestamp = int(time.time())

    query = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
    }

    sign = generate_partner_signature(
        path=path,
        timestamp=timestamp,
        access_token=access_token,
        shop_id=shop_id
    )
    query["sign"] = sign

    body = {
        "order_sn": order_sn
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            base_url, params=query, json=body, headers={"Content-Type": "application/json"}
        ) as response:
            data = await response.json()
            if data.get("error") == 0:
                return data["response"]
            else:
                raise Exception(f"[Shopee] Price detail error: {data.get('message')}")
