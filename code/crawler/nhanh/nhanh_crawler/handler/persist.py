import logging
import aiohttp  # type: ignore

from datetime import datetime
from typing import Dict, List

from model.settings import settings


def enrich_doc(doc: Dict) -> Dict:
    # Create doc_id based on the document's id and createdDateTime
    ts = int(datetime.strptime(doc["createdDateTime"], "%Y-%m-%d %H:%M:%S").timestamp())
    doc_id = f"{doc['id']}_{ts}"

    metadata = {
        "_vada": {
            "ingest": {
                "doc_id": doc_id,
            }
        }
    }
    return doc | metadata


async def send_to_insert_service(docs: List[Dict], index_name: str) -> Dict:
    payload = {"meta": {"index_name": index_name}, "data": docs}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.INSERT_SERVICE_BASEURL}/json",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as response:
            resp_json = await response.json()
            return {
                "status": response.status,
                "detail": resp_json["detail"],
            }


async def post_processing(docs: List[Dict], index_name: str) -> Dict:
    """Produce data to insert service in batches
    Note: The process is after doc enrichment (enrich_doc)

    Args:
        docs: List of processed data to be sent
        index_name: Name of the index to insert into

    Returns:
        Dict: Last response from insert service
    """
    batch_size = 1000
    total_docs = len(docs)
    total_batches = (total_docs + batch_size - 1) // batch_size
    last_response = {}

    logging.info(
        f"Sending {total_batches} batches ({total_docs} total docs) to insert service"
    )

    for i in range(0, total_docs, batch_size):
        batch = docs[i : i + batch_size]
        current_batch = i // batch_size + 1

        logging.debug(f"Sending batch {current_batch} of {total_batches}")
        insert_json = await send_to_insert_service(batch, index_name)

        status = insert_json.get("status", "unknown")
        detail = insert_json.get("detail", "")

        if status != "success":
            logging.error(
                f"Batch {current_batch}/{total_batches} - Status: {status} - Detail: {detail}"
            )

        last_response = insert_json

    return last_response
