import pytest

import utils.unit_conversions as unit_conversions


@pytest.mark.parametrize(
    "test_input, expected",
    [([2.54, "cm"], 1), ([1, "in"], 1)],
)
def test_convert_to_inches(test_input, expected):
    result = unit_conversions.convert_to_inches(test_input[0], test_input[1])
    assert result == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [([16, "oz"], 1), ([1, "lb"], 1)],
)
def test_convert_to_pounds(test_input, expected):
    result = unit_conversions.convert_to_pounds(test_input[0], test_input[1])
    assert result == expected
