import aiohttp
import time
import logging
from typing import Dict, Any
from .order import get_pancake_orders
from .shop import get_shop_info

def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def convert_keys_to_snake_case(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            camel_to_snake(k): convert_keys_to_snake_case(v) for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_keys_to_snake_case(item) for item in obj]
    else:
        return obj

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