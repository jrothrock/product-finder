"""Module for scraping AmazonFees -- Category and Item."""
import time
import logging

import redis

import utils.system as system
import utils.mappings as mappings
from scraper.core.drivers import Driver
from database.db import Database, Item as ItemDB, Category as CategoryDB


class AmazonFee(Driver):
    """Class that holds procedures for scraping Amazon fees."""

    def __init__(self):
        """Instantiate Selenium Driver and Redis."""
        super().__init__()
        self.redis = redis.Redis()

    def _check_categories(self):
        """Check the Amazon category fees queue and process the categories."""
        category_ids = self.redis.lrange("queue:category:amazon:fees", 0, -1)
        self.redis.delete("queue:category:amazon:fees")
        self._process_record(category_ids, CategoryDB)

    def _check_items(self):
        """Check the Amazon item fees queue and process the items."""
        item_ids = self.redis.lrange("queue:item:amazon:fees", 0, -1)
        self.redis.delete("queue:item:amazon:fees")
        self._process_record(item_ids, ItemDB)

    def _process_record(self, record_ids, db_klass):
        for record_id in record_ids:
            try:
                self._get_amazon(record_id, db_klass)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(
                    f"Exception scraping number of shopify sites: {e.__dict__}"
                )
                pass

    def _get_amazon(self, record_id, db_klass):
        """Scrape the amazon page for a particular category or item."""
        time.sleep(1)
        record = Database().session.query(db_klass).get(int(record_id))
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
        session = Database().session
        session.query(db_klass).filter(db_klass.id == record.id).update(
            {"amazon_fee": float(amazon_fees[1:])}
        )
        session.commit()
        session.close()
        if isinstance(record, ItemDB):
            self.redis.rpush("queue:item:calculator", record.id)
        else:
            self.redis.rpush("queue:category:calculator", record.id)

        self.driver.delete_all_cookies()

    @classmethod
    def run_item_fees(cls):
        """Public method to instantiate scraping Amazon fees for items."""
        cls()._check_items()

    @classmethod
    def run_category_fees(cls):
        """Public method to instantiate scraping Amazon fees for categories."""
        cls()._check_categories()
