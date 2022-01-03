import logging

import redis

import utils.system as system
from database.db import Database, Category as CategoryDB, Item as ItemDB

# AD_CONVERSION_PERCENTAGE = 0.02
# LOW_CPC_DOLLARS = 0.1
# MEDIUM_CPC_DOLLARS = 0.4
# HIGH_CPC_DOLLARS = 5
# RETURN_RATE_PERCENTAGE = 0.05
# SHOPIFY_MONTHLY_DOLLARS = 29.00
# RETURN_ON_AD_SPEND_PERCENTAGE = 400
# DOMAIN_YEARLY_DOLLARS = 15
# EMAIL_MONTHLY_DOLLARS = 7
# LLC_YEARLY_DOLLARS = 50
# VIRTUAL_ADDRESS_MONTHLY_DOLALRS = 30

# Would be 50%, but have the 10% included in guestimated shipping. However, see below comments.
GROSS_MARGIN_PERCENTAGE = 0.4

# May use later
# FIVERR_COPYWRITING_DESCRIPTION = 30 # 300 words at 10 cents a word
# PHOTOGRAPHY_COSTS?


class CategoryCalculator:
    def __init__(self):
        self.redis = redis.Redis()

    def _check_categories(self):
        category_ids = self.redis.lrange("queue:category:calculator", 0, -1)
        self.redis.delete("queue:category:calculator")
        self._process_categories(category_ids)

    def _process_categories(self, category_ids):
        for category_id in category_ids:
            try:
                self._calculate_category(category_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(f"Exception calculations catgory: {e.__dict__}")
                pass

    def _calculate_category(self, category_id):
        category = Database().session.query(CategoryDB).get(int(category_id))
        calculated_shipping_cost = self._calculate_shipping_cost(category_id)
        # will probably need to circle back on this. Probably too low of a breakeven.
        estimated_shipping_cost = (
            calculated_shipping_cost
            if calculated_shipping_cost
            else category.average_amazon_price * 0.1
        )
        average_min_break_even = (
            category.amazon_average_price - estimated_shipping_cost
        ) * (1 - GROSS_MARGIN_PERCENTAGE)
        average_min_break_even_amazon = average_min_break_even - category.amazon_fee
        session = Database().session
        session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
            {
                "average_min_break_even": average_min_break_even,
                "average_min_break_even_amazon": average_min_break_even_amazon,
            }
        )
        session.commit()
        session.close()

    def _calculate_shipping_cost(self, category_id):
        records = (
            Database()
            .session.query(ItemDB, CategoryDB)
            .join(CategoryDB)
            .filter(CategoryDB.id == category_id)
            .all()
        )
        shipping_costs = []
        for record in records:
            shipping_costs.append(record.Item.shipping_price)

        average_shipping_cost = (
            sum(shipping_costs) / len(shipping_costs) if len(shipping_costs) else None
        )
        return average_shipping_cost

    @classmethod
    def run(cls):
        cls()._check_categories()


class ItemCalculator:
    def __init__(self):
        self.redis = redis.Redis()

    def _check_items(self):
        item_ids = self.redis.lrange("queue:item:calculator", 0, -1)
        self.redis.delete("queue:item:calculator")
        self._process_items(item_ids)

    def _process_items(self, item_ids):
        for item_id in item_ids:
            try:
                self._calculate_item(item_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(f"Exception calculations item: {e.__dict__}")
                pass

    def _calculate_item(self, item_id):
        item = Database().session.query(ItemDB).get(int(item_id))
        break_even_sale_price = item.price + item.shipping_price
        break_even_amazon_sale_price = (
            break_even_sale_price + item.amazon_fee if item.amazon_fee else None
        )
        session = Database().session
        session.query(ItemDB).filter(ItemDB.id == item.id).update(
            {
                "break_even_sale_price": break_even_sale_price,
                "break_even_amazon_sale_price": break_even_amazon_sale_price,
            }
        )
        session.commit()
        session.close()

    @classmethod
    def run(cls):
        cls()._check_items()


def calculate_categories():
    CategoryCalculator.run()


def calculate_items():
    ItemCalculator.run()


def calculate_all():
    calculate_categories()
    calculate_items()
