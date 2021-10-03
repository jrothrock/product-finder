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
    try:
      # May run into race conditions, may need a transaction later
      item_ids = self.redis.lrange("queue:item", 0, -1)
      self.redis.delete("queue:item")
      self.process_items(item_ids)
    except:
      pass

  def process_items(self, item_ids):
    for item_id in item_ids:
      self.get_amazon(item_id)

  def get_amazon(self, item_id):
    time.sleep(1)
    item = Database().session.query(ItemDB).get(int(item_id))
    self.driver.get("https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index?lang=en_US")
    time.sleep(1)
    self.driver.find_element_by_xpath("//input[contains(@aria-labelledby, 'link_continue-announce')]").click()
    self.driver.find_element_by_id("product-length").send_keys(str(round(item.length, 2)))
    self.driver.find_element_by_id("product-width").send_keys(str(round(item.width, 2)))
    self.driver.find_element_by_id("product-height").send_keys(str(round(item.height, 2)))
    self.driver.find_element_by_id("product-weight").send_keys(str(round(item.weight, 2)))
    self.driver.find_element_by_xpath("//span[contains(text(), 'Select category')]").click()
    self.driver.find_element_by_xpath("//a[contains(text(), '"+item.amazon_category+"')]").click()
    self.driver.find_element_by_id("estimate-new-announce").click()
    self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight - 250);')
    time.sleep(1)
    amazon_fees = self.driver.find_element_by_id("afn-seller-proceeds").get_attribute("value")
    session = Database().session
    session.query(ItemDB).filter(ItemDB.id == item.id).update({"amazon_fee": float(amazon_fees[1:])})
    session.commit()
    session.close()
    self.driver.manage().delete_all_cookies()

  def __del__ (self, *exc):
    if self.driver:
      self.driver.quit()
    
  
class AmazonCategory(Driver):
  def __init__(self):
    super().__init__()
    self.check_categories()

  def check_categories(self):
    try:
      # May run into race conditions, may need a transaction later
      category_ids = self.redis.lrange("queue:category", 0, -1)
      self.redis.delete("queue:category")
      self.process_categories(category_ids)
    except:
      pass

  def process_categories(self, category_ids):
    for category_id in category_ids:
      self.get_amazon(category_id)

  def get_amazon(self, category_id):
    category = Database().session.query(CategoryDB).get(int(category_id))
    kew_words = category.title.split("_")

  def __del__ (self, *exc):
    if self.driver:
      self.driver.quit()
