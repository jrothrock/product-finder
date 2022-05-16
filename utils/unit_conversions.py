"""Utility module used for converting various units."""
UNIT_CONVERSION_DIMENSIONS = {"cm": 2.54, "mm": 25.4, "in": 1}
UNIT_CONVERSION_WEIGHT = {
    "g": 453.592,
    "kg": 0.4535,
    "oz": 16.0,
    "lb": 1.0,
    "pound": 1.0,
    "ounce": 16.0,
}


def convert_to_inches(value: float, unit: str = "in") -> float:
    """Convert common measurement units to inches."""
    divisor = UNIT_CONVERSION_DIMENSIONS[unit.lower()]
    return value / divisor


def convert_to_pounds(value: float, unit: str = "lb") -> float:
    """Convert common weight measurement units to pounds."""
    divisor = UNIT_CONVERSION_WEIGHT[unit.lower()]
    return value / divisor
