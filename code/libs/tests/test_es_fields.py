from es_utils import determine_es_field_types


def test_determine_es_field_types():
    json_lines = [
        '{"name": "Alice", "age": 30, "is_student": false, "scores": [95, 85], "binary_data": "aGVsbG8=", "address": {"city": "New York", "zip": "10001"}, "created_at": "2023-10-01T12:34:56Z"}',  # Base64 for "hello"
        '{"name": "Bob", "age": 25, "is_student": true, "scores": [88, 92], "binary_data": "d29ybGQ=", "address": {"city": "San Francisco", "zip": "94105"}, "created_at": "2023-09-15T08:00:00Z"}',  # Base64 for "world"
        '{"name": "Charlie", "age": 35, "is_student": false, "scores": [90, 80], "binary_data": "Zm9v", "address": {"city": "Chicago", "zip": "60601"}, "created_at": "2023-08-20T15:30:00Z"}',  # Base64 for "foo"
        '{"name": "Dave", "age": 40.5, "is_student": true, "scores": [85, 95], "tags": ["engineer", "developer"], "address": {"city": "Seattle", "zip": "98101"}, "created_at": "2023-07-01T00:00:00Z"}',
        '{"name": "Eve", "age": 28, "is_student": false, "scores": [95, 90], "contacts": [{"type": "email", "value": "eve@example.com"}, {"type": "phone", "value": "123-456-7890"}], "created_at": "2023-06-01T12:00:00Z"}',
        '{"timestamp": 1609459200}',  # A timestamp (Unix epoch time for 2021-01-01T00:00:00Z)
        '{"price": "123.45", "discount": "10"}',  # Price as string "123.45" and discount as string "10"
        '{"price": ""}',
        '{"price": ""}',
    ]

    field_types = determine_es_field_types(json_lines)
    expected_field_types = {
        "name": "keyword",
        "age": "long",
        "is_student": "boolean",
        "scores": "unknown",
        "binary_data": "binary",
        "address": "nested",
        "created_at": "date",
        "tags": "keyword",
        "contacts": "nested",
        "timestamp": "date",
        "price": "double",
        "discount": "long",
    }
    assert field_types == expected_field_types
