from utils.database import Database
from IPython import embed

class Item(Database):
  UNIT_CONVERSION = {
    "CM": 2.54,
    "MM": 25.4,
    "IN": 1
  }

  def __init__(self):
    super().__init__()
    self.item()

  def new(self, **kwargs):
    title = self.create_title(kwargs["title_words"])
    dimensions_in_inches = self.dimensions(kwargs["dimensions"])
    weight = self.weight(kwargs["dimensions"])

    query = self.db.insert(self.item()).values(
      title=title,
      price=kwargs["price"],
      shipping_price=kwargs["shipping_price"],
      shipping_price_10_units=kwargs["shipping_price_10_units"],
      length=dimensions_in_inches["length"],
      width=dimensions_in_inches["width"],
      height=dimensions_in_inches["height"],
      weight=weight
    )

    self.connection.execute(query)


  def create_title(self, values):
    # TODO need to investigate why values is type None
    if values == None or len(values) == 0:
      return ""
    else:
      values.sort()
      return '_'.join(values)

  # Need to save dimensions as inches
  def dimensions(self,values):
    # TODO investigate better regex to pull measurements
    if values == None:
      return {"length": 0, "width": 0, "height": 0}

    divisor = self.UNIT_CONVERSION[values["measurement"].upper()]
    length_in_inches = values["length"] / divisor
    width_in_inches = values["width"] / divisor
    height_in_inches = values["height"] / divisor
    return {"length": length_in_inches, "width": width_in_inches, "height": height_in_inches}

  # TODO need to make a reasonable guess at weight based on dimensions
  def weight(self,values):
    return 5