import aiohttp # type: ignore
import logging
from typing import List, Dict
from model.settings import settings

async def get_shop_info(api_token: str) -> List[Dict]:
    """
    Fetch shop information from Pancake POS API.
    """
    url = f"{settings.PCP_BASE_URL}/shops"
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "api_token": api_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("shops", [])
            else:
                logging.error(f"Failed to fetch shop info: {response.status} {await response.text()}")
                return []