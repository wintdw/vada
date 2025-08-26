from typing import Dict


def enrich_record(record: Dict, type: str) -> Dict:
    """
    type can be "order" or "finance"
    """
    # Create doc_id based on create_time, id, and user_id

    if type == "order":
        doc_id = ".".join([str(record["create_time"]), record["id"], record["user_id"]])
    elif type == "finance":
        doc_id = ".".join([str(record["statement_time"]), record["id"]])
    else:
        raise RuntimeError(f"Unknown type: {type}")

    metadata = {
        "_vada": {
            "ingest": {
                "doc_id": doc_id,
            }
        }
    }
    return record | metadata
