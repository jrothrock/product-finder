from utils.database import Item as ItemDB
from utils.database import Database as db
from IPython import embed
from sqlalchemy.orm.exc import NoResultFound
class Item(db):
  UNIT_CONVERSION = {
    "CM": 2.54,
    "MM": 25.4,
    "IN": 1
  }

  def __init__(self):
    super().__init__()

  def find_or_create(self, **kwargs):
    try:
      item = self.session.query(ItemDB).filter_by(title=kwargs["title"]).one() # filter on name
    except NoResultFound:
      item = self.new(**kwargs)
    
    return item


  def new(self, **kwargs):
    dimensions_in_inches = self.dimensions(kwargs["dimensions"])
    weight = self.weight(kwargs["dimensions"])

    new_item = ItemDB(
      title=kwargs["title"], 
      price=kwargs["price"],
      shipping_price=kwargs["shipping_price"],
      shipping_price_10_units=kwargs["shipping_price_10_units"],
      length=dimensions_in_inches["length"],
      width=dimensions_in_inches["width"],
      height=dimensions_in_inches["height"],
      weight=weight,
      url=kwargs["url"],
      category_id=kwargs["category_id"]
    )

    self.session.add(new_item)
    self.session.commit()
    return new_item


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
  