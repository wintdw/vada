import logging
from typing import Dict
from aiohttp import ClientSession, ClientResponse, BasicAuth


class AsyncESProcessor:
    def __init__(self, es_baseurl: str, es_user: str, es_pass: str):
        self.es_baseurl = es_baseurl
        self.auth = BasicAuth(es_user, es_pass)
        self.session = None

    async def _create_session(self):
        """Create a new session."""
        if not self.session:
            self.session = ClientSession()

    async def check_es_health(self) -> ClientResponse:
        """Check the health of the Elasticsearch cluster."""
        es_url = f"{self.es_baseurl}/_cluster/health"

        await self._create_session()
        async with self.session.get(es_url, auth=self.auth) as response:
            if response.status != 200:
                logging.error(
                    f"Failed to get health info. Status Code: {response.status} - {await response.text()}"
                )

            logging.debug(f"Cluster health: {await response.text()}")
            return response

    async def get_es_index_mapping(self, index_name: str) -> Dict:
        """Get the mapping of a specific Elasticsearch index."""
        es_url = f"{self.es_baseurl}/{index_name}/_mapping"

        await self._create_session()
        async with self.session.get(es_url, auth=self.auth) as response:
            if response.status != 200:
                logging.error(
                    f"Failed to get mappings. Status Code: {response.status} - {await response.text()}"
                )

            mappings = await response.json()
            logging.info(f"Retrieved mappings for index: {index_name}")
            return mappings

    async def send_to_es(
        self, index_name: str, doc_id: str, msg: Dict
    ) -> ClientResponse:
        """Send data to a specific Elasticsearch index."""
        es_url = f"{self.es_baseurl}/{index_name}/_doc/{doc_id}"

        await self._create_session()
        async with self.session.put(es_url, json=msg, auth=self.auth) as response:
            logging.info(f"Index: {index_name} Document ID: {doc_id}")
            if response.status == 201:
                logging.info("Document created successfully.")
            elif response.status == 200:
                logging.info("Document updated successfully.")
            else:
                logging.error(
                    f"Failed to send data to Elasticsearch. Status code: {response.status} - {await response.text()}"
                )

            return response

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
