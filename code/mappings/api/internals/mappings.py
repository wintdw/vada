import logging
from typing import Dict
from api.connectors.async_es import AsyncESProcessor
from api.connectors.crm import CRMAPI


class MappingsProcessor:
    def __init__(
        self,
        es_conf_dict: Dict,
        crm_conf_dict: Dict,
    ):
        self.es = AsyncESProcessor(
            es_conf_dict["url"], es_conf_dict["user"], es_conf_dict["passwd"]
        )
        # crm_conf_dict = {"auth": {"username": "", "password": ""}, "baseurl": ""}
        self.crm = CRMAPI(crm_conf_dict["baseurl"])
        self.crm_user = crm_conf_dict["auth"]["username"]
        self.crm_passwd = crm_conf_dict["auth"]["password"]

    async def auth_crm(self):
        # Auth & reauth
        if not await self.crm.is_auth():
            await self.crm.auth(self.crm_user, self.crm_passwd)

    async def get_mappings(self, index_name: str) -> Dict:
        es_mapping = await self.es.get_es_index_mapping(index_name)
        mappings = es_mapping[index_name]["mappings"]

        return mappings

    async def set_mappings(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mappings: Dict,
    ):
        response_json = await self.crm.set_mappings(
            user_id, index_name, index_friendly_name, mappings
        )
        return response_json

    async def copy_mappings(
        self, user_id: str, index_name: str, index_friendly_name: str = None
    ) -> Dict:
        await self.auth_crm()

        if not index_friendly_name:
            index_friendly_name = index_name

        index_mappings = await self.get_mappings(index_name)
        response_json = await self.set_mappings(
            user_id, index_name, index_friendly_name, index_mappings
        )
        logging.info(
            "Mappings set for user: %s, index: %s, mappings: %s",
            user_id,
            index_name,
            index_mappings,
        )

        return response_json

    async def add_user(
        self,
        user_name: str,
        user_email: str,
        user_passwd: str,
        index_name: str,
        index_friendly_name: str = None,
    ) -> Dict:
        await self.auth_crm()

        if not index_friendly_name:
            index_friendly_name = index_name

        index_mappings = await self.get_mappings(index_name)
        await self.crm.add_user(
            user_name,
            user_email,
            user_passwd,
            index_name,
            index_friendly_name,
            index_mappings,
        )
