import json

from libs.utils.es_field_types import (
    determine_es_field_types,
    determine_and_convert_es_field_types,
    construct_es_mappings,
)

json_lines = [
    {
        "name": "Alice",
        "age": 30,
        "is_student": "false",
        "scores": [95, 85],
        "address": {"city": "New York", "zip": "10001"},
        "created_at": "2023-10-01T12:34:56Z",
    },
    {
        "name": "Bob",
        "age": "25",
        "is_student": "true",
        "scores": [88, 92],
        "address": {"city": "San Francisco", "zip": "94105"},
        "created_at": "2023-09-15T08:00:00Z",
    },
    {
        "name": "Charlie",
        "age": 35,
        "is_student": "false",
        "scores": [90, 80],
        "address": {"city": "Chicago", "zip": "60601"},
        "created_at": "2023-08-20T15:30:00Z",
    },
    {
        "name": "Dave",
        "age": "40.5",
        "is_student": "true",
        "scores": [85, 95],
        "tags": ["engineer", "developer"],
        "address": {"city": "Seattle", "zip": "98101"},
        "created_at": "2023-07-01T00:00:00Z",
    },
    {
        "name": "Eve",
        "age": 28,
        "is_student": "false",
        "scores": [95, 90],
        "contacts": [
            {"type": "email", "value": "eve@example.com"},
            {"type": "phone", "value": "123-456-7890"},
        ],
        "created_at": "2023-06-01T12:00:00Z",
    },
    {"timestamp": "1609459200"},
    {"timestamp": ""},
    {
        "price": "123.45",
        "discount": "10",
    },
    {"price": ""},
    {"price": ""},
    {"another_date": 1753894800000},
    {"another_date": "2025-01-15 15:46:56"},
]


def test_determine_es_field_types():
    field_types = determine_es_field_types(json_lines)
    expected_field_types = {
        "name": "text",
        "age": "double",
        "is_student": "boolean",
        "scores": "unknown",
        "address": "object",
        "address.city": "text",
        "address.zip": "long",
        "created_at": "date",
        "tags": "unknown",
        "contacts": "nested",
        "contacts.type": "text",
        "contacts.value": "text",
        "timestamp": "date",
        "price": "double",
        "discount": "long",
        "another_date": "date",
    }

    print(json.dumps(field_types, indent=4))
    assert field_types == expected_field_types


def test_determine_and_convert_es_field_types():
    converted_json_lines = determine_and_convert_es_field_types(json_lines)

    expected_converted_json_lines = [
        {
            "name": "Alice",
            "age": 30.0,
            "is_student": False,
            "scores": [95, 85],
            "address": {"city": "New York", "zip": 10001},
            "created_at": "2023-10-01T19:34:56+07:00",
        },
        {
            "name": "Bob",
            "age": 25.0,
            "is_student": True,
            "scores": [88, 92],
            "address": {"city": "San Francisco", "zip": 94105},
            "created_at": "2023-09-15T15:00:00+07:00",
        },
        {
            "name": "Charlie",
            "age": 35.0,
            "is_student": False,
            "scores": [90, 80],
            "address": {"city": "Chicago", "zip": 60601},
            "created_at": "2023-08-20T22:30:00+07:00",
        },
        {
            "name": "Dave",
            "age": 40.5,
            "is_student": True,
            "scores": [85, 95],
            "tags": ["engineer", "developer"],
            "address": {"city": "Seattle", "zip": 98101},
            "created_at": "2023-07-01T07:00:00+07:00",
        },
        {
            "name": "Eve",
            "age": 28.0,
            "is_student": False,
            "scores": [95, 90],
            "contacts": [
                {"type": "email", "value": "eve@example.com"},
                {"type": "phone", "value": "123-456-7890"},
            ],
            "created_at": "2023-06-01T19:00:00+07:00",
        },
        {"timestamp": "2021-01-01T07:00:00+07:00"},
        {"timestamp": "2000-01-01T00:00:00+07:00"},
        {"price": 123.45, "discount": 10},
        {"price": 0},
        {"price": 0},
        {"another_date": "2025-07-31T00:00:00+07:00"},
        {"another_date": "2025-01-15T15:46:56+07:00"},
    ]

    print(json.dumps(converted_json_lines, indent=4))
    assert converted_json_lines == expected_converted_json_lines


def test_construct_es_mappings():
    field_types = determine_es_field_types(json_lines)

    expected_mappings = {
        "mappings": {
            "dynamic": True,
            "dynamic_date_formats": [
                "strict_date_optional_time",
                "basic_date",
                "basic_date_time",
                "basic_date_time_no_millis",
                "yyyy/MM/dd HH:mm:ss",
            ],
            "properties": {
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256,
                            "eager_global_ordinals": True,
                        }
                    },
                },
                "address": {"type": "object", "properties": {}},
                "created_at": {"type": "date", "ignore_malformed": True},
                "contacts": {"type": "nested", "properties": {}},
                "timestamp": {"type": "date", "ignore_malformed": True},
                "another_date": {"type": "date", "ignore_malformed": True},
            },
        }
    }

    es_mappings = construct_es_mappings(field_types)
    print(json.dumps(es_mappings, indent=4))
    assert es_mappings == expected_mappings
