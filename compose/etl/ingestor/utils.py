import json
import logging
from typing import Dict, List


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def convert_value(value: str):
    """
    Attempt to convert a string to an int or float if possible.

    Args:
        value (str): The string value to convert.

    Returns:
        The converted value (int, float, or str if conversion is not possible).
    """
    try:
        # Try converting to int
        return int(value)
    except ValueError:
        try:
            # Try converting to float
            return float(value)
        except ValueError:
            # Return the original string if it cannot be converted
            return value


def convert_dict_values(data: List[Dict]) -> List[Dict]:
    """
    Convert all string values in a list of dictionaries to numeric values (int or float) where applicable.

    Args:
        data (List[Dict]): List of dictionaries to convert.

    Returns:
        List[Dict]: A list of dictionaries with string values converted to numeric where possible.
    """
    for item in data:
        for key, value in item.items():
            # Convert value if it's a string
            if isinstance(value, str):
                item[key] = convert_value(value)
    return data


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
