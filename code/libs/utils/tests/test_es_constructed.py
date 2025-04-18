from datetime import datetime, timezone
from libs.utils.es_field_types import (
    construct_es_mappings,
    determine_and_convert_es_field_types,
)


def test_construct_es_mappings_basic():
    """Test basic field type mappings"""
    field_types = {
        "text_field": "text",
        "long_field": "long",
        "double_field": "double",
        "date_field": "date",
        "boolean_field": "boolean",
    }

    mappings = construct_es_mappings(field_types)

    assert "mappings" in mappings
    assert "properties" in mappings["mappings"]
    properties = mappings["mappings"]["properties"]

    # Check text field with keyword subfield
    assert properties["text_field"]["type"] == "text"
    assert "keyword" in properties["text_field"]["fields"]
    assert properties["text_field"]["fields"]["keyword"]["type"] == "keyword"

    # Check other basic types
    assert properties["long_field"]["type"] == "long"
    assert properties["double_field"]["type"] == "double"
    assert properties["date_field"]["type"] == "date"
    assert properties["boolean_field"]["type"] == "boolean"


def test_construct_es_mappings_nested():
    """Test nested and object field type mappings"""
    field_types = {
        "user": "object",
        "user.name": "text",
        "user.address": "object",
        "user.address.street": "text",
        "user.address.zip": "long",
        "user.contacts": "nested",
        "user.contacts.type": "text",
        "user.contacts.value": "text",
    }

    mappings = construct_es_mappings(field_types)
    properties = mappings["mappings"]["properties"]

    print(mappings)

    # Check object structure
    assert properties["user"]["type"] == "object"
    assert "properties" in properties["user"]

    user_props = properties["user"]["properties"]
    assert user_props["name"]["type"] == "text"
    assert user_props["address"]["type"] == "object"
    assert user_props["contacts"]["type"] == "nested"

    # Check nested address properties
    address_props = user_props["address"]["properties"]
    assert address_props["street"]["type"] == "text"
    assert address_props["zip"]["type"] == "long"

    # Check nested contacts properties
    contacts_props = user_props["contacts"]["properties"]
    assert contacts_props["type"]["type"] == "text"
    assert contacts_props["value"]["type"] == "text"


def test_construct_es_mappings_dynamic_settings():
    """Test dynamic settings in mappings"""
    field_types = {"field": "text"}
    mappings = construct_es_mappings(field_types)

    assert mappings["mappings"]["dynamic"] is True
    assert "dynamic_date_formats" in mappings["mappings"]
    assert isinstance(mappings["mappings"]["dynamic_date_formats"], list)


def test_determine_and_convert_full_workflow():
    """Test the complete workflow of determining types and converting data"""
    input_data = [
        {
            "user": {
                "name": "John Doe",
                "age": "30",
                "verified": "true",
                "score": "95.5",
                "created_at": "2023-01-01T12:00:00Z",
                "addresses": [
                    {
                        "type": "home",
                        "street": "123 Main St",
                        "zip": "10001",
                    },
                    {
                        "type": "work",
                        "street": "456 Market St",
                        "zip": "94105",
                    },
                ],
            }
        }
    ]

    # Process the data
    converted_data = determine_and_convert_es_field_types(input_data)

    # Verify the conversion results
    result = converted_data[0]

    assert isinstance(result["user"], dict)
    assert result["user"]["name"] == "John Doe"
    assert result["user"]["age"] == 30
    assert result["user"]["verified"] is True
    assert result["user"]["score"] == 95.5
    assert result["user"]["created_at"] == "2023-01-01T12:00:00+00:00"

    # Verify nested array conversion
    addresses = result["user"]["addresses"]
    assert len(addresses) == 2
    assert addresses[0]["zip"] == 10001
    assert addresses[0]["street"] == "123 Main St"
    assert addresses[1]["zip"] == 94105
    assert addresses[1]["street"] == "456 Market St"
