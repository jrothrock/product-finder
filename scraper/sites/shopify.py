"""Module for scraping number of shopify stores for a particular category."""
import logging
import os
import re
import time

import broker
import utils.system as system
from database.db import Category as CategoryDB
from database.db import Database
from scraper.core.drivers import Driver

CATEGORY_SHOPIFY_QUEUE = (
    "test:queue:category:shopify" if os.getenv("TEST_ENV") else "queue:category:shopify"
)


class ShopifyCategory(Driver):
    """Class that holds procedures for scraping Shopify store counts."""

    def __init__(self):
        """Instantiate Selenium Driver and Redis."""
        super().__init__()
        self.redis = broker.redis()

    def _check_categories(self):
        """Check the Shopify category queue and process categories."""
        category_ids = self.redis.lrange(CATEGORY_SHOPIFY_QUEUE, 0, -1)
        self.redis.delete(CATEGORY_SHOPIFY_QUEUE)
        self._process_categories(category_ids)

    def _process_categories(self, category_ids):
        """Process the shopify categories."""
        for category_id in category_ids:
            try:
                self._get_shopify(category_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(
                    f"Exception scraping number of shopify sites: {e.__dict__}"
                )
                pass

    def _get_shopify(self, category_id):
        """Pull the shopify store count for a particular category from Google."""
        category = Database().session.query(CategoryDB).get(int(category_id))
        key_words = category.title.split("_")
        self.driver.get(
            "https://www.google.com/search?q=site%3Amyshopify.com+"
            + "+".join(key_words)
        )
        time.sleep(2)
        number_of_sites_elem = self.driver.find_element_by_xpath(
            "//div[contains(@id, 'result-stats')]"
        )
        number_of_shopify_sites = self._get_number_of_sites(
            number_of_sites_elem.get_attribute("innerHTML")
        )
        session = Database().session
        session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
            {
                "number_of_shopify_sites": number_of_shopify_sites,
            }
        )
        session.commit()
        session.close()

    def _get_number_of_sites(self, number_of_sites_elem_text):
        """Get integer number of stores from text body."""
        return int(
            re.search("About (.+) results", number_of_sites_elem_text)
            .group(1)
            .strip()
            .replace(",", "")
        )

    @classmethod
    def run(cls):
        """Public method for scraping Shopify store count for category."""
        cls()._check_categories()
