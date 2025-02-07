import json
import hashlib
from typing import Dict, List


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def generate_docid(msg: Dict) -> str:
    serialized_data = json.dumps(msg, sort_keys=True)
    return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()


def remove_fields(msg: Dict, fields_to_remove: List) -> Dict:
    return {k: v for k, v in msg.items() if k not in fields_to_remove}


def process_msg(msg: str) -> Dict:
    """
    Process the client message into a structured JSON object.

    Args:
        msg (str): Client-provided message in JSON format.

    Raises:
        ValidationError: If JSON is invalid or required fields are missing.

    Returns:
        Dict: A processed JSON object with a `__vada` field.
    """
    try:
        json_msg = json.loads(msg)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}")

    if not isinstance(json_msg, dict):
        raise ValidationError("Expected a JSON object (dictionary).")

    if "IndexName" not in json_msg:
        raise ValidationError("Missing required field: 'IndexName'.")

    # update __vada field
    json_msg["__vada"] = {}
    json_msg["__vada"]["index_name"] = json_msg["IndexName"]

    if "FriendlyName" in json_msg:
        json_msg["__vada"]["index_friendly_name"] = json_msg["FriendlyName"]

    ret_msg = remove_fields(json_msg, ["IndexName", "FriendlyName"])

    return ret_msg
