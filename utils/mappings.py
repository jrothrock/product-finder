import os

import yaml
from IPython import embed

# Not super performant. May want to revisit.
def get_category_mappings():
  path = os.path.relpath("./utils/mappings/category_mappings.yaml")
  with open(path) as stream:
      return yaml.safe_load(stream)

def map_amazon_category(category):
    category_mappings = get_category_mappings()
    return category_mappings["categories"].get(category, {}).get("amazon_category", None)
