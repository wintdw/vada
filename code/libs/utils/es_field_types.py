import logging
from datetime import datetime, timezone
from collections import defaultdict
from dateutil import parser  # type: ignore
from typing import Dict, List, Any


def determine_es_field_types(json_objects: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Determines the Elasticsearch field types for a list of JSON objects.

    Args:
        json_objects (List[Dict[str, Any]]): A list of JSON objects, each representing a line of data.

    Returns:
        Dict[str, str]: A dictionary where keys are field names and values are the determined Elasticsearch field types.

    The function analyzes each field in the JSON objects and classifies it into one of the following Elasticsearch types:
        - "boolean": For boolean values.
        - "long": For integer values that are not likely timestamps.
        - "double": For floating-point numbers or strings that can be converted to floats.
        - "date": For integer values that are likely timestamps or strings that can be parsed as dates.
        - "text": For strings that are not dates, numbers.
        - "nested": For lists of dictionaries.
        - "unknown": For lists that do not fit the above criteria.

    The function uses heuristics to determine the most probable type for each field, prioritizing "double" if any double values are detected.
    """

    def is_valid_timestamp(value: int) -> bool:
        # Unix timestamps for the years 2000 to 2100
        # Start of 2000: 946684800
        # End of 2100: 4102444800
        # With milliseconds: Start of 2000: 946684800000, End of 2100: 4102444800000
        return (946684800 <= value <= 4102444800) or (
            946684800000 <= value <= 4102444800000
        )

    # Initialize a dictionary to count the occurrences of each type for each field
    field_type_counts = defaultdict(lambda: defaultdict(int))

    for data in json_objects:
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
                if value.lower() in ["true", "false"]:
                    field_type_counts[field]["boolean"] += 1
                    continue
                # Try to convert the string into a number (either int or float)
                try:
                    int_value = int(value)
                    # if it's too long -> keep it text
                    if len(value) > 15:
                        field_type_counts[field]["text"] += 1
                    # Check if it's timestamp
                    elif is_valid_timestamp(int_value):
                        field_type_counts[field]["date"] += 1
                    else:
                        field_type_counts[field]["long"] += 1
                except (ValueError, OverflowError):
                    try:
                        float(value)
                        field_type_counts[field]["double"] += 1
                    except ValueError:
                        # Check if the string is a valid date-time
                        try:
                            parser.parse(value)
                            field_type_counts[field]["date"] += 1
                        # Catch all other exception from dateutil.parser
                        except:
                            # If not a date, classify as text
                            field_type_counts[field]["text"] += 1
            elif isinstance(value, list):
                # Handle empty lists
                if not value:
                    field_type_counts[field]["unknown"] += 1
                # If the list contains dictionaries, classify as nested
                elif all(isinstance(item, dict) for item in value):
                    field_type_counts[field]["nested"] += 1
                else:
                    field_type_counts[field]["unknown"] += 1
            elif isinstance(value, dict):
                field_type_counts[field]["object"] += 1

    # Determine the most probable type for each field, applying the logic for 'double' when needed
    field_types = {}
    for field, type_counts in field_type_counts.items():
        most_probable_type = max(type_counts, key=type_counts.get)
        # If there are any text values, set the field type to text
        if "text" in type_counts:
            most_probable_type = "text"
        elif most_probable_type == "long" and "double" in type_counts:
            # If the most probable type is 'long' but 'double' was also detected, classify as 'double'
            most_probable_type = "double"

        field_types[field] = most_probable_type

    logging.info("Field types: %s", field_types)

    return field_types


def convert_es_field_types(
    json_objects: List[Dict[str, Any]], field_types: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Convert field types in a list of JSON objects based on specified field types.

    Args:
        json_objects (List[Dict[str, Any]]): A list of JSON objects, each representing a line of data.
        field_types (Dict[str, str]): A dictionary mapping field names to their desired types.
            Supported types include "boolean", "long", "double", "date", "nested", and "text".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with fields converted to the specified types.

    Conversion Rules:
        - "boolean": Converts "true"/"false" strings to boolean values.
        - "long": Converts strings or floats to integers.
        - "double": Converts strings or integers to floats.
        - "date": Converts strings to ISO format dates if they are not already.
        - "nested": Leaves nested dictionaries unchanged.
        - "text": Leaves strings unchanged.
        - For numeric fields ("long", "double"), sets None or empty string values to 0.
        - Skips fields that cannot be converted.
    """

    converted_json_objects = []

    for data in json_objects:
        for field, value in data.items():
            field_type = field_types.get(field)

            if value is None or value == "":
                if field_type in ["long", "double"]:
                    # If value is None or an empty string, set to 0 for numeric fields
                    data[field] = 0
                if field_type == "date":
                    # Set default date to 1/1/2000 if the value is empty
                    data[field] = datetime(2000, 1, 1, tzinfo=timezone.utc).isoformat()
                continue  # No need for further conversion checks

            if field_type == "boolean":
                # Convert "true"/"false" strings to boolean
                if isinstance(value, str):
                    data[field] = value.lower() == "true"
                elif isinstance(value, bool):
                    data[field] = value

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
                        # If parsing fails, try to convert string to int and then to date
                        try:
                            int_value = int(value)
                            data[field] = datetime.fromtimestamp(
                                int_value, timezone.utc
                            ).isoformat()
                        except (ValueError, TypeError):
                            # If all parsing fails, try dateutil parser
                            try:
                                data[field] = parser.parse(value).isoformat()
                            except (ValueError, TypeError):
                                continue  # If conversion fails, leave it unchanged
                elif isinstance(value, int):
                    # Convert integer timestamp to ISO format date
                    try:
                        data[field] = datetime.fromtimestamp(
                            value, timezone.utc
                        ).isoformat()
                    except (ValueError, TypeError):
                        continue  # If parsing fails, leave it unchanged

            elif field_type == "object" and isinstance(value, dict):
                # If it's a dictionary, no need to modify
                pass

            elif field_type == "nested" and isinstance(value, list):
                # If it's a nested dictionary, no need to modify
                pass

            elif field_type == "text" and isinstance(value, str):
                # Text are typically strings and don't require conversion
                pass

            else:
                # For other types (or unclassified types), no conversion needed
                pass

        converted_json_objects.append(data)

    return converted_json_objects


def determine_and_convert_es_field_types(json_lines: List[str]) -> List[Dict[str, Any]]:
    """
    Determine Elasticsearch field types and convert fields in a list of JSON lines.

    Args:
        json_lines (List[str]): A list of JSON strings, each representing a line of data.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with fields converted to their determined Elasticsearch types.

    The function first determines the most probable Elasticsearch field types for each field in the JSON lines.
    It then converts the fields in the JSON lines to these determined types, ensuring compatibility with Elasticsearch.
    """
    field_types = determine_es_field_types(json_lines)
    converted_json_lines = convert_es_field_types(json_lines, field_types)

    return converted_json_lines


def construct_es_mappings(field_types: Dict[str, str]) -> Dict[str, Any]:
    """
    Construct Elasticsearch mappings based on field types.

    Args:
        field_types (Dict[str, str]): A dictionary where keys are field names and values are the determined Elasticsearch field types.

    Returns:
        Dict[str, Any]: A dictionary representing the Elasticsearch mappings.
    """
    es_mappings = {
        "mappings": {"dynamic": True, "properties": {}},
    }

    for field, field_type in field_types.items():
        es_field_type = field_type
        # for the list of str/int, or "unknown"
        if field_type == "unknown":
            es_field_type = "text"

        # Add field mapping
        if es_field_type == "text":
            # Add keyword subfield for text fields
            es_mappings["mappings"]["properties"][field] = {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256,
                        "eager_global_ordinals": True,
                    },
                },
            }
        else:
            # For non-text fields, keep as is
            es_mappings["mappings"]["properties"][field] = {"type": es_field_type}

    return es_mappings
