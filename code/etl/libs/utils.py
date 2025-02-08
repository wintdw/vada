import json
from typing import Dict

from libs.utils.common import remove_fields, generate_docid


def process_msg(msg: str) -> Dict:
    """
    Process the client message into a structured JSON object.

    Args:
        msg (str): Client-provided message in JSON format.

    Raises:
        RuntimeError: If JSON is invalid or required fields are missing.

    Returns:
        Dict: A processed JSON object with a `__vada` field.
    """
    try:
        json_msg = json.loads(msg)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON format: {e}")

    if not isinstance(json_msg, dict):
        raise RuntimeError("Expected a JSON object (dictionary).")

    if "IndexName" not in json_msg:
        raise RuntimeError("Missing required field: 'IndexName'.")

    index_name = json_msg["IndexName"]
    if "FriendlyName" in json_msg:
        index_friendly_name = json_msg["FriendlyName"]
    else:
        index_friendly_name = index_name

    json_msg = remove_fields(json_msg, ["IndexName", "FriendlyName"])
    doc_id = generate_docid(json_msg)

    # update _vada field
    json_msg["_vada"] = {
        "ingest": {
            "doc_id": doc_id,
            "destination": {
                "type": "elasticsearch",
                "index": index_name,
                "index_friendly_name": index_friendly_name,
            },
        }
    }

    return json_msg
