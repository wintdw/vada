import aiohttp
import time
import logging
from typing import Dict, Any
from .shop import get_shop_info
from .utils import convert_keys_to_snake_case

async def get_pancake_orders(shop_id: str, api_token: str, from_date: str, to_date: str) -> list:
    """
    Fetch orders from Pancake POS API filtered by start and end date.
    """
    url = f"{settings.PCP_BASE_URL}/shops/{shop_id}/orders"
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "api_token": api_token,
        "start_date": from_date,
        "end_date": to_date,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("orders", [])
            else:
                logging.error(f"Failed to fetch orders: {response.status} {await response.text()}")
                return []

async def crawl_pancake_orders(api_token: str, from_date: str, to_date: str) -> list:
    """
    Crawl orders for all shops associated with the API token.
    """
    start_time = time.time()

    # Fetch shop information
    logging.info("Fetching shop information...")
    shops = await get_shop_info(api_token)

    if not shops:
        logging.error("No shops found. Aborting crawl.")
        return []

    all_orders = []

    for shop in shops:
        shop_id = shop.get("id")
        if not shop_id:
            logging.warning("Shop ID not found for a shop. Skipping...")
            continue

        logging.info(f"Fetching orders for shop ID {shop_id}...")
        orders = await get_pancake_orders(shop_id, api_token, from_date, to_date)

        # Convert all order fields to snake_case
        orders = [convert_keys_to_snake_case(order) for order in orders]
        all_orders.extend(orders)

    logging.debug(f"Total orders: {len(all_orders)} in {time.time() - start_time} seconds")
    return all_orders