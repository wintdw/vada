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
    order_status: Optional[str] = None,
    response_optional_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get order list from Shopee API
    
    Args:
        access_token: Shop access token
        shop_id: Shop ID
        create_time_from: Start time (Unix timestamp)
        create_time_to: End time (Unix timestamp)
        page_size: Number of orders per page (max 100)
        order_status: Filter by order status (UNPAID, READY_TO_SHIP, PROCESSED, SHIPPED, COMPLETED, IN_CANCEL, CANCELLED, INVOICE_PENDING)
        response_optional_fields: Optional fields to include in response
    """
    path = "/api/v2/order/get_order_list"
    base_url = f"{settings.SHOPEE_OPEN_API_BASEURL}{path}"

    all_orders = []
    cursor = ""
    
    # Default optional fields if not provided
    if response_optional_fields is None:
        response_optional_fields = [
            "order_status"
        ]

    async with aiohttp.ClientSession() as session:
        while True:
            timestamp = int(time.time())
            
            logging.info(f"[Shopee] Getting order list from {path}")

            # All parameters go in query string for GET request
            query = {
                "partner_id": settings.SHOPEE_PARTNER_ID,
                "timestamp": timestamp,
                "access_token": access_token,
                "shop_id": shop_id,
                "time_range_field": "create_time",
                "time_from": create_time_from,
                "time_to": create_time_to,
                "page_size": page_size,
            }

            # Optional parameters
            if cursor:
                query["cursor"] = cursor
            
            if response_optional_fields:
                query["response_optional_fields"] = ",".join(response_optional_fields)

            sign = generate_partner_signature(
                path=path,
                timestamp=timestamp,
                access_token=access_token,
                shop_id=shop_id
            )
            query["sign"] = sign

            logging.info(f"[Shopee] Request URL: {base_url}")
            logging.info(f"[Shopee] Query params: {json.dumps(query, indent=2)}")

            async with session.get(base_url, params=query) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"[Shopee] HTTP {response.status}: {error_text}")
                    raise Exception(f"HTTP {response.status}: {error_text}")
                
                try:
                    data = await response.json()
                except Exception as e:
                    error_text = await response.text()
                    logging.error(f"[Shopee] Failed to parse JSON: {error_text}")
                    raise Exception(f"Failed to parse response: {str(e)}")
                
                logging.info(f"[Shopee] Order List Response: {json.dumps(data, indent=2)}")

                if data["error"] == "":
                    orders = data["response"]["order_list"]
                    all_orders.extend(orders)
                    cursor = data["response"].get("next_cursor")
                    if not cursor:
                        break
                else:
                    error_msg = data.get("message", "Unknown error")
                    logging.error(f"[Shopee] API error: {error_msg}")
                    raise Exception(f"[Shopee] API error: {error_msg}")

    logging.info(f"[Shopee] Total orders retrieved: {len(all_orders)}")
    return {"total": len(all_orders), "orders": all_orders}


async def get_order_detail(
    access_token: str,
    shop_id: int,
    order_sn_list: List[str],
    response_optional_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get order detail from Shopee API
    
    Args:
        access_token: Shop access token
        shop_id: Shop ID
        order_sn_list: List of order serial numbers (max 50 orders)
        response_optional_fields: Optional fields to include in response
    """
    path = "/api/v2/order/get_order_detail"
    base_url = f"{settings.SHOPEE_OPEN_API_BASEURL}{path}"
    timestamp = int(time.time())

    # Default optional fields if not provided
    if response_optional_fields is None:
        response_optional_fields = [
            "buyer_user_id",
            "buyer_username", 
            "estimated_shipping_fee",
            "recipient_address",
            "actual_shipping_fee",
            "goods_to_declare",
            "note",
            "note_update_time",
            "item_list",
            "pay_time",
            "dropshipper",
            "dropshipper_phone",
            "split_up",
            "buyer_cancel_reason",
            "cancel_by",
            "cancel_reason",
            "actual_shipping_fee_confirmed",
            "buyer_cpf_id",
            "fulfillment_flag",
            "pickup_done_time",
            "package_list",
            "shipping_carrier",
            "payment_method",
            "total_amount",
            "invoice_data"
        ]

    # All parameters go in query string for GET request
    query = {
        "partner_id": settings.SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "order_sn_list": ",".join(order_sn_list),  # Comma-separated list
    }

    # Add response_optional_fields as comma-separated string
    if response_optional_fields:
        query["response_optional_fields"] = ",".join(response_optional_fields)

    sign = generate_partner_signature(
        path=path,
        timestamp=timestamp,
        access_token=access_token,
        shop_id=shop_id
    )
    query["sign"] = sign

    logging.info(f"[Shopee] Getting order detail for {len(order_sn_list)} orders")
    logging.info(f"[Shopee] Request URL: {base_url}")
    logging.info(f"[Shopee] Query params: {json.dumps(query, indent=2)}")

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=query) as response:
            logging.info(f"[Shopee] Order detail response status: {response.status}")
            
            if response.status != 200:
                error_text = await response.text()
                logging.error(f"[Shopee] HTTP {response.status}: {error_text}")
                raise Exception(f"HTTP {response.status}: {error_text}")
            
            try:
                data = await response.json()
            except Exception as e:
                error_text = await response.text()
                logging.error(f"[Shopee] Failed to parse JSON: {error_text}")
                raise Exception(f"Failed to parse response: {str(e)}")
            
            logging.info(f"[Shopee] Order detail response: {json.dumps(data, indent=2)}")
            
            if data["error"] == "":
                return data["response"]
            else:
                error_msg = data.get("message", "Unknown error")
                logging.error(f"[Shopee] Order detail API error: {error_msg}")
                raise Exception(f"[Shopee] Order detail error: {error_msg}")


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
