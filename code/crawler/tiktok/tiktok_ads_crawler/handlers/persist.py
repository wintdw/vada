import logging
from typing import List, Dict

from tools.requests import post
from models.settings import settings

logger = logging.getLogger(__name__)


def add_insert_metadata(batch_report: List, index_name: str) -> dict:
    return {"meta": {"index_name": index_name}, "data": batch_report}


async def send_to_insert_service(data: Dict) -> dict:
    request_json = await post(url=f"{settings.INSERT_SERVICE_URL}/json", json=data)
    return request_json


async def send_batch(batch_report: List, index_name: str) -> Dict:
    """Produce data to insert service in batches of 1000

    Args:
        batch_report: List of data to be processed and sent
        index_name: Name of the index to insert into

    Returns:
        Dict: Last response from insert service
    """
    batch_size = 1000
    total_reports = len(batch_report)
    total_batches = (total_reports + batch_size - 1) // batch_size
    last_response = {}

    for i in range(0, total_reports, batch_size):
        batch = batch_report[i : i + batch_size]
        current_batch = i // batch_size + 1

        logger.debug(f"Sending batch {current_batch} of {total_batches}")
        insert_json = await send_to_insert_service(
            add_insert_metadata(batch, index_name)
        )

        status = insert_json.get("status", "unknown")
        detail = insert_json.get("detail", "")

        if status != "success":
            logger.error(
                f"Batch {current_batch}/{total_batches} - Status: {status} - Detail: {detail}"
            )

        last_response = insert_json

    return last_response
