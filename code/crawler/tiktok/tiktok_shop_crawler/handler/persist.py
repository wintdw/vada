import aiohttp  # type: ignore
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
    """Produce data to insert service

    Args:
        raw_data: List of data to be processed and sent

    Returns:
        Dict: Response from insert service
    """

    # Enrich each record with metadata
    enriched_records = []
    for record in raw_data:
        # Create unique doc ID using ad.id + ad_group.id + campaign.id + date
        doc_id = ".".join(
            [
                record.get("create_time", ""),
                record.get("buyer_uid", ""),
                record.get("order_id", ""),
            ]
        )
        enriched_record = enrich_record(record, doc_id)
        enriched_records.append(enriched_record)

    # Add insert metadata wrapper
    enriched_record_data = add_insert_metadata(enriched_records, index_name)

    # Send to insert service
    response = await send_to_insert_service(enriched_record_data)

    return response
