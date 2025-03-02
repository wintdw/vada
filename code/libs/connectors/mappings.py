import aiohttp  # type: ignore
from typing import Dict

from libs.utils.common import friendlify_index_name


class MappingsClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def check_health(self) -> Dict:
        url = f"{self.base_url}/health"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return {"status": response.status, "detail": await response.json()}
        except Exception as e:
            return {
                "status": 500,
                "detail": f"Mappings service is down - {await response.text()}",
            }

    async def create_mappings(
        self, user_id: str, index_name: str, index_friendly_name: str = None
    ) -> Dict:
        url = f"{self.base_url}/mappings"

        if not index_friendly_name:
            index_friendly_name = friendlify_index_name(index_name)

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return await response.json()

    async def create_crm_mappings(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mappings: Dict,
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ) -> Dict:
        url = f"{self.base_url}/crm/mappings"

        if index_friendly_name == index_name:
            index_friendly_name = friendlify_index_name(index_name)

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
            "mappings": mappings,
            "id_field": id_field,
            "agg_field": agg_field,
            "time_field": time_field,
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=payload) as response:
                return await response.json()
