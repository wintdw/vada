import logging
import json
import hashlib
from typing import Dict, List
from aiohttp import ClientSession, BasicAuth  # type: ignore

from libs.utils.common import remove_fields, generate_docid


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

    async def check_health(self) -> Dict:
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
            return {"status": response.status, "detail": await response.json()}

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

            return {"status": response.status, "detail": await response.json()}

    async def index_doc(self, index_name: str, doc: Dict, doc_id: str = None) -> Dict:
        """Send data to a specific Elasticsearch index."""
        await self._create_session()
        if "_vada" in doc:
            try:
                doc_id = doc.get("_vada", {}).get("ingest", {}).get("doc_id", "")
            except Exception:
                doc_id = ""

            doc = remove_fields(doc, ["_vada"])
        if not doc_id:
            doc_id = generate_docid(doc)

        es_url = f"{self.es_baseurl}/{index_name}/_doc/{doc_id}"

        async with self.session.put(es_url, json=doc, auth=self.auth) as response:
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

            return {"status": response.status, "detail": await response.json()}

    async def bulk_index_docs(self, index_name: str, docs: List[Dict]) -> Dict:
        """Send multiple documents to a specific Elasticsearch index using the bulk API."""
        await self._create_session()
        es_url = f"{self.es_baseurl}/{index_name}/_bulk"

        # Prepare the bulk request payload
        bulk_payload = ""
        for doc in docs:
            # Find the doc_id in the metadata, if appears
            if "_vada" in doc:
                try:
                    doc_id = doc.get("_vada", {}).get("ingest", {}).get("doc_id", "")
                except Exception:
                    doc_id = ""
                if not doc_id:
                    doc_id = generate_docid(doc)
                doc = remove_fields(doc, ["_vada"])

            action_metadata = {"index": {"_index": index_name, "_id": doc_id}}
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
                logging.info("%s docs indexed successfully", len(docs))
            else:
                logging.error(
                    "Failed to send bulk data to Elasticsearch. Status %s - %s",
                    response.status,
                    await response.text(),
                )

            response_json = await response.json()
            logging.info("Bulk response: %s", response_json)

            # For accounting purposes
            success = 0
            failure = 0
            error_msgs = []
            for item in response_json["items"]:
                if item["index"]["status"] not in [200, 201]:
                    error_msg = {
                        "index": item["index"]["_index"],
                        "status": item["index"]["status"],
                        "doc_id": item["index"]["_id"],
                        "reason": item["index"]["error"]["reason"],
                    }
                    logging.error(
                        "Failed to index doc_id: %s", json.dumps(error_msg, indent=4)
                    )
                    error_msgs.append(error_msg)
                    failure += 1
                else:
                    success += 1

            response_detail = {
                "took": response_json["took"],
                "errors": response_json["errors"],
                "success": success,
                "failure": failure,
                "error_msgs": error_msgs,
            }

            return {"status": response.status, "detail": response_detail}

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
