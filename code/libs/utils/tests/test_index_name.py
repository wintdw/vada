from libs.utils.common import friendlify_index_name


def test_friendlify_index_name():
    friendly_index_name = friendlify_index_name("csv_dw_csv")
    assert friendly_index_name == "CSV dw"


def test_friendlify_index_name_with_mul_underscores():
    friendly_index_name = friendlify_index_name("csv_dw_dw_csv")
    assert friendly_index_name == "CSV dw_dw"


def test_friendlify_index_name_empty_string():
    friendly_index_name = friendlify_index_name("")
    assert friendly_index_name == ""
