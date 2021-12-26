import redis
import time
import re
import logging

import utils.system as system
from scraper.core.drivers import Driver

from database.db import Database, Category as CategoryDB

from IPython import embed


class ShopifyCategory(Driver):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()
        self._check_categories()

    def _check_categories(self):
        category_ids = self.redis.lrange("queue:shopify", 0, -1)
        # self.redis.delete("queue:shopify")
        self._process_categories(category_ids)

    def _process_categories(self, category_ids):
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

    def _get_number_of_sites(self, number_of_sites_elem):
        return int(
            re.search("About (.+) results", number_of_sites_elem)
            .group(1)
            .strip()
            .replace(",", "")
        )

    @classmethod
    def run(cls):
        cls()
