import aiohttp  # type: ignore
import logging
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
        except Exception:
            return {
                "status": 500,
                "detail": f"Mappings service is down - {await response.text()}",
            }

    async def create_user(
        self, user_name: str, user_email: str, user_passwd: str
    ) -> Dict:
        url = f"{self.base_url}/users"
        payload = {
            "user_name": user_name,
            "user_email": user_email,
            "user_passwd": user_passwd,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response_data = await response.json()

                if response.status >= 400:
                    logging.error(response_data["detail"])
                    raise Exception(response_data["detail"])

                msg = f"User created: {user_name}, email: {user_email}"
                logging.info(msg)

                return response_data["detail"]

    async def copy_mappings(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str = "",
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ) -> Dict:
        url = f"{self.base_url}/mappings"

        if not index_friendly_name or index_friendly_name == index_name:
            index_friendly_name = friendlify_index_name(index_name)

        payload = {
            "user_id": user_id,
            "index_name": index_name,
            "index_friendly_name": index_friendly_name,
            "id_field": id_field,
            "agg_field": agg_field,
            "time_field": time_field,
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

    async def create_es_mappings(
        self,
        index_name: str,
        mappings: Dict,
    ) -> Dict:
        """Create Elasticsearch mappings for an index

        Args:
            index_name: Name of the index
            mappings: Dictionary containing the ES mappings

        Returns:
            Dict containing the response from the mappings service
        """
        url = f"{self.base_url}/es/mappings"

        payload = {"index_name": index_name, "mappings": mappings}

        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=payload) as response:
                response_data = await response.json()

                if response.status >= 400:
                    logging.error(f"Error creating ES mappings: {response_data}")
                    raise Exception(response_data["detail"])

                msg = f"ES Mappings created for index: {index_name}"
                logging.info(msg)

                return response_data
