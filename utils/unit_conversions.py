UNIT_CONVERSION_DIMENSIONS = {"cm": 2.54, "mm": 25.4, "in": 1}
UNIT_CONVERSION_WEIGHT = {"g": 453.592, "kg": 0.4535, "oz": 16, "lb": 1, "pound": 1, "ounce": 16}

def convert_to_inches(value, unit):
    divisor = UNIT_CONVERSION_DIMENSIONS[unit.lower()]
    return value / divisor


def convert_to_pounds(value, unit):
    divisor = UNIT_CONVERSION_WEIGHT[unit.lower()]
    return value / divisor
