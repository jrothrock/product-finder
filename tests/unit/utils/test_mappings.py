import pytest

import utils.mappings as mappings


@pytest.mark.parametrize(
    "test_input, expected",
    [("0", None), ("1", "Home and Garden (including Pet Supplies)")],
)
def test_map_amazon_category(test_input, expected):
    category = mappings.map_amazon_category(test_input)
    assert category == expected
