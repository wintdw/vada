import math
import logging
import aiohttp  # type: ignore

from datetime import datetime
from typing import Dict, List

from model.settings import settings


def get_optimal_batch_size(
    total_docs: int, min_batch: int = 500, max_batch: int = 1000
) -> int:
    """
    Find the most balanced batch size between min_batch and max_batch
    that evenly splits total_docs into batches with minimal remainder.

    Returns:
        int: Best-fit batch size
    """
    best_batch_size = max_batch
    min_remainder = total_docs

    for batch_size in range(min_batch, max_batch + 1):
        remainder = total_docs % batch_size
        num_batches = total_docs // batch_size
        if num_batches == 0:
            continue  # skip batch sizes larger than total_docs

        # Prefer batch sizes with:
        # - minimal remainder
        # - fewer batches (larger batch size)
        if remainder < min_remainder or (
            remainder == min_remainder and batch_size > best_batch_size
        ):
            best_batch_size = batch_size
            min_remainder = remainder

            if remainder == 0:
                break  # perfect fit

    return best_batch_size


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
    total_docs = len(docs)
    batch_size = get_optimal_batch_size(total_docs)
    total_batches = (total_docs + batch_size - 1) // batch_size
    last_response = {}

    logging.info(
        f"Sending {total_batches} batches (~{batch_size} docs each, total {total_docs} docs) to Insert service"
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
