import logging

import redis
from sqlalchemy.orm.exc import NoResultFound
from IPython import embed

import utils.system as system
import utils.unit_conversions as unit_conversions
from database.db import Item as ItemDB, Database as db


class Item(db):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()

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
        weight = self._weight_in_pounds(kwargs["weight"])
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

        length_in_inches = unit_conversions.convert_to_inches(values["length"], values["measurement"])
        width_in_inches = unit_conversions.convert_to_inches(values["width"], values["measurement"])
        height_in_inches = unit_conversions.convert_to_inches(values["height"], values["measurement"])
        return {
            "length": length_in_inches,
            "width": width_in_inches,
            "height": height_in_inches,
        }

    def _weight_in_pounds(self, values):
        if (
            values["weight"] == None
            or values["measurement"] == None
        ):
            return 0
        
        return unit_conversions.convert_to_pounds(values["weight"], values["measurement"])

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
            self.redis.rpush("queue:item:amazon:fees", new_item.id)
