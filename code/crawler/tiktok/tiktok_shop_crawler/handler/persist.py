import aiohttp  # type: ignore
import logging
from typing import Dict, List

from model.setting import settings


def add_insert_metadata(records: List, index_name: str) -> Dict:
    return {"meta": {"index_name": index_name}, "data": records}


def enrich_record(record: Dict, doc_id: str) -> Dict:
    metadata = {
        "_vada": {
            "ingest": {
                "doc_id": doc_id,
            }
        }
    }
    return record | metadata


async def send_to_insert_service(data: Dict) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.INSERT_SERVICE_BASEURL}/json",
            json=data,
            headers={"Content-Type": "application/json"},
        ) as response:
            return {"status": response.status, "detail": await response.text()}


### The main function to process and send records
async def post_processing(raw_data: List[Dict], index_name: str) -> Dict:
    """Produce data to insert service in batches of 1000

    Args:
        raw_data: List of data to be processed and sent

    Returns:
        Dict: Last response from insert service
    """

    # Enrich each record with metadata
    enriched_records = []
    for record in raw_data:
        doc_id = ".".join(
            [
                str(record.get("create_time", "")),
                record.get("id", ""),
                record.get("user_id", ""),
            ]
        )
        enriched_record = enrich_record(record, doc_id)
        enriched_records.append(enriched_record)

    batch_size = 300
    total_records = len(enriched_records)
    total_batches = (total_records + batch_size - 1) // batch_size
    last_response = {}

    logging.info(f"Sending {total_batches} batches to insert service")

    for i in range(0, total_records, batch_size):
        batch = enriched_records[i : i + batch_size]
        current_batch = i // batch_size + 1

        enriched_record_data = add_insert_metadata(batch, index_name)
        response = await send_to_insert_service(enriched_record_data)
        status = response.get("status", 0)
        if status != 200:
            logging.error(
                f"Batch {current_batch}/{total_batches} failed - Status: {status} - Detail: {response.get('detail', '')}"
            )
        last_response = response

    return last_response
