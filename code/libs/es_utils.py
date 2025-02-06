import json
import base64
from collections import defaultdict
from dateutil import parser  # type: ignore
from typing import Dict, List


def determine_es_field_types(json_lines: List[str]) -> Dict[str, str]:
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
                # Add more types if needed
        except json.JSONDecodeError:
            continue  # Skip invalid JSON lines

    # Determine the most probable type for each field
    field_types = {}
    for field, type_counts in field_type_counts.items():
        most_probable_type = max(type_counts, key=type_counts.get)
        field_types[field] = most_probable_type

    return field_types
