from typing import Dict


def enrich_record(record: Dict, type: str) -> Dict:
    """
    type can be "order" or "finance"
    """
    # Create doc_id based on create_time, id, and user_id

    doc_id = ".".join([str(record["create_time"]), record["id"], record["user_id"]])
    if type == "finance":
        doc_id = ".".join([str(record["create_time"]), record["id"]])

    metadata = {
        "_vada": {
            "ingest": {
                "doc_id": doc_id,
            }
        }
    }
    return record | metadata
