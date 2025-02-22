import re
import aiohttp  # type: ignore
from typing import Dict


class MappingsClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_mappings(
        self, user_id: str, index_name: str, index_friendly_name: str = None
    ) -> Dict:
        url = f"{self.base_url}/mappings"

        if not index_friendly_name:
            # pretify the index_friendly_name
            match = re.search(r"csv_(.*?)_csv", index_name)
            if match:
                index_friendly_name = f"CSV " + match.group(1)

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return await response.json()
