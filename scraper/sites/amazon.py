import redis
import time

from scraper.core.drivers import Driver, WebDriverWait, EC, By
from scraper.core.category import Category as CategoryModel
from scraper.core.item import Item as ItemModel
from scraper.core.utils.language_utils import LanguageUtils

from database.db import Database, Item as ItemDB, Category as CategoryDB

from IPython import embed


class AmazonItem(Driver):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()
        self.check_items()

    def check_items(self):
        item_ids = self.redis.lrange("queue:item", 0, -1)
        self.redis.delete("queue:item")
        self.process_items(item_ids)

    def process_items(self, item_ids):
        for item_id in item_ids:
            try:
                self.get_amazon(item_id)
            except:
                pass

    def get_amazon(self, item_id):
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


class AmazonCategory(Driver):
    def __init__(self):
        super().__init__()
        self.redis = redis.Redis()
        self.check_categories()

    def check_categories(self):
        category_ids = self.redis.lrange("queue:category", 0, -1)
        self.redis.delete("queue:category")
        self.process_categories(category_ids)

    def process_categories(self, category_ids):
        for category_id in category_ids:
            try:
                self.get_amazon(category_id)
            except:
                pass

    def get_amazon(self, category_id):
        time.sleep(1)
        category = Database().session.query(CategoryDB).get(int(category_id))
        key_words = category.title.split("_")
        self.driver.get(
            "https://www.amazon.com/s?k=" + "+".join(key_words) + "&ref=nb_sb_noss"
        )
        time.sleep(1)
        number_of_products_elem = self.driver.find_element_by_xpath(
            "//div[contains(@class, 's-breadcrumb']//div[contains(@class, 'a-spacing-top-small')]/*[1]"
        ).text
        amazon_total_results = self.get_number_of_products(number_of_products_elem.text)
        prices = map(
            lambda price_elem: float(price_elem.text),
            self.driver.find_elements_by_class_name("a-offscreen"),
        )
        ratings = map(
            lambda rating_elem: self.get_review_from_text(rating_elem.text),
            self.driver.find_elements_by_class_name("a-icon-alt"),
        )
        amazon_min_price = prices.min
        amazon_max_price = prices.max
        amazon_min_rating = ratings.min
        amazon_max_rating = ratings.max
        session = Database().session
        session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
            {
                "amazon_total_results": int(amazon_total_results),
                "amazon_min_price": amazon_min_price,
                "amazon_max_price": amazon_max_price,
                "amazon_min_rating": amazon_min_rating,
                "amazon_max_rating": amazon_max_rating,
            }
        )
        self.redis.lpush("queue:item_calculator", category.id)

    def get_number_of_products(self, number_of_products_text):
        pass

    def get_review_from_text(self, review_text):
        pass
