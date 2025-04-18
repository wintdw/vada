import logging
from datetime import datetime, timezone
from collections import defaultdict
from dateutil import parser  # type: ignore
from typing import Dict, List, Any


def determine_es_field_types(
    json_objects: List[Dict[str, Any]], nested_path: str = ""
) -> Dict[str, str]:
    """
    Determines the Elasticsearch field types for a list of JSON objects, including nested objects.

    Args:
        json_objects (List[Dict[str, Any]]): A list of JSON objects, each representing a line of data.
        nested_path (str): The current nested path (used internally for recursion).

    Returns:
        Dict[str, str]: A dictionary where keys are field names and values are the determined Elasticsearch field types.
    """

    def is_valid_timestamp(value: int) -> bool:
        # Unix timestamps for the years 2000 to 2100
        # Start of 2000: 946684800
        # End of 2100: 4102444800
        # With milliseconds: Start of 2000: 946684800000, End of 2100: 4102444800000
        # With microseconds: Start of 2000: 946684800000000, End of 2100: 4102444800000000
        return (
            (946684800 <= value <= 4102444800)
            or (946684800000 <= value <= 4102444800000)
            or (946684800000000 <= value <= 4102444800000000)
        )

    # Initialize a dictionary to count the occurrences of each type for each field
    field_type_counts = defaultdict(lambda: defaultdict(int))

    for data in json_objects:
        for field, value in data.items():
            full_field_name = f"{nested_path}.{field}" if nested_path else field

            # Handle nested dictionary
            if isinstance(value, dict):
                nested_types = determine_es_field_types([value], full_field_name)
                for nested_field, nested_type in nested_types.items():
                    field_type_counts[nested_field][nested_type] += 1
                field_type_counts[full_field_name]["object"] += 1
                continue

            # Handle nested list of dictionaries
            if (
                isinstance(value, list)
                and value
                and all(isinstance(item, dict) for item in value)
            ):
                nested_types = determine_es_field_types(value, full_field_name)
                for nested_field, nested_type in nested_types.items():
                    field_type_counts[nested_field][nested_type] += 1
                field_type_counts[full_field_name]["nested"] += 1
                continue

            # Rest of the existing type detection logic
            if isinstance(value, bool):
                field_type_counts[full_field_name]["boolean"] += 1
            elif isinstance(value, int):
                if is_valid_timestamp(value):
                    field_type_counts[full_field_name]["date"] += 1
                else:
                    field_type_counts[full_field_name]["long"] += 1
            elif isinstance(value, float):
                field_type_counts[full_field_name]["double"] += 1
            elif isinstance(value, str):
                if not value:
                    continue
                if value.lower() in ["true", "false"]:
                    field_type_counts[full_field_name]["boolean"] += 1
                    continue
                try:
                    int_value = int(value)
                    if is_valid_timestamp(int_value):
                        field_type_counts[full_field_name]["date"] += 1
                    elif len(value) > 13:
                        field_type_counts[full_field_name]["text"] += 1
                    else:
                        field_type_counts[full_field_name]["long"] += 1
                except (ValueError, OverflowError):
                    try:
                        float(value)
                        field_type_counts[full_field_name]["double"] += 1
                    except ValueError:
                        try:
                            parser.parse(value)
                            field_type_counts[full_field_name]["date"] += 1
                        except:
                            field_type_counts[full_field_name]["text"] += 1
            elif isinstance(value, list):
                if not value:
                    field_type_counts[full_field_name]["unknown"] += 1
                elif all(isinstance(item, dict) for item in value):
                    field_type_counts[full_field_name]["nested"] += 1
                else:
                    field_type_counts[full_field_name]["unknown"] += 1

    # Determine the most probable type for each field
    field_types = {}
    for field, type_counts in field_type_counts.items():
        most_probable_type = max(type_counts, key=type_counts.get)
        if "text" in type_counts:
            most_probable_type = "text"
        elif most_probable_type == "long" and "double" in type_counts:
            most_probable_type = "double"

        field_types[field] = most_probable_type

    logging.info("Field types: %s", field_types)

    return field_types


