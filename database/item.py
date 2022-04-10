"""Item module which holds procedures commonly used when creating item records."""
import logging
import os

from sqlalchemy.orm.exc import NoResultFound

import broker
import database.db
import utils.unit_conversions as unit_conversions
from database.db import Item as ItemDB

ITEM_AMAZON_FEES_QUEUE = (
    "test:queue:item:amazon:fees" if os.getenv("TEST_ENV") else "queue:item:amazon:fees"
)

ITEM_CALCULATOR_QUEUE = (
    "test:queue:item:calculator" if os.getenv("TEST_ENV") else "queue:item:calculator"
)


class Item(database.db.Database):
    """Class which holds procedures commonly used when creating item records."""

    def __init__(self):
        """Instantiate database communication and Redis."""
        super().__init__()
        self.redis = broker.redis()
        self.session = database.db.database_instance.get_session()

    def find_or_create(self, **kwargs):
        """Find or creates an item record based on the title."""
        try:
            item = (
                self.session.query(ItemDB)
                .filter_by(title=kwargs.get("title", ""))
                .one()
            )  # filter on name
        except NoResultFound:
            item = self.new(**kwargs)

        self.session.close()
        return item

    def new(self, **kwargs):
        """Create an item recored."""
        dimensions_in_inches = self._dimensions(kwargs["dimensions"])
        weight = self._weight_in_pounds(kwargs["weight"])
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
                amazon_category=kwargs["amazon_category"],
                available_quantity=kwargs["quantity"],
                unit_discount_percentage=kwargs.get("unit_discounts", {}).get(
                    "discount", None
                ),
                unit_discount_minimum_volume=kwargs.get("unit_discounts", {}).get(
                    "unit_discounts", None
                ),
            )
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
        """Normalize and convert dimensions when creating an item record."""
        # TODO investigate better regex to pull measurements
        if (
            values is None
            or values["measurement"] is None
            or values["measurement"] == ""
        ):
            return {"length": 0, "width": 0, "height": 0}

        length_in_inches = unit_conversions.convert_to_inches(
            values["length"], values["measurement"]
        )
        width_in_inches = unit_conversions.convert_to_inches(
            values["width"], values["measurement"]
        )
        height_in_inches = unit_conversions.convert_to_inches(
            values["height"], values["measurement"]
        )
        return {
            "length": length_in_inches,
            "width": width_in_inches,
            "height": height_in_inches,
        }

    def _weight_in_pounds(self, values):
        """Normalize and convert weight when creating an item record."""
        if values["weight"] is None or values["measurement"] is None:
            return 0

        return unit_conversions.convert_to_pounds(
            values["weight"], values["measurement"]
        )

    def _add_to_redis_queue(self, new_item):
        """Add item record id to Redis to be processed for Amazon fees or calculations."""
        if (
            new_item.length != 0
            and new_item.width != 0
            and new_item.height != 0
            and new_item.weight != 0
        ):
            self.redis.rpush(ITEM_AMAZON_FEES_QUEUE, new_item.id)
        else:
            self.redis.rpush(ITEM_CALCULATOR_QUEUE, new_item.id)
