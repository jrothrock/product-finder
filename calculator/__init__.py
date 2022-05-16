"""Subpackage for running profitability calculations on category and item records."""
import logging
import os

import broker as broker
import database.db
from database.db import Category as CategoryDB
from database.db import Item as ItemDB

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

ITEM_CALCULATOR_QUEUE = (
    "test:queue:item:calculator" if os.getenv("TEST_ENV") else "queue:item:calculator"
)

CATEGORY_CALCULATOR_QUEUE = (
    "test:queue:category:calculator"
    if os.getenv("TEST_ENV")
    else "queue:category:calculator"
)


class CategoryCalculator:
    """Class which holds procedures for running category profitability calculations."""

    def __init__(self):
        """Instantiate Redis."""
        self.redis = broker.redis()
        self.session = database.db.database_instance.get_session()

    def _check_categories(self) -> None:
        """Check for categories that need to have calculations performed."""
        category_ids = self.redis.lrange(CATEGORY_CALCULATOR_QUEUE, 0, -1)
        self.redis.delete(CATEGORY_CALCULATOR_QUEUE)
        self._process_categories(category_ids)

    def _process_categories(self, category_ids: list[str]) -> None:
        """Process categories and perform profitability calculations."""
        for category_id in category_ids:
            try:
                self._calculate_category(category_id)
            except Exception as e:
                logging.exception(f"Exception calculations catgory: {e.__dict__}")
                pass

    def _calculate_category(self, category_id: str) -> None:
        """Perform calculations on a category then updates the record."""
        category = self.session.query(CategoryDB).get(int(category_id))
        calculated_shipping_cost = self._calculate_shipping_cost(category_id)
        # will probably need to circle back on this. Probably too low of a breakeven.
        estimated_shipping_cost = (
            calculated_shipping_cost
            if calculated_shipping_cost
            else category.amazon_average_price * 0.1
        )
        average_min_break_even = (
            category.amazon_average_price - estimated_shipping_cost
        ) * (1 - GROSS_MARGIN_PERCENTAGE)
        average_min_break_even_amazon = average_min_break_even + category.amazon_fee
        self.session.query(CategoryDB).filter(CategoryDB.id == int(category_id)).update(
            {
                "average_min_break_even": average_min_break_even,
                "average_min_break_even_amazon": average_min_break_even_amazon,
            }
        )
        self.session.commit()

    def _calculate_shipping_cost(self, category_id: str) -> float:
        """Calculate shipping costs for a particular category."""
        records = (
            self.session.query(ItemDB, CategoryDB)
            .join(CategoryDB)
            .filter(CategoryDB.id == int(category_id))
            .all()
        )
        shipping_costs = []
        for record in records:
            shipping_costs.append(record.Item.shipping_price)

        average_shipping_cost = (
            sum(shipping_costs) / len(shipping_costs) if len(shipping_costs) else 0.0
        )
        return average_shipping_cost

    @classmethod
    def run(cls):
        """Public method for running item calculations on processable categories."""
        cls()._check_categories()


class ItemCalculator:
    """Class which holds procedures for running item profitability calculations."""

    def __init__(self):
        """Instantiate Redis."""
        self.redis = broker.redis()
        self.session = database.db.database_instance.get_session()

    def _check_items(self) -> None:
        """Check for items that need to have calculations performed."""
        item_ids = self.redis.lrange(ITEM_CALCULATOR_QUEUE, 0, -1)
        self.redis.delete(ITEM_CALCULATOR_QUEUE)
        self._process_items(item_ids)

    def _process_items(self, item_ids: list[str]) -> None:
        """Process items and perform profitability calculations."""
        for item_id in item_ids:
            try:
                self._calculate_item(item_id)
            except Exception as e:
                logging.exception(f"Exception calculations item: {e.__dict__}")
                pass

    def _calculate_item(self, item_id) -> None:
        """Perform calculations on an item and updates the record."""
        item = self.session.query(ItemDB).get(int(item_id))
        break_even_sale_price = item.price + item.shipping_price
        break_even_amazon_sale_price = (
            break_even_sale_price + item.amazon_fee if item.amazon_fee else None
        )

        self.session.query(ItemDB).filter(ItemDB.id == int(item_id)).update(
            {
                "break_even_sale_price": break_even_sale_price,
                "break_even_amazon_sale_price": break_even_amazon_sale_price,
            }
        )
        self.session.commit()

    @classmethod
    def run(cls):
        """Public method for running item calculations on processable items."""
        cls()._check_items()


def calculate_categories():
    """Easy to use interface for running category calculations."""
    CategoryCalculator.run()


def calculate_items():
    """Easy to use interface for running item calculations."""
    ItemCalculator.run()


def calculate_all():
    """Easy to use interface for running all calculations."""
    calculate_categories()
    calculate_items()
