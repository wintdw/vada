import logging
import aiohttp  # type: ignore
from typing import Dict, Tuple
from datetime import datetime
from dateutil.relativedelta import relativedelta  # type: ignore
from fastapi import HTTPException  # type: ignore

from libs.security.jwt import verify_jwt


class CRMAPI:
    def __init__(self, baseurl: str):
        self.baseurl = baseurl
        self.headers = {}
        self.session = None

    async def _get_access_token(self, username: str, password: str) -> str:
        """
        Function to call the login API and extract the access token.

        Returns:
            str: The access token from the response.
        """
        url = f"{self.baseurl}/auth/login"
        payload = {"username": username, "password": password}
        headers = {"Content-Type": "application/json"}

        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                access_token = data.get("access_token")
                logging.debug("Access token retrieved: %s", access_token)
                return access_token
            else:
                logging.error(
                    "Failed to retrieve access token, status code: %d, detail: %s",
                    response.status,
                    await response.text(),
                )
                return None

    async def close(self):
        if self.session:
            await self.session.close()
        if "Authorization" in self.headers:
            self.headers.pop("Authorization", None)

    async def auth(self, user: str, passwd: str) -> str:
        """
        Function to init session and authenticate the user
        and set the JWT token in headers.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        jwt_token = await self._get_access_token(user, passwd)
        if jwt_token:
            self.headers["Authorization"] = f"Bearer {jwt_token}"
        else:
            raise Exception(f"Failed to authenticate user: {user}")

    async def is_auth(self) -> bool:
        """
        Function to check if the user is authenticated and if the JWT is still valid.
        """
        if "Authorization" not in self.headers:
            return False

        token = self.headers["Authorization"].split(" ")[1]
        try:
            verify_jwt(token)
            return True
        except HTTPException as e:
            logging.debug("JWT verification failed: %s", e.detail)
            return False

    async def check_health(self) -> Dict:
        url = f"{self.baseurl}/ping"

        async with self.session.get(url, headers=self.headers) as response:
            return response.status, await response.json()

    async def check_index_created(self, index: str) -> Dict:
        url = f"{self.baseurl}/v1/querybuilder/master_file/treebeard/{index}"

        async with self.session.get(url, headers=self.headers) as response:
            res = await response.json()
            # Not found
            if "index" not in res:
                return {}
            return res

    async def set_mappings(
        self, user_id: str, index_name: str, index_friendly_name: str, mappings: Dict
    ) -> Tuple[int, Dict]:
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
        async with self.session.put(
            url, headers=self.headers, json=post_data
        ) as response:
            return response.status, await response.json()

    async def add_user(
        self,
        user_name: str,
        user_email: str,
        user_passwd: str,
    ) -> Tuple[int, Dict]:
        url = f"{self.baseurl}/v1/adm/users"

        now = datetime.now()
        months_ago = now - relativedelta(months=6)

        post_data = {
            "email": user_email,
            "username": user_name,
            "password": user_passwd,
            "permission": "admin",
            "configuration": {
                "default_values": {
                    "default_time_left": now.strftime("%Y-%m-%d"),
                    "default_time_right": months_ago.strftime("%Y-%m-%d"),
                }
            },
        }

        async with self.session.post(
            url, headers=self.headers, json=post_data
        ) as response:
            return response.status, await response.json()
