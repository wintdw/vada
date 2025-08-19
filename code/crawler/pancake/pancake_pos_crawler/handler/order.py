import aiohttp # type: ignore
import logging
from model.settings import settings
from datetime import datetime

async def get_pancake_orders(shop_id: str, api_key: str, from_date: str, to_date: str) -> list:
    """
    Fetch orders from Pancake POS API filtered by start and end date, with paging support.
    """
    url = f"{settings.PCP_BASE_URL}/shops/{shop_id}/orders"
    headers = {
        "Content-Type": "application/json",
    }
    
    # Convert dates to Unix timestamps
    from_timestamp = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
    to_timestamp = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())

    all_orders = []
    page_number = 1

    while True:
        params = {
            "api_key": api_key,
            "startDateTime": from_timestamp,
            "endDateTime": to_timestamp,
            "page": page_number,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    orders = data.get("data", [])
                    
                    # Remove 'items.variation_info.barcode', 'items.variation_info.display_id', and 'tags' fields from orders
                    for order in orders:
                        for item in order.get("items", []):
                            if "variation_info" in item:
                                if "barcode" in item["variation_info"]:
                                    del item["variation_info"]["barcode"]
                                if "display_id" in item["variation_info"]:
                                    del item["variation_info"]["display_id"]
                        if "tags" in order:
                            del order["tags"]
                        if "customer" in order and "notes" in order["customer"] and "removed_at" in order["customer"]["notes"]:
                            del order["customer"]["notes"]["removed_at"]

                    all_orders.extend(orders)

                    total_pages = data.get("total_pages", 1)
                    if page_number >= total_pages:
                        break
                    page_number += 1
                else:
                    logging.error(f"Failed to fetch orders: {response.status} {await response.text()}")
                    break

    return all_orders