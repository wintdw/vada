import aiohttp  # type: ignore
import logging
from typing import Dict, List

from model.setting import settings


def get_optimal_batch_size(
    total_records: int, min_batch: int = 300, max_batch: int = 500
) -> int:
    """
    Find the most balanced batch size between min_batch and max_batch
    such that the batch count is minimized and the last batch isn't too small.
    """
    best_batch_size = None
    best_score = float("inf")

    for batch_size in range(min_batch, max_batch + 1):
        full_batches = total_records // batch_size
        remainder = total_records % batch_size

        if full_batches == 0:
            continue  # too large

        last_batch_size = remainder if remainder > 0 else batch_size
        if last_batch_size < min_batch:
            continue  # reject if final batch is too small

        total_batches = full_batches + (1 if remainder > 0 else 0)
        score = total_batches * batch_size - total_records

        if score < best_score:
            best_score = score
            best_batch_size = batch_size

    return best_batch_size if best_batch_size else min(total_records, max_batch)


def enrich_record(record: Dict) -> Dict:
    # Create doc_id based on create_time, id, and user_id
    doc_id = ".".join([str(record["create_time"]), record["id"], record["user_id"]])

    metadata = {
        "_vada": {
            "ingest": {
                "doc_id": doc_id,
            }
        }
    }
    return record | metadata


async def send_to_insert_service(records: List[Dict], index_name: str) -> Dict:
    payload = {"meta": {"index_name": index_name}, "data": records}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.INSERT_SERVICE_BASEURL}/json",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as response:
            resp_json = await response.json()
            return {
                "status": response.status,
                "detail": resp_json.get("detail", {}),
            }


async def post_processing(raw_data: List[Dict], index_name: str) -> Dict:
    """
    Produce data to insert service in batches, after enrichments.
    Args:
        raw_data: List of data to be processed and sent
        index_name: Name of the index to insert into
    Returns:
        Dict: Aggregated response from insert service
    """
    if not raw_data:
        logging.info(
            "No records to process for index '%s'. Skipping insert.", index_name
        )
        return {
            "took": 0,
            "error": False,
            "success": 0,
            "failure": 0,
            "error_msgs": [],
        }

    # Enrich records before batching
    enriched_records = [enrich_record(record) for record in raw_data]
    total_records = len(enriched_records)
    batch_size = get_optimal_batch_size(total_records)
    total_batches = (total_records + batch_size - 1) // batch_size

    logging.info(
        f"Sending {total_batches} batches (~{batch_size} records each, total {total_records} records) to Insert service"
    )

    total_took = 0
    total_success = 0
    total_failure = 0
    any_errors = False
    all_error_msgs = []

    for i in range(0, total_records, batch_size):
        batch = enriched_records[i : i + batch_size]
        current_batch = i // batch_size + 1

        logging.debug(f"Sending batch {current_batch} of {total_batches}")
        insert_json = await send_to_insert_service(batch, index_name)

        # Aggregate results
        total_took += insert_json["detail"].get("took", 0)
        total_success += insert_json["detail"].get("success", 0)
        total_failure += insert_json["detail"].get("failure", 0)
        any_errors = any_errors or insert_json["detail"].get("errors", False)
        all_error_msgs.extend(insert_json["detail"].get("error_msgs", []))

        logging.debug(
            f"Batch {current_batch}/{total_batches} - Response: {insert_json}"
        )

    return_dict = {
        "took": total_took,
        "error": any_errors,
        "success": total_success,
        "failure": total_failure,
        "error_msgs": all_error_msgs,
    }

    logging.info(
        f"Finished processing {total_records} records in {total_batches} batches. Response: {return_dict}"
    )

    return return_dict
