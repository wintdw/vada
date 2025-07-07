from datetime import datetime, timezone, timedelta
from libs.utils.es_field_types import convert_es_field_types


def test_convert_es_field_types_nested():
    """Test conversion of nested structures"""
    json_objects = [
        {
            "user": {
                "name": "John Doe",
                "age": "30",
                "contact": {"email": "john@example.com", "phone": "123-456-7890"},
                "addresses": [
                    {
                        "type": "home",
                        "zip": "10001",
                        "coordinates": {"lat": "40.7128", "lon": "-74.0060"},
                    },
                    {
                        "type": "work",
                        "zip": "94105",
                        "coordinates": {"lat": "37.7749", "lon": "-122.4194"},
                    },
                ],
            },
            "metadata": {
                "created_at": "2023-01-01T12:00:00Z",
                "is_active": "true",
                "score": "95.5",
            },
        }
    ]

    field_types = {
        "user": "object",
        "user.name": "text",
        "user.age": "long",
        "user.contact": "object",
        "user.contact.email": "text",
        "user.contact.phone": "text",
        "user.addresses": "nested",
        "user.addresses.type": "text",
        "user.addresses.zip": "long",
        "user.addresses.coordinates": "object",
        "user.addresses.coordinates.lat": "double",
        "user.addresses.coordinates.lon": "double",
        "metadata": "object",
        "metadata.created_at": "date",
        "metadata.is_active": "boolean",
        "metadata.score": "double",
    }

    converted = convert_es_field_types(json_objects, field_types)[0]

    assert converted["user"]["name"] == "John Doe"
    assert converted["user"]["age"] == 30
    assert converted["user"]["contact"]["email"] == "john@example.com"
    assert len(converted["user"]["addresses"]) == 2
    assert converted["user"]["addresses"][0]["zip"] == 10001
    assert converted["user"]["addresses"][0]["coordinates"]["lat"] == 40.7128
    assert converted["user"]["addresses"][1]["coordinates"]["lon"] == -122.4194
    assert converted["metadata"]["is_active"] is True
    assert converted["metadata"]["score"] == 95.5
    assert converted["metadata"]["created_at"] == "2023-01-01T12:00:00+00:00"


def test_convert_es_field_types_empty_values():
    """Test handling of empty and null values"""
    json_objects = [
        {
            "number_long": "",
            "number_double": None,
            "date_field": None,
            "text_field": "",
            "boolean_field": None,
        }
    ]

    field_types = {
        "number_long": "long",
        "number_double": "double",
        "date_field": "date",
        "text_field": "text",
        "boolean_field": "boolean",
    }

    converted = convert_es_field_types(json_objects, field_types)[0]

    assert converted["number_long"] == 0
    assert converted["number_double"] == 0
    assert (
        converted["date_field"]
        == datetime(2000, 1, 1, tzinfo=timezone(timedelta(hours=7))).isoformat()
    )
    assert converted["text_field"] == ""
    assert "boolean_field" in converted


def test_convert_es_field_types_date_formats():
    """Test conversion of different date formats"""
    json_objects = [
        {
            "date1": "2023-01-01T12:00:00Z",
            "date2": "1672574400",  # 2023-01-01 12:00:00
            "date3": "1672574400000",  # milliseconds
            "date4": "2023/01/01 12:00:00",
        }
    ]

    field_types = {
        "date1": "date",
        "date2": "date",
        "date3": "date",
        "date4": "date",
    }

    converted = convert_es_field_types(json_objects, field_types)[0]

    assert converted["date1"] == "2023-01-01T12:00:00+00:00"
    assert "2023-01-01" in converted["date2"]
    assert "2023-01-01" in converted["date3"]
    assert "2023-01-01" in converted["date4"]


def test_convert_es_field_types_numeric_conversions():
    """Test numeric type conversions"""
    json_objects = [
        {
            "long1": "123",
            "long2": 123.45,
            "double1": "123.45",
            "double2": 123,
        }
    ]

    field_types = {
        "long1": "long",
        "long2": "long",
        "double1": "double",
        "double2": "double",
    }

    converted = convert_es_field_types(json_objects, field_types)[0]

    assert converted["long1"] == 123
    assert converted["long2"] == 123
    assert converted["double1"] == 123.45
    assert converted["double2"] == 123.0


def test_convert_es_field_types_invalid_values():
    """Test handling of invalid values"""
    json_objects = [
        {
            "long_field": "not_a_number",
            "double_field": "invalid",
            "date_field": "invalid_date",
            "boolean_field": "not_a_bool",
        }
    ]

    field_types = {
        "long_field": "long",
        "double_field": "double",
        "date_field": "date",
        "boolean_field": "boolean",
    }

    converted = convert_es_field_types(json_objects, field_types)[0]

    # Invalid values should be preserved
    assert converted["long_field"] == "not_a_number"
    assert converted["double_field"] == "invalid"
    assert converted["date_field"] == "invalid_date"
    assert converted["boolean_field"] == False


def test_convert_es_field_types_boolean_values():
    """Test boolean value conversions"""
    json_objects = [
        {
            "bool1": "true",
            "bool2": "false",
            "bool3": True,
            "bool4": False,
            "bool5": "TRUE",
            "bool6": "FALSE",
        }
    ]

    field_types = {
        "bool1": "boolean",
        "bool2": "boolean",
        "bool3": "boolean",
        "bool4": "boolean",
        "bool5": "boolean",
        "bool6": "boolean",
    }

    converted = convert_es_field_types(json_objects, field_types)[0]

    assert converted["bool1"] is True
    assert converted["bool2"] is False
    assert converted["bool3"] is True
    assert converted["bool4"] is False
    assert converted["bool5"] is True
    assert converted["bool6"] is False
