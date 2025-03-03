import logging
from typing import Dict
from libs.connectors.async_es import AsyncESProcessor
from libs.connectors.crm import CRMAPI


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

    async def close(self):
        await self.es.close()
        await self.crm.close()

    async def check_health(self) -> Dict:
        es_resp = await self.es.check_health()
        crm_resp = await self.crm.check_health()

        return {"es": es_resp, "crm": crm_resp}

    async def auth_crm(self):
        # Auth & reauth
        if not await self.crm.is_auth():
            await self.crm.auth(self.crm_user, self.crm_passwd)

    async def get_es_mappings(self, index_name: str) -> Dict:
        es_mapping = await self.es.get_mappings(index_name)
        if index_name not in es_mapping:
            index_name = next(iter(es_mapping))  # Get the first key

        return es_mapping[index_name]["mappings"]

    async def set_es_mappings(self, index_name: str, mappings: Dict):
        if not await self.es.check_index_exists(index_name):
            await self.es.set_mappings(index_name, mappings)

    async def set_crm_mappings(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str,
        mappings: Dict,
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ):
        await self.auth_crm()
        return await self.crm.set_mappings(
            user_id,
            index_name,
            index_friendly_name,
            mappings,
            id_field,
            agg_field,
            time_field,
        )

    async def copy_mappings(
        self,
        user_id: str,
        index_name: str,
        index_friendly_name: str = "",
        id_field: str = "",
        agg_field: str = "",
        time_field: str = "",
    ) -> Dict:
        index_mappings = await self.get_es_mappings(index_name)
        logging.info(
            "Mappings set for user: %s, index: %s, mappings: %s",
            user_id,
            index_name,
            index_mappings,
        )

        return await self.set_crm_mappings(
            user_id,
            index_name,
            index_friendly_name,
            index_mappings,
            id_field,
            agg_field,
            time_field,
        )

    async def add_user(
        self,
        user_name: str,
        user_email: str,
        user_passwd: str,
    ) -> Dict:

        await self.auth_crm()
        return await self.crm.add_user(user_name, user_email, user_passwd)
