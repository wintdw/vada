import json
import base64
from collections import defaultdict
from dateutil import parser  # type: ignore
from typing import Dict, List, Any


def determine_es_field_types(json_lines: List[str]) -> Dict[str, str]:
    """
    Determines the Elasticsearch field types for a list of JSON lines.

    Args:
        json_lines (List[str]): A list of JSON strings, each representing a line of data.

    Returns:
        Dict[str, str]: A dictionary where keys are field names and values are the determined Elasticsearch field types.

    The function analyzes each field in the JSON lines and classifies it into one of the following Elasticsearch types:
        - "boolean": For boolean values.
        - "long": For integer values that are not likely timestamps.
        - "double": For floating-point numbers or strings that can be converted to floats.
        - "date": For integer values that are likely timestamps or strings that can be parsed as dates.
        - "keyword": For strings that are not dates, numbers, or binary data.
        - "binary": For strings that are valid Base64 encoded binary data.
        - "nested": For lists of dictionaries or dictionaries.
        - "unknown": For lists that do not fit the above criteria.

    The function uses heuristics to determine the most probable type for each field, prioritizing "double" if any double values are detected.
    """

    def is_valid_timestamp(value: int) -> bool:
        # Unix timestamps for the years 2000 to 2100
        # Start of 2000: 946684800
        # End of 2100: 4102444800
        return 946684800 <= value <= 4102444800

    # Initialize a dictionary to count the occurrences of each type for each field
    field_type_counts = defaultdict(lambda: defaultdict(int))

    for line in json_lines:
        try:
            data = json.loads(line)
            for field, value in data.items():
                # Determine the type of the value based on ES data types
                if isinstance(value, bool):
                    field_type_counts[field]["boolean"] += 1
                elif isinstance(value, int):
                    # Check if the integer is a likely timestamp
                    if is_valid_timestamp(value):
                        field_type_counts[field]["date"] += 1
                    else:
                        field_type_counts[field]["long"] += 1
                elif isinstance(value, float):
                    field_type_counts[field]["double"] += 1
                elif isinstance(value, str):
                    if not value:
                        continue  # Skip empty strings
                    # Try to convert the string into a number (either int or float)
                    try:
                        int_value = int(value)
                        # If conversion to int is successful, classify as long
                        if is_valid_timestamp(int_value):
                            field_type_counts[field]["date"] += 1
                        else:
                            field_type_counts[field]["long"] += 1
                    except ValueError:
                        try:
                            float_value = float(value)
                            field_type_counts[field]["double"] += 1
                        except ValueError:
                            # Check if the string is a valid Base64 encoded binary
                            try:
                                base64.b64decode(value, validate=True)
                                field_type_counts[field]["binary"] += 1
                            except (base64.binascii.Error, ValueError):
                                # Check if the string is a valid date-time
                                try:
                                    parser.isoparse(value)  # Try parsing as ISO format
                                    field_type_counts[field]["date"] += 1
                                except (ValueError, TypeError):
                                    # If not a date, classify as keyword
                                    field_type_counts[field]["keyword"] += 1
                elif isinstance(value, list):
                    # If the list contains dictionaries, classify as nested
                    if all(isinstance(item, dict) for item in value):
                        field_type_counts[field]["nested"] += 1
                    # If the list contains strings, it could be a keyword family
                    elif all(isinstance(item, str) for item in value):
                        field_type_counts[field]["keyword"] += 1
                    else:
                        field_type_counts[field]["unknown"] += 1
                elif isinstance(value, dict):
                    # Classify dictionaries as nested
                    field_type_counts[field]["nested"] += 1

        except json.JSONDecodeError:
            continue  # Skip invalid JSON lines

    # Determine the most probable type for each field, applying the logic for 'double' when needed
    field_types = {}
    for field, type_counts in field_type_counts.items():
        # If any 'double' values were detected, classify the field as 'double'
        if "double" in type_counts and type_counts["double"] > 0:
            field_types[field] = "double"
        else:
            # Otherwise, take the most probable type
            most_probable_type = max(type_counts, key=type_counts.get)
            field_types[field] = most_probable_type

    return field_types


def convert_es_field_types(
    json_lines: List[str], field_types: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Convert field types in a list of JSON lines based on specified field types.

    Args:
        json_lines (List[str]): A list of JSON strings, each representing a line of data.
        field_types (Dict[str, str]): A dictionary mapping field names to their desired types.
            Supported types include "boolean", "long", "double", "date", "binary", "nested", and "keyword".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with fields converted to the specified types.

    Conversion Rules:
        - "boolean": Converts "true"/"false" strings to boolean values.
        - "long": Converts strings or floats to integers.
        - "double": Converts strings or integers to floats.
        - "date": Converts strings to ISO format dates if they are not already.
        - "binary": Validates base64-encoded strings.
        - "nested": Leaves nested dictionaries unchanged.
        - "keyword": Leaves strings unchanged.
        - For numeric fields ("long", "double"), sets None or empty string values to 0.
        - Skips invalid JSON lines and fields that cannot be converted.
    """

    converted_json_lines = []

    for line in json_lines:
        try:
            data = json.loads(line)
            for field, value in data.items():
                field_type = field_types.get(field)

                # If value is None or an empty string, set to 0 for numeric fields
                if value is None or value == "":
                    if field_type in ["long", "double"]:
                        data[field] = 0
                    continue  # No need for further conversion checks, as it's now 0

                if field_type == "boolean" and isinstance(value, str):
                    # Convert "true"/"false" strings to boolean
                    data[field] = (
                        value.lower() == "true" if isinstance(value, str) else value
                    )

                elif field_type == "long":
                    # Convert string or float to int
                    if isinstance(value, str):
                        try:
                            data[field] = int(value)
                        except ValueError:
                            continue  # If the string can't be converted, leave it unchanged
                    elif isinstance(value, float):
                        data[field] = int(value)

                elif field_type == "double":
                    # Convert string or int to float
                    if isinstance(value, str):
                        try:
                            data[field] = float(value)
                        except ValueError:
                            continue  # If the string can't be converted, leave it unchanged
                    elif isinstance(value, int):
                        data[field] = float(value)

                elif field_type == "date":
                    # Convert string to ISO format date if it's not already
                    if isinstance(value, str):
                        try:
                            # Attempt to parse string as date and convert to ISO format
                            data[field] = parser.isoparse(value).isoformat()
                        except (ValueError, TypeError):
                            continue  # If parsing fails, leave it unchanged

                elif field_type == "binary":
                    # If base64-encoded string, leave it as it is
                    if isinstance(value, str):
                        try:
                            base64.b64decode(value, validate=True)
                        except (base64.binascii.Error, ValueError):
                            continue  # If not valid base64, leave it unchanged

                elif field_type == "nested" and isinstance(value, dict):
                    # If it's a nested dictionary, no need to modify
                    pass

                elif field_type == "keyword" and isinstance(value, str):
                    # Keywords are typically strings and don't require conversion
                    pass

                else:
                    # For other types (or unclassified types), no conversion needed
                    pass

            converted_json_lines.append(data)

        except json.JSONDecodeError:
            continue  # Skip invalid JSON lines

    return converted_json_lines
