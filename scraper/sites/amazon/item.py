import redis
import time
import logging

import utils.system as system
from scraper.core.drivers import Driver
from database.db import Database, Item as ItemDB

from IPython import embed


class AmazonItem(Driver):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()
        self.check_items()

    def _check_items(self):
        item_ids = self.redis.lrange("queue:item", 0, -1)
        self.redis.delete("queue:item")
        self._process_items(item_ids)

    def _process_items(self, item_ids):
        for item_id in item_ids:
            try:
                self._get_amazon(item_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(
                    f"Exception scraping number of shopify sites: {e.__dict__}"
                )
                pass

    def _get_amazon(self, item_id):
        time.sleep(1)
        item = Database().session.query(ItemDB).get(int(item_id))
        self.driver.get(
            "https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index?lang=en_US"
        )
        time.sleep(1)
        self.driver.find_element_by_xpath(
            "//input[contains(@aria-labelledby, 'link_continue-announce')]"
        ).click()
        self.driver.find_element_by_id("product-length").send_keys(
            str(round(item.length, 2))
        )
        self.driver.find_element_by_id("product-width").send_keys(
            str(round(item.width, 2))
        )
        self.driver.find_element_by_id("product-height").send_keys(
            str(round(item.height, 2))
        )
        self.driver.find_element_by_id("product-weight").send_keys(
            str(round(item.weight, 2))
        )
        self.driver.find_element_by_xpath(
            "//span[contains(text(), 'Select category')]"
        ).click()
        self.driver.find_element_by_xpath(
            "//a[contains(text(), '" + item.amazon_category + "')]"
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
        session.query(ItemDB).filter(ItemDB.id == item.id).update(
            {"amazon_fee": float(amazon_fees[1:])}
        )
        session.commit()
        session.close()
        self.driver.delete_all_cookies()

    @classmethod
    def run(cls):
        cls()
