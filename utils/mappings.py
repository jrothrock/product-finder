"""Utility module used for mapping the categories between aliexpress, amazon, etc."""
import os

import yaml


# Not super performant. May want to revisit.
def get_category_mappings():
    """Get the mappings for a particular category."""
    path = os.path.relpath("./utils/mappings/category_mappings.yaml")
    with open(path) as stream:
        return yaml.safe_load(stream)


def map_amazon_category(category):
    """Get mapped Amazon category."""
    category_mappings = get_category_mappings()
    return (
        category_mappings["categories"].get(category, {}).get("amazon_category", None)
    )
