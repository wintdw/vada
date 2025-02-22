from libs.utils.common import friendlify_index_name


def test_friendlify_index_name():
    self.assertEqual(friendlify_index_name("csv_dw_csv"), "CSV dw")


def test_friendlify_index_name_with_mul_underscores():
    self.assertEqual(friendlify_index_name("csv_dw_dw_csv"), "CSV dw_dw")


def test_friendlify_index_name_empty_string():
    self.assertEqual(friendlify_index_name(""), "")
