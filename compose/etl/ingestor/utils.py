import json
import logging
from dateutil import parser
from datetime import datetime
from typing import Dict, List, Union, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def convert_datetime_to_isoformat(dt: datetime) -> str:
    """
    Convert a datetime object to a string in the strict_date_optional_time_nanos format
    that is compatible with Elasticsearch.

    Args:
        dt (datetime): The datetime object to be converted.

    Returns:
        str: The formatted datetime string compatible with Elasticsearch.
    """
    if isinstance(dt, datetime):
        # Handle the case when the datetime only has the date (no time part)
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
            return dt.date().isoformat()  # e.g., "2024-12-03"

        nanoseconds = dt.microsecond * 1000
        return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{nanoseconds:09d}Z")


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
            return True, convert_datetime_to_isoformat(converted_date)
        except (ValueError, OverflowError):
            return False, value
    else:
        return False, value


def convert_value(value: str) -> Tuple[bool, Union[int, float, str, datetime]]:
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
        # First, try converting to datetime
        if value.isdigit() and len(value) == 8:
            try:
                converted_value = datetime.strptime(value, "%Y%m%d")
                return True, convert_datetime_to_isoformat(converted_value)
            except ValueError:
                pass

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
            # first, convert str -> number
            # if not converted -> try datetime
            if isinstance(value, str):
                is_converted, converted_value = convert_value(value)
                if not is_converted:
                    _, converted_value = convert_datetime(value)
            item[key] = converted_value
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
