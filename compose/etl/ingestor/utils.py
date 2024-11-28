import json
import logging
from typing import Dict, List


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def process_msg(msg: str) -> Dict:
    """
    Process the client message into a structured JSON object.

    Args:
        msg (str): Client-provided message in JSON format.

    Raises:
        ValidationError: If JSON is invalid or required fields are missing.

    Returns:
        Dict: A processed JSON object with a `__meta` field.
    """
    try:
        json_msg = json.loads(msg)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}")

    if not isinstance(json_msg, dict):
        raise ValidationError("Expected a JSON object (dictionary).")

    if "IndexName" not in json_msg:
        raise ValidationError("Missing required field: 'IndexName'.")

    # Create or update __meta field
    json_msg["__meta"] = json_msg.get("__meta", {})
    json_msg["__meta"]["index_name"] = json_msg["IndexName"]

    if "FriendlyName" in json_msg:
        json_msg["__meta"]["index_friendly_name"] = json_msg["FriendlyName"]

    # Remove specified fields
    fields_to_remove = ["IndexName", "FriendlyName"]
    ret_msg = {
        key: value for key, value in json_msg.items() if key not in fields_to_remove
    }

    return ret_msg
