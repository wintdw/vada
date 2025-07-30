import json
import time
import aiohttp  # type: ignore
import logging

from typing import Dict, List
from datetime import datetime

from model.settings import settings
from .persist import enrich_report, send_batch


async def get_access_token(access_code: str) -> Dict:
    """
    API documentation at https://open.nhanh.vn/api/oauth/access_token
    """
    url = f"{settings.NHANH_BASE_URL}/oauth/access_token"
    oauth_version = "2.0"
    app_id = settings.NHANH_APP_ID
    secret_key = settings.NHANH_SECRET_KEY

    # Prepare the request payload
    payload = {
        "appId": app_id,
        "version": oauth_version,
        "secretKey": secret_key,
        "accessCode": access_code,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    # Log the error response for debugging
                    error_text = await response.text()
                    logging.debug(
                        f"Error getting access token. Status: {response.status}, Response: {error_text}",
                        exc_info=True,
                    )
                    return {}

    except Exception as e:
        logging.debug(
            f"Unexpected error while getting access token: {e}", exc_info=True
        )
        raise


async def get_product_detail(
    business_id: str,
    access_token: str,
    product_id: str,
) -> Dict:
    url = f"{settings.NHANH_BASE_URL}/product/detail"
    oauth_version = "2.0"

    headers = {"Accept": "application/json"}
    payload = {
        "version": oauth_version,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
        "data": product_id,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {}).get(product_id, {})
                else:
                    error_text = await response.text()
                    logging.debug(
                        f"Error getting product detail. Status: {response.status}, Response: {error_text}",
                        exc_info=True,
                    )
                    return {}
    except Exception as e:
        logging.debug(
            f"Unexpected error while getting product detail: {e}", exc_info=True
        )
        raise


async def get_orders(
    business_id: str, access_token: str, from_date: str, to_date: str, page: int = 1
):
    url = f"{settings.NHANH_BASE_URL}/order/index"
    oauth_version = "2.0"
    headers = {"Accept": "application/json"}
    payload = {"fromDate": from_date, "toDate": to_date, "page": page}
    data = {
        "version": oauth_version,
        "appId": settings.NHANH_APP_ID,
        "businessId": business_id,
        "accessToken": access_token,
        "data": json.dumps(payload),
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {})
                else:
                    error_text = await response.text()
                    logging.debug(
                        f"Error getting orders. Status: {response.status}, Response: {error_text}"
                    )
                    return {}
    except aiohttp.ClientError as e:
        logging.debug(f"HTTP client error while getting orders: {e}")
        raise
    except Exception as e:
        logging.debug(f"Unexpected error while getting orders: {e}")
        raise


async def crawl_nhanh_data(
    index_name: str, business_id: str, access_token: str, from_date: str, to_date: str
) -> List[Dict]:
    try:
        start_time = time.time()

        detailed_data = []
        total_pages = 1
        page = 1

        while page <= total_pages:
            logging.debug(
                f"Fetching page {page} for orders from {from_date} to {to_date}"
            )
            # Get orders for the current page
            data = await get_orders(business_id, access_token, from_date, to_date, page)

            total_pages = data.get("totalPages", 1)
            orders = data.get("orders", {})

            # Convert keys from camelCase to snake_case
            def camel_to_snake(name):
                import re

                s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
                return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

            def convert_keys_to_snake_case(data):
                if isinstance(data, dict):
                    return {
                        camel_to_snake(k): convert_keys_to_snake_case(v)
                        for k, v in data.items()
                    }
                elif isinstance(data, list):
                    return [convert_keys_to_snake_case(item) for item in data]
                else:
                    return data

            for order_id, order in orders.items():
                # Map saleChannel to saleChannelName
                sale_channel_mapping = {
                    "1": "Admin",
                    "2": "Website",
                    "10": "API",
                    "20": "Facebook",
                    "21": "Instagram",
                    "41": "Lazada.vn",
                    "42": "Shopee.vn",
                    "43": "Sendo.vn",
                    "45": "Tiki.vn",
                    "46": "Zalo Shop",
                    "47": "1Landing.vn",
                    "48": "Tiktok Shop",
                    "49": "Zalo OA",
                    "50": "Shopee Chat",
                    "51": "Lazada Chat",
                }
                sale_channel = str(order.get("saleChannel", ""))
                order["saleChannelName"] = sale_channel_mapping.get(
                    sale_channel, "Unknown"
                )

                timestamp = int(
                    datetime.strptime(
                        order["createdDateTime"], "%Y-%m-%d %H:%M:%S"
                    ).timestamp()
                )
                doc_id = f"{order['id']}_{timestamp}"

                import_money = 0
                for product in order.get("products", []):
                    product_id = product.get("productId")
                    product["detail"] = await get_product_detail(
                        business_id, access_token, product_id
                    )
                    if product["detail"]["importPrice"]:
                        product["importMoney"] = int(
                            product["detail"]["importPrice"]
                        ) * int(product["quantity"])
                        import_money += product["importMoney"]
                    time.sleep(0.2)  # avoid API overuse
                order["TotalImportMoney"] = import_money

                order_snake_case = convert_keys_to_snake_case(order)
                orders[order_id] = order_snake_case

                detailed_data.append(
                    enrich_report(order_snake_case, index_name, doc_id)
                )
            page += 1

        batch_size = 1000

        # Send reports in batches
        total_reports = len(detailed_data)
        logging.debug(f"Sending {total_reports} reports in batches of {batch_size}")

        for i in range(0, total_reports, batch_size):
            batch = detailed_data[i : i + batch_size]
            current_batch = i // batch_size + 1
            total_batches = (total_reports + batch_size - 1) // batch_size

            logging.debug(f"Sending batch {current_batch} of {total_batches}")
            await send_batch(index_name, batch)

            # Calculate total spending
            total_spend = sum(
                float(report.get("calcTotalMoney", 0)) for report in detailed_data
            )

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)

        return {
            "status": "success",
            "total_reports": total_reports,
            "total_spend": round(total_spend, 2),
            "date_start": from_date,
            "date_end": to_date,
            "execution_time": execution_time,
        }
    except Exception as e:
        logging.debug(f"Error while crawling Nhanh data: {e}")
        raise
