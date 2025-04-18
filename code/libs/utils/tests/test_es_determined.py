import json
from libs.utils.es_field_types import determine_es_field_types


def test_determine_es_field_types_nested():
    # Test data with various nested structures
    json_lines = [
        {
            "user": {
                "name": "John Doe",
                "age": 30,
                "contact": {"email": "john@example.com", "phone": "123-456-7890"},
                "addresses": [
                    {
                        "type": "home",
                        "street": "123 Main St",
                        "city": "New York",
                        "zip": "10001",
                        "coordinates": {"lat": 40.7128, "lon": -74.0060},
                    },
                    {
                        "type": "work",
                        "street": "456 Market St",
                        "city": "San Francisco",
                        "zip": "94105",
                        "coordinates": {"lat": 37.7749, "lon": -122.4194},
                    },
                ],
            },
            "metadata": {
                "created_at": "2023-01-01T12:00:00Z",
                "is_active": "true",
                "score": "95.5",
                "tags": ["premium", "verified"],
            },
        }
    ]

    field_types = determine_es_field_types(json_lines)

    # Expected field types with dot notation for nested fields
    expected_types = {
        "metadata": "object",
        "metadata.created_at": "date",
        "metadata.is_active": "boolean",
        "metadata.score": "double",
        "metadata.tags": "unknown",
        "user": "object",
        "user.addresses": "nested",
        "user.addresses.city": "text",
        "user.addresses.coordinates": "object",
        "user.addresses.coordinates.lat": "double",
        "user.addresses.coordinates.lon": "double",
        "user.addresses.street": "text",
        "user.addresses.type": "text",
        "user.addresses.zip": "long",
        "user.age": "long",
        "user.contact": "object",
        "user.contact.email": "text",
        "user.contact.phone": "text",
        "user.name": "text",
    }

    print("Actual field types:")
    print(json.dumps(field_types, indent=2))
    print("\nExpected field types:")
    print(json.dumps(expected_types, indent=2))

    assert field_types == expected_types


def test_determine_es_field_types_empty_nested():
    # Test handling of empty nested structures
    json_lines = [{"user": {}, "addresses": [], "metadata": {"tags": []}}]

    field_types = determine_es_field_types(json_lines)

    expected_types = {
        "user": "object",
        "addresses": "unknown",
        "metadata": "object",
        "metadata.tags": "unknown",
    }

    assert field_types == expected_types


def test_determine_es_field_types_mixed_types():
    # Test handling of fields that sometimes contain nested structures
    # and sometimes contain primitive values
    json_lines = [
        {"data": {"value": "nested object"}},
        {"data": "simple string"},
        {"data": {"value": "another nested"}},
    ]

    field_types = determine_es_field_types(json_lines)

    # Should prefer text type when mixed with objects
    expected_types = {"data": "text", "data.value": "text"}

    assert field_types == expected_types


def test_determine_es_field_types_deep_nesting():
    # Test handling of deeply nested structures
    json_lines = [
        {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep nested",
                            "number": 42,
                            "date": "2023-01-01T00:00:00Z",
                        }
                    }
                }
            }
        }
    ]

    field_types = determine_es_field_types(json_lines)

    expected_types = {
        "level1": "object",
        "level1.level2": "object",
        "level1.level2.level3": "object",
        "level1.level2.level3.level4": "object",
        "level1.level2.level3.level4.value": "text",
        "level1.level2.level3.level4.number": "long",
        "level1.level2.level3.level4.date": "date",
    }

    assert field_types == expected_types
