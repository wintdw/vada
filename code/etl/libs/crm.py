import aiohttp  # type: ignore

from libs.security import get_access_token


class CRMAPI:
    def __init__(self, baseurl: str):
        self.baseurl = baseurl

    def auth(self, auth_dict: dict) -> str:
        jwt_token = get_access_token(auth_dict["username"], auth_dict["password"])
        self.headers = {"Authorization": f"Bearer {jwt_token}"}

    async def check_index_created(self, index: str) -> dict:
        url = f"{self.baseurl}/v1/querybuilder/master_file/treebeard/{index}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                print(f"Request failed: {e}")
                return None

    async def set_mappings(
        self, user_id: str, index_name: str, index_friendly_name: str, mappings: dict
    ) -> dict:
        url = f"{self.baseurl}/v1/adm/indices"
        post_data = {"user_id": user_id}
        post_data["master_index"] = {
            "name": index_name,
            "friendly_name": index_friendly_name,
            "agg_field": "",
            "time_field": "",
            "deleted": False,
            "mappings": mappings,
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(
                    url, headers=self.headers, json=post_data
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                print(f"Request failed: {e}")
                return None
