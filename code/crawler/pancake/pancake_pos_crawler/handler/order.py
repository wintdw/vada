import aiohttp # type: ignore
import logging
from model.settings import settings

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