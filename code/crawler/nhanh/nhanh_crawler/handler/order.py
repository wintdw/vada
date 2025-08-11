import json
import logging

from typing import Dict, List

from model.settings import settings
from .request import retry_post


async def get_orders(
    business_id: str,
    access_token: str,
    from_date: str,
    to_date: str,
) -> List[Dict]:
    url = f"{settings.NHANH_BASE_URL}/order/index"
    page = 1
    orders = []

    logging.info(f"[{business_id}] Fetching orders from {from_date} to {to_date}...")
    while True:
        payload = {"fromDate": from_date, "toDate": to_date, "page": page}

        response_data = await retry_post(
            url=url,
            business_id=business_id,
            access_token=access_token,
            payload=json.dumps(payload),
        )

        if not response_data:
            logging.warning(f"[{business_id}] No response for page {page}")
            break

        page_orders = response_data.get("orders", {})
        orders.extend(page_orders.values())

        current_page = response_data.get("page", page)
        total_pages = response_data.get("totalPages", current_page)

        if current_page >= total_pages:
            break

        page += 1

    logging.info(f"[{business_id}] Total orders fetched: {len(orders)}")

    return orders
