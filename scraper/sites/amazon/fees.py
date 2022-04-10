"""Module for scraping AmazonFees -- Category and Item."""
import logging
import os
import time

import broker
import database.db
import scraper.core.drivers
import utils.mappings as mappings
from database.db import Category as CategoryDB
from database.db import Item as ItemDB

ITEM_AMAZON_FEES_QUEUE = (
    "test:queue:item:amazon:fees" if os.getenv("TEST_ENV") else "queue:item:amazon:fees"
)

ITEM_CALCULATOR_QUEUE = (
    "test:queue:item:calculator" if os.getenv("TEST_ENV") else "queue:item:calculator"
)

CATEGORY_CALCULATOR_QUEUE = (
    "test:queue:category:calculator"
    if os.getenv("TEST_ENV")
    else "queue:category:calculator"
)

CATEGORY_AMAZON_FEES_QUEUE = (
    "test:queue:category:amazon:fees"
    if os.getenv("TEST_ENV")
    else "queue:category:amazon:fees"
)


class AmazonFee:
    """Class that holds procedures for scraping Amazon fees."""

    def __init__(self):
        """Set redis, database and driver instances."""
        self.redis = broker.redis()
        self.session = database.db.database_instance.get_session()
        self.driver = scraper.core.drivers.driver_instance.get_driver()

    def _check_categories(self):
        """Check the Amazon category fees queue and process the categories."""
        category_ids = self.redis.lrange(CATEGORY_AMAZON_FEES_QUEUE, 0, -1)
        self.redis.delete(CATEGORY_AMAZON_FEES_QUEUE)
        self._process_record(category_ids, CategoryDB)

    def _check_items(self):
        """Check the Amazon item fees queue and process the items."""
        item_ids = self.redis.lrange(ITEM_AMAZON_FEES_QUEUE, 0, -1)
        self.redis.delete(ITEM_AMAZON_FEES_QUEUE)
        self._process_record(item_ids, ItemDB)

    def _process_record(self, record_ids, db_klass):
        for record_id in record_ids:
            try:
                self._get_amazon(record_id, db_klass)
            except Exception as e:
                self._add_to_redis_queue(record_id, db_klass)
                logging.exception(
                    f"Exception scraping amazon category fees: {e.__dict__}"
                )
                pass

    def _add_to_redis_queue(self, record_id, db_klass):
        if db_klass == ItemDB:
            self.redis.rpush(ITEM_CALCULATOR_QUEUE, record_id)
        else:
            self.redis.rpush(CATEGORY_CALCULATOR_QUEUE, record_id)

    def _get_amazon(self, record_id, db_klass):
        """Scrape the amazon page for a particular category or item."""
        time.sleep(1)
        record = self.session.query(db_klass).get(int(record_id))
        self.driver.get(
            "https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index?lang=en_US"
        )
        time.sleep(1)

        self.driver.find_element_by_xpath(
            "//input[contains(@aria-labelledby, 'link_continue-announce')]"
        ).click()

        record_length = (
            record.length
            if isinstance(record, ItemDB)
            else record.amazon_average_length
        )

        self.driver.find_element_by_id("product-length").send_keys(
            str(round(record_length, 2))
        )

        record_width = (
            record.width if isinstance(record, ItemDB) else record.amazon_average_width
        )
        self.driver.find_element_by_id("product-width").send_keys(
            str(round(record_width, 2))
        )

        record_height = (
            record.height
            if isinstance(record, ItemDB)
            else record.amazon_average_height
        )
        self.driver.find_element_by_id("product-height").send_keys(
            str(round(record_height, 2))
        )

        record_weight = (
            record.weight
            if isinstance(record, ItemDB)
            else record.amazon_average_weight
        )
        self.driver.find_element_by_id("product-weight").send_keys(
            str(round(record_weight, 2))
        )

        self.driver.find_element_by_xpath(
            "//span[contains(text(), 'Select category')]"
        ).click()

        mapped_amazon_category = mappings.map_amazon_category(record.amazon_category)

        self.driver.find_element_by_xpath(
            "//a[contains(text(), '" + mapped_amazon_category + "')]"
        ).click()

        self.driver.find_element_by_id("estimate-new-announce").click()

        self.driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight - 250);"
        )

        time.sleep(1)
        amazon_fees = self.driver.find_element_by_id(
            "afn-seller-proceeds"
        ).get_attribute("value")
        self.session.query(db_klass).filter(db_klass.id == record.id).update(
            {"amazon_fee": float(amazon_fees[1:])}
        )
        self.session.commit()

        self._add_to_redis_queue(record_id, db_klass)

        self.driver.delete_all_cookies()

    @classmethod
    def run_item_fees(cls):
        """Public method to instantiate scraping Amazon fees for items."""
        cls()._check_items()

    @classmethod
    def run_category_fees(cls):
        """Public method to instantiate scraping Amazon fees for categories."""
        cls()._check_categories()