def convert_es_field_types(
    json_objects: List[Dict[str, Any]],
    field_types: Dict[str, str],
    nested_path: str = "",
) -> List[Dict[str, Any]]:
    """
    Convert field types in a list of JSON objects based on specified field types.

    Args:
        json_objects (List[Dict[str, Any]]): A list of JSON objects, each representing a line of data.
        field_types (Dict[str, str]): A dictionary mapping field names to their desired types.
        nested_path (str): The current nested path (used internally for recursion).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with fields converted to the specified types.

    Conversion Rules:
        - "boolean": Converts "true"/"false" strings to boolean values.
        - "long": Converts strings or floats to integers.
        - "double": Converts strings or integers to floats.
        - "date": Converts strings to ISO format dates if they are not already.
        - "nested": Processes nested lists of dictionaries recursively.
        - "object": Processes nested dictionaries recursively.
        - "text": Leaves strings unchanged.
        - For numeric fields ("long", "double"), sets None or empty string values to 0.
        - Skips fields that cannot be converted.
    """
    converted_json_objects = []

    for data in json_objects:
        converted_data = data.copy()
        for field, value in data.items():
            full_field_name = f"{nested_path}.{field}" if nested_path else field
            field_type = field_types.get(full_field_name)

            # Handle nested dictionary
            if isinstance(value, dict):
                converted_data[field] = convert_es_field_types(
                    [value], field_types, full_field_name
                )[0]
                continue

            # Handle nested list of dictionaries
            if (
                isinstance(value, list)
                and value
                and all(isinstance(item, dict) for item in value)
            ):
                converted_data[field] = convert_es_field_types(
                    value, field_types, full_field_name
                )
                continue

            if value is None or value == "":
                if field_type in ["long", "double"]:
                    converted_data[field] = 0
                elif field_type == "date":
                    converted_data[field] = datetime(
                        2000, 1, 1, tzinfo=timezone.utc
                    ).isoformat()
                continue

            # Rest of the type conversion logic remains the same
            if field_type == "boolean":
                if isinstance(value, str):
                    converted_data[field] = value.lower() == "true"
                elif isinstance(value, bool):
                    converted_data[field] = value

            elif field_type == "long":
                if isinstance(value, str):
                    try:
                        converted_data[field] = int(value)
                    except ValueError:
                        continue
                elif isinstance(value, float):
                    converted_data[field] = int(value)

            elif field_type == "double":
                if isinstance(value, str):
                    try:
                        converted_data[field] = float(value)
                    except ValueError:
                        continue
                elif isinstance(value, int):
                    converted_data[field] = float(value)

            elif field_type == "date":
                if isinstance(value, str):
                    try:
                        converted_data[field] = parser.isoparse(value).isoformat()
                    except (ValueError, TypeError):
                        try:
                            int_value = int(value)
                            converted_data[field] = datetime.fromtimestamp(
                                (
                                    int_value / 1000000
                                    if int_value > 100000000000000
                                    else (
                                        int_value / 1000
                                        if int_value > 100000000000
                                        else int_value
                                    )
                                ),
                                timezone.utc,
                            ).isoformat()
                        except (ValueError, TypeError):
                            try:
                                converted_data[field] = parser.parse(value).isoformat()
                            except (ValueError, TypeError):
                                continue
                elif isinstance(value, int):
                    try:
                        converted_data[field] = datetime.fromtimestamp(
                            value, timezone.utc
                        ).isoformat()
                    except (ValueError, TypeError):
                        continue

        converted_json_objects.append(converted_data)

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
    date_formats = [
        "strict_date_optional_time",
        "basic_date",
        "basic_date_time",
        "basic_date_time_no_millis",
        "yyyy/MM/dd HH:mm:ss",
    ]

    es_mappings = {
        "mappings": {
            "dynamic": True,
            "dynamic_date_formats": date_formats,
            "properties": {},
        },
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

        es_mappings["mappings"]["properties"][field] = {"type": es_field_type}

    return es_mappings
