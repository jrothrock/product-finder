"""Module for scraping Aliexpress products."""
import logging
import re
import time

import selenium

import utils.language_utils as language_utils
import utils.mappings as mappings
import utils.system as system
from database.category import Category as CategoryModel
from database.item import Item as ItemModel
from scraper.core.drivers import EC
from scraper.core.drivers import By
from scraper.core.drivers import Driver
from scraper.core.drivers import WebDriverWait


class Aliexpress(Driver):
    """Class that holds procedures for scraping Aliexpress products."""

    def __init__(self):
        """Instantiate Selenium Driver and Redis. Cache category and item models."""
        super().__init__()
        self.category = CategoryModel()
        self.item = ItemModel()

    def _scrape_pages(self):
        """Scrape Aliexpress pages and pull prductk links."""
        category_mappings = mappings.get_category_mappings()
        category_mapping_keys = category_mappings.get("categories", {}).keys()
        for category_id in category_mapping_keys:
            amazon_url = (
                category_mappings.get("categories", {})
                .get(category_id, {})
                .get("aliexpress_url", None)
            )
            self.driver.get(amazon_url)
            amazon_category = int(category_id)
            pages = 0
            while True:
                current_url = self.driver.current_url
                self.driver.execute_script(
                    "window.scrollTo(0,document.body.scrollHeight);"
                )
                url_elements = self.driver.find_elements_by_xpath(
                    "//div[contains(@class, 'product-container')]//a[.//h1]"
                )
                urls = [url_elem.get_attribute("href") for url_elem in url_elements]
                for link in urls:
                    try:
                        self._scrape_page(link, amazon_category)
                    except selenium.common.exceptions.TimeoutException:
                        logging.exception(
                            "Timeout occurred on page. Items may not have been found. Passing"
                        )
                        pass
                    except Exception as e:
                        logging.exception(
                            f"Exception scraping aliexpress page: {e.__dict__}"
                        )
                        pass

                self.driver.get(current_url)
                self.driver.execute_script(
                    "window.scrollTo(0,document.body.scrollHeight - 1750);"
                )
                pages += 1

                if pages >= 1:
                    break
                time.sleep(1)
                self.driver.find_element_by_class_name("next-next").click()

    def _scrape_page(self, link, amazon_category):
        """Scrape one of the product pages and pull neccessary values."""
        time.sleep(1)
        self.driver.get(link)
        self.driver.execute_script("window.scrollTo(0,1000)")
        WebDriverWait(self.driver, 12).until(
            EC.visibility_of_element_located((By.ID, "product-description"))
        )

        description_element = self.driver.find_element_by_id("product-description")
        title_element = self.driver.find_element_by_class_name("product-title-text")
        quantity_element = self.driver.find_element_by_class_name(
            "product-quantity-tip"
        )
        image_element = self.driver.find_element_by_class_name("magnifier-image")

        category_words = language_utils.get_important_title_words(
            title_element.text, description_element.text
        )
        dimensions = language_utils.get_dimensions(description_element.text)
        weight = language_utils.get_weight(description_element.text)
        quantity = language_utils.get_units_available(quantity_element.text)
        image_url = image_element.get_attribute("src")
        price = self._scrape_price()

        try:
            shipping_price = self._scrape_shipping_price()
            shipping_price_10_units = self._scrape_shipping_price(ten_units=True)
        except KeyboardInterrupt:
            system.exit()
        except Exception as e:
            # TODO: Sometimes boxes will appear asking where to ship from.
            logging.exception(
                f"Exception finding shipping and price and units: {e.__dict__}"
            )
            shipping_price = 0.0
            shipping_price_10_units = 0.0

        if (
            len(self.driver.find_elements(By.CLASS_NAME, "product-quantity-package"))
            > 0
        ):
            packaging_element = self.driver.find_element_by_class_name(
                "product-quantity-package"
            )
            unit_discounts = language_utils.get_unit_discounts(packaging_element.text)
        else:
            unit_discounts = {"discount": 0, "discount_amount": 0}

        # Find or create the category if it doesn't exist
        # then create the item and assign it the category
        category = self.category.find_or_create(
            category_words=category_words, amazon_category=amazon_category
        )

        self.item.find_or_create(
            title=title_element.text,
            category_id=category.id,
            dimensions=dimensions,
            price=price,
            shipping_price=shipping_price,
            shipping_price_10_units=shipping_price_10_units,
            url=self.driver.current_url,
            weight=weight,
            unit_discounts=unit_discounts,
            quantity=quantity,
            amazon_category=amazon_category,
            image_url=image_url,
        )

    def _scrape_price(self):
        """Scrape the price for a particular product."""
        price_element = None
        if len(self.driver.find_elements(By.CLASS_NAME, "product-price-value")) > 0:
            price_element = self.driver.find_element_by_class_name(
                "product-price-value"
            )
        else:
            price_element = self.driver.find_element_by_class_name(
                "uniform-banner-box-discounts"
            )

        price_regex = re.search(".(\d+\.\d+).*", price_element.text, re.IGNORECASE)
        if price_regex:
            return float(price_regex.group(1))
        else:
            return -1

    def _scrape_shipping_price(self, ten_units=False):
        """Check the shipping prices for a particular product/page."""
        if ten_units is True:
            for _x in range(9):
                self.driver.find_element_by_class_name(
                    "next-after"
                ).find_element_by_class_name("next-btn").click()

        shipping_price_element = self.driver.find_element_by_class_name(
            "product-shipping-price"
        )
        if shipping_price_element.text == "Free Shipping":
            return 0.0
        else:
            price_regex = re.search(
                ".(\d+\.\d+).*", shipping_price_element.text, re.IGNORECASE
            )
            if price_regex:
                return float(price_regex.group(1))

    @classmethod
    def run(cls):
        """Public method to instantiate scraping of Aliexpress products."""
        cls()._scrape_pages()
