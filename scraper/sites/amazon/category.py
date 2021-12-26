import redis
import time
import re
import logging

import utils.system as system
from scraper.core.drivers import Driver
from database.db import Database, Category as CategoryDB

from IPython import embed


class AmazonCategory(Driver):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()
        self._check_categories()

    def _check_categories(self):
        category_ids = self.redis.lrange("queue:category", 0, -1)
        # self.redis.delete("queue:category")
        self._process_categories(category_ids)

    def _process_categories(self, category_ids):
        for category_id in category_ids:
            try:
                self._get_amazon(category_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.log(f"Exception scraping number of shopify sites: {e.__dict__}")
                pass

    def _get_amazon(self, category_id):
        category = Database().session.query(CategoryDB).get(int(category_id))
        key_words = category.title.split("_")
        self.driver.get(
            "https://www.amazon.com/s?k=" + "+".join(key_words) + "&ref=nb_sb_noss"
        )
        time.sleep(2)
        number_of_products_elem = self.driver.find_element_by_xpath(
            "//div[contains(@class, 's-breadcrumb')]//div[contains(@class, 'a-spacing-top-small')]/*[1]"
        ).text
        amazon_total_results = self._get_number_of_products(number_of_products_elem)
        prices = [
            self._get_price_from_text(price_elem.get_attribute("innerHTML"))
            for price_elem in self.driver.find_elements_by_xpath(
                "//span[contains(@class, 'a-price')]//span[contains(@class, 'a-offscreen')]"
            )
        ]
        ratings = [
            self._get_review_from_text(rating_elem.get_attribute("innerHTML"))
            for rating_elem in self.driver.find_elements_by_xpath(
                "//div[contains(@class, 's-result-item')]//span[contains(@class, 'a-icon-alt')]"
            )
        ]
        number_of_ratings = [
            self._get_number_of_ratings_from_text(
                num_rating_elem.get_attribute("innerHTML")
            )
            for num_rating_elem in self.driver.find_elements_by_xpath(
                "//div[contains(@class, 's-result-list')]//div[contains(@class, 'a-section')]//div[contains(@class, 'a-row')]//span/a[contains(@class, 'a-link-normal')]//span[contains(@class, 'a-size-base')]"
            )
        ]
        prices = list(filter(lambda x: x is not None, prices))
        ratings = list(filter(lambda x: x is not None, ratings))
        number_of_ratings = list(filter(lambda x: x is not None, number_of_ratings))
        amazon_min_price = min(prices) if len(prices) else None
        amazon_max_price = max(prices) if len(prices) else None
        amazon_average_price = (sum(prices) / len(prices)) if len(prices) else None
        amazon_min_rating = min(ratings) if len(ratings) else None
        amazon_max_rating = max(ratings) if len(ratings) else None
        amazon_average_rating = (sum(ratings) / len(ratings)) if len(ratings) else None
        amazon_average_number_of_ratings = (
            (sum(number_of_ratings) / len(number_of_ratings))
            if len(number_of_ratings)
            else None
        )
        session = Database().session
        session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
            {
                "amazon_total_results": int(amazon_total_results),
                "amazon_min_price": amazon_min_price,
                "amazon_max_price": amazon_max_price,
                "amazon_average_price": amazon_average_price,
                "amazon_min_rating": amazon_min_rating,
                "amazon_max_rating": amazon_max_rating,
                "amazon_average_rating": amazon_average_rating,
                "amazon_average_number_of_ratings": amazon_average_number_of_ratings,
            }
        )
        session.commit()
        session.close()
        self.redis.lpush("queue:shopify", category.id)
        self.redis.lpush("queue:item_calculator", category.id)

    def _get_price_from_text(self, price_text):
        return float(price_text[1:-1].strip().replace(",", ""))

    def _get_number_of_products(self, number_of_products_text):
        return int(
            re.search("of (over)?(.+) results", number_of_products_text)
            .group(2)
            .strip()
            .replace(",", "")
        )

    def _get_review_from_text(self, review_text):
        return float(re.search("(.+) (out|Stars)", review_text).group(1))

    def _get_number_of_ratings_from_text(self, num_ratings_text):
        return int(num_ratings_text.strip().replace(",", ""))

    @classmethod
    def run(cls):
        cls()
