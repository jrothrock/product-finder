import logging

from redis import Redis
from sqlalchemy.orm.exc import NoResultFound

import utils.system as system
from database.db import Item as ItemDB, Database as db

from IPython import embed


class Item(db):
    # convert to inches
    UNIT_CONVERSION_DIMENSIONS = {"cm": 2.54, "mm": 25.4, "in": 1}

    # convert to lbs
    UNIT_CONVERSION_WEIGHT = {"g": 453.592, "kg": 0.4535, "lb": 1}

    # density in lbs/in^3
    MATERIAL_DENSITY = {
        "wood": 0.02384,
        "plastic": 0.05,
        "steel": 0.29,
        "fabric": 0.06,
        "polyester": 0.05,
    }

    def __init__(self):
        super().__init__()

    def find_or_create(self, **kwargs):
        try:
            item = (
                self.session.query(ItemDB)
                .filter_by(title=kwargs.get("title", ""))
                .one()
            )  # filter on name
        except NoResultFound:
            item = self.new(**kwargs)

        return item

    def new(self, **kwargs):
        dimensions_in_inches = self._dimensions(kwargs["dimensions"])
        weight = self._weight(dimensions_in_inches, kwargs["weight_or_material"])
        amazon_category = self._amazon_category(kwargs["amazon_category"])
        try:
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
                image_url=kwargs["image_url"],
                category_id=kwargs["category_id"],
                amazon_category=amazon_category,
                available_quantity=kwargs["quantity"],
                unit_discount_percentage=kwargs.get("unit_discounts", {}).get(
                    "discount", None
                ),
                unit_discount_minimum_volume=kwargs.get("unit_discounts", {}).get(
                    "unit_discounts", None
                ),
            )
        except KeyboardInterrupt:
            system.exit()
        except Exception as e:
            logging.exception(f"Exception creating item: {e.__dict__}")
            pass

        self.session.add(new_item)
        self.session.commit()
        # Add to queue if item has dimensions and weight
        self._add_to_redis_queue(new_item)
        return new_item

    # Need to save dimensions as inches
    def _dimensions(self, values):
        # TODO investigate better regex to pull measurements
        if (
            values == None
            or values["measurement"] == None
            or values["measurement"] == ""
        ):
            return {"length": 0, "width": 0, "height": 0}

        divisor = self.UNIT_CONVERSION_DIMENSIONS[values["measurement"].lower()]
        length_in_inches = values["length"] / divisor
        width_in_inches = values["width"] / divisor
        height_in_inches = values["height"] / divisor
        return {
            "length": length_in_inches,
            "width": width_in_inches,
            "height": height_in_inches,
        }

    def _weight(self, dimensions, weight_or_material):
        if (
            weight_or_material["weight"] != None
            and weight_or_material["measurement"] != None
        ):
            return (
                weight_or_material["weight"]
                / self.UNIT_CONVERSION_WEIGHT[weight_or_material["measurement"].lower()]
            )

        # bail as we won't be able to calculate volume
        if (
            dimensions["length"] == 0
            or dimensions["width"] == 0
            or dimensions["height"] == 0
        ):
            return 0

        # an overestimate as the product is most likely not a cube
        volume = dimensions["length"] * dimensions["width"] * dimensions["height"]
        # fallback to steel density if material not identified
        density_of_item_per_cubic_inch = (
            0.29
            if weight_or_material["material"] == None
            else self.MATERIAL_DENSITY[weight_or_material["material"].lower()]
        )
        mass = volume * density_of_item_per_cubic_inch
        weight = mass * (9.81 * 0.4535)
        return weight

    def _amazon_category(self, category):
        if category == 1:
            return "Home and Garden (including Pet Supplies)"

    def _add_to_redis_queue(self, new_item):
        if (
            new_item.length != 0
            and new_item.width != 0
            and new_item.height != 0
            and new_item.weight != 0
        ):
            Redis().lpush("queue:item", new_item.id)
