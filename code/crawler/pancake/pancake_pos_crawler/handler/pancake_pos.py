import time
import logging
from .order import get_pancake_orders
from .shop import get_shop_info

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

        all_orders.extend(orders)

    logging.debug(f"Total orders: {len(all_orders)} in {time.time() - start_time} seconds")
    return all_orders