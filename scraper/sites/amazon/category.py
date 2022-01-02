import time
import re
import logging
import statistics

import redis
from IPython import embed

import utils.system as system
import utils.language_utils as language_utils
import utils.unit_conversions as unit_conversions
from scraper.core.drivers import Driver
from database.db import Database, Category as CategoryDB


class AmazonCategory(Driver):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()

    def _check_categories(self):
        category_ids = self.redis.lrange("queue:category:amazon:listings", 0, -1)
        self.redis.delete("queue:category:amazon:listings")
        self._process_categories(category_ids)

    def _process_categories(self, category_ids):
        for category_id in category_ids:
            try:
                self._get_amazon_category(category_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(f"Exception scraping amazon categories: {e.__dict__}")
                pass

    def _get_amazon_category(self, category_id):
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
        amazon_deviation_price = statistics.pstdev(prices) if len(prices) else None
        amazon_average_price = (sum(prices) / len(prices)) if len(prices) else None
        amazon_min_rating = min(ratings) if len(ratings) else None
        amazon_max_rating = max(ratings) if len(ratings) else None
        amazon_deviation_rating = statistics.pstdev(ratings) if len(ratings) else None
        amazon_average_rating = (sum(ratings) / len(ratings)) if len(ratings) else None
        amazon_average_number_of_ratings = (
            (sum(number_of_ratings) / len(number_of_ratings))
            if len(number_of_ratings)
            else None
        )
        try:
            category_dimensions_and_weight_dict = (
                self._get_category_dimensions_and_weight()
            )
        except KeyboardInterrupt:
            system.exit()
        except Exception as e:
            logging.exception(
                f"Exception getting category dimensions and weight: {e.__dict__}"
            )
            category_dimensions_and_weight_dict = {}

        session = Database().session
        session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
            {
                "amazon_total_results": int(amazon_total_results),
                "amazon_min_price": amazon_min_price,
                "amazon_max_price": amazon_max_price,
                "amazon_deviation_price": amazon_deviation_price,
                "amazon_average_price": amazon_average_price,
                "amazon_min_rating": amazon_min_rating,
                "amazon_max_rating": amazon_max_rating,
                "amazon_deviation_rating": amazon_deviation_rating,
                "amazon_average_rating": amazon_average_rating,
                "amazon_average_number_of_ratings": amazon_average_number_of_ratings,
                "amazon_average_length": category_dimensions_and_weight_dict.get(
                    "amazon_average_length", None
                ),
                "amazon_average_width": category_dimensions_and_weight_dict.get(
                    "average_average_width", None
                ),
                "amazon_average_height": category_dimensions_and_weight_dict.get(
                    "amazon_average_height", None
                ),
                "amazon_deviation_dimensions": category_dimensions_and_weight_dict.get(
                    "amazon_deviation_dimensions", None
                ),
                "amazon_average_weight": category_dimensions_and_weight_dict.get(
                    "amazon_average_weight", None
                ),
                "amazon_deviation_weight": category_dimensions_and_weight_dict.get(
                    "amazon_deviation_weight", None
                ),
            }
        )
        session.commit()
        session.close()
        self.redis.rpush("queue:category:shopify", category.id)

        if len(category_dimensions_and_weight_dict.keys()):
            self.redis.rpush("queue:category:amazon:fees", category.id)

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

    def _get_category_dimensions_and_weight(self):
        product_link_elems = self.driver.find_elements_by_xpath(
            "//div[contains(@class, 's-result-list')]//div[contains(@class, 'a-section')]//h2/a[contains(@class, 'a-link-normal')]"
        )
        product_links = [
            product_link_elem.get_attribute("href")
            for product_link_elem in product_link_elems
        ]

        return self._calculate_dimensions_and_weight(product_links)

    def _calculate_dimensions_and_weight(self, product_links):
        category_lengths = []
        category_widths = []
        category_heights = []
        category_weights = []

        # uses higher than 3 to eliminate sponsored products
        for product_link in product_links[4:7]:
            product_dimensions_and_weight = (
                self._get_amazon_product_dimensions_and_weight(product_link)
            )
            category_lengths.append(product_dimensions_and_weight.get("length", None))
            category_widths.append(product_dimensions_and_weight.get("width", None))
            category_heights.append(product_dimensions_and_weight.get("height", None))
            category_weights.append(product_dimensions_and_weight.get("weight", None))

        category_dimensions = [
            l * w * h
            for l, w, h in zip(category_lengths, category_widths, category_heights)
        ]

        amazon_average_length = (
            (sum(category_lengths) / len(category_lengths))
            if len(category_lengths)
            else None
        )
        amazon_average_width = (
            (sum(category_widths) / len(category_widths))
            if len(category_widths)
            else None
        )
        amazon_average_height = (
            (sum(category_heights) / len(category_heights))
            if len(category_heights)
            else None
        )
        amazon_deviation_height = (
            statistics.pstdev(category_dimensions) if len(category_dimensions) else None
        )
        amazon_average_weight = (
            (sum(category_weights) / len(category_weights))
            if len(category_weights)
            else None
        )
        amazon_deviation_weight = (
            statistics.pstdev(category_weights) if len(category_dimensions) else None
        )

        return {
            "amazon_average_length": amazon_average_length,
            "amazon_average_width": amazon_average_width,
            "amazon_average_height": amazon_average_height,
            "amazon_deviation_dimensions": amazon_deviation_height,
            "amazon_average_weight": amazon_average_weight,
            "amazon_deviation_weight": amazon_deviation_weight,
        }

    def _get_amazon_product_dimensions_and_weight(self, url):
        self.driver.get(url)
        product_details_elem = self.driver.find_element_by_xpath(
            "//table[contains(@id, 'productDetails_detailBullets_sections1')]"
        )
        dimensions = language_utils.get_dimensions(
            product_details_elem.get_attribute("innerHTML")
        )
        weight = language_utils.get_weight(
            product_details_elem.get_attribute("innerHTML")
        )

        length_in_inches = unit_conversions.convert_to_inches(
            dimensions["length"], dimensions["measurement"]
        )
        width_in_inches = unit_conversions.convert_to_inches(
            dimensions["width"], dimensions["measurement"]
        )
        height_in_inches = unit_conversions.convert_to_inches(
            dimensions["height"], dimensions["measurement"]
        )
        weight_in_pounds = unit_conversions.convert_to_pounds(
            weight["weight"], weight["measurement"]
        )

        return {
            "length": length_in_inches,
            "width": width_in_inches,
            "height": height_in_inches,
            "weight": weight_in_pounds,
        }

    @classmethod
    def run(cls):
        cls()._check_categories()