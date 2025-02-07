import logging
import json
from typing import Dict, List
from aiohttp import ClientSession, ClientResponse, BasicAuth  # type: ignore


class ESException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Status: {status_code} - Detail: {detail}")


class AsyncESProcessor:
    def __init__(self, es_baseurl: str, es_user: str, es_pass: str):
        self.es_baseurl = es_baseurl
        self.auth = BasicAuth(es_user, es_pass)
        self.session = None

    async def _create_session(self):
        """Create a new session."""
        if not self.session:
            self.session = ClientSession()

    async def check_health(self) -> ClientResponse:
        """Check the health of the Elasticsearch cluster."""
        es_url = f"{self.es_baseurl}/_cluster/health"

        await self._create_session()
        async with self.session.get(es_url, auth=self.auth) as response:
            if response.status != 200:
                logging.error(
                    "Failed to get health info. Status: %s - %s",
                    response.status,
                    await response.text(),
                )

            logging.debug("Cluster health: %s", await response.text())
            return response

    async def check_index_exists(self, index_name: str) -> bool:
        """Check if an Elasticsearch index exists."""
        es_url = f"{self.es_baseurl}/{index_name}"

        await self._create_session()
        async with self.session.head(es_url, auth=self.auth) as response:
            if response.status == 200:
                logging.info("Index exists: %s", index_name)
                return True
            elif response.status == 404:
                logging.info("Index does not exist: %s", index_name)
                return False
            else:
                logging.error(
                    "Failed to check index existence. Status: %s - %s",
                    response.status,
                    await response.text(),
                )
                raise ESException(response.status, await response.text())

    async def get_mappings(self, index_name: str) -> Dict:
        """Get the mapping of a specific Elasticsearch index."""
        es_url = f"{self.es_baseurl}/{index_name}/_mapping"

        await self._create_session()
        async with self.session.get(es_url, auth=self.auth) as response:
            if response.status != 200:
                logging.error(
                    "Failed to get mappings. Status: %s - %s",
                    response.status,
                    await response.text(),
                )
                raise ESException(response.status, await response.text())

            mappings = await response.json()
            logging.info("Retrieved mappings for index: %s", index_name)
            return mappings

    async def set_mappings(self, index_name: str, mappings: Dict) -> Dict:
        """Set the mappings for a specific Elasticsearch index."""
        es_url = f"{self.es_baseurl}/{index_name}"

        await self._create_session()

        async with self.session.put(es_url, json=mappings, auth=self.auth) as response:
            if response.status == 200:
                logging.info("Mappings set successfully: %s", mappings)
            else:
                logging.error(
                    "Failed to set mappings. Status: %s - %s",
                    response.status,
                    await response.text(),
                )
                raise ESException(response.status, await response.text())

            return response.json()

    async def index_doc(
        self, index_name: str, doc_id: str, msg: Dict
    ) -> ClientResponse:
        """Send data to a specific Elasticsearch index."""
        es_url = f"{self.es_baseurl}/{index_name}/_doc/{doc_id}"

        await self._create_session()

        async with self.session.put(es_url, json=msg, auth=self.auth) as response:
            logging.info("Index: %s - Document ID: %s", index_name, doc_id)
            if response.status == 201:
                logging.info("Document created successfully.")
            elif response.status == 200:
                logging.info("Document updated successfully.")
            else:
                logging.error(
                    "Failed to send data to Elasticsearch. Status %s - %s",
                    response.status,
                    await response.text(),
                )
                raise ESException(response.status, await response.text())

            return response

    async def bulk_index_docs(
        self, index_name: str, docs: List[Dict]
    ) -> ClientResponse:
        """Send multiple documents to a specific Elasticsearch index using the bulk API."""
        es_url = f"{self.es_baseurl}/{index_name}/_bulk"

        await self._create_session()

        # Prepare the bulk request payload
        bulk_payload = ""
        for doc in docs:
            action_metadata = {"index": {"_index": index_name, "_id": doc.get("id")}}
            bulk_payload += json.dumps(action_metadata) + "\n"
            bulk_payload += json.dumps(doc) + "\n"

        async with self.session.post(
            es_url,
            data=bulk_payload,
            headers={"Content-Type": "application/x-ndjson"},
            auth=self.auth,
        ) as response:
            logging.info("Bulk indexing to index: %s", index_name)
            if response.status in [200, 201]:
                logging.info("Bulk indexing completed successfully.")
            else:
                logging.error(
                    "Failed to send bulk data to Elasticsearch. Status %s - %s",
                    response.status,
                    await response.text(),
                )
                raise ESException(response.status, await response.text())

            return response

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
