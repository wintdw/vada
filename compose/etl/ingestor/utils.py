import json
import logging
from dateutil import parser
from typing import Dict, List, Union, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def convert_datetime(value: str) -> Tuple[bool, Union[str, str]]:
    """
    Attempt to convert a string to a datetime if possible.

    Args:
        value (str): The date in string to be checked and converted.

    Returns:
        Tuple[bool, Union[str, str]]: A tuple where the first element is
        True if conversion is successful and the second element is the converted datetime in str format.
        If conversion fails, the first element is False and the second element is the original string.
    """
    if isinstance(value, str):
        try:
            converted_date = parser.parse(value)
            return True, str(converted_date)
        except (ValueError, OverflowError):
            return False, value
    else:
        return False, value


def convert_value(value: str) -> Tuple[bool, Union[int, float, str]]:
    """
    Attempt to convert a string to an int or float if possible.

    Args:
        value (str): The string value to convert.

    Returns:
        Tuple[bool, Union[int, float, str]]: A tuple where the first element is
        True if conversion is successful and the second element is the converted value.
        If conversion fails, the first element is False and the second element is the original string.
    """
    if isinstance(value, str):
        try:
            # Try converting to int
            converted_value = int(value)
            return True, converted_value
        except ValueError:
            try:
                # Try converting to float
                converted_value = float(value)
                return True, converted_value
            except ValueError:
                # Return the original string if it cannot be converted
                return False, value
    else:
        return False, value


def convert_dict_values(data: List[Dict]) -> List[Dict]:
    """
    Convert all string values in a list of dictionaries to datetime or numeric values (int or float) where applicable.

    Args:
        data (List[Dict]): List of dictionaries to convert.

    Returns:
        List[Dict]: A list of dictionaries with string values converted to datetime or numeric where possible.
    """
    for item in data:
        for key, value in item.items():
            # Convert value if it's a string
            if isinstance(value, str):
                is_date_converted, item[key] = convert_datetime(value)
                if not is_date_converted:
                    _, item[key] = convert_value(value)
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
