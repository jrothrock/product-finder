from drivers import *
from IPython import embed
from utils.language_utils import LanguageUtils
from item import Item
from category import Category
from utils.database import *
import redis
import time 

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
    item = Database().session.query(Item).get(int(item_id))
    self.driver.get("https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index?lang=en_US")
    self.driver.find_element_by_xpath("//input[contains(@aria-labelledby, 'link_continue-announce')]").click()
    self.driver.find_element_by_id("product-length").send_keys(str(item.length))
    self.driver.find_element_by_id("product-width").send_keys(str(item.width))
    self.driver.find_element_by_id("product-height").send_keys(str(item.height))
    self.driver.find_element_by_id("product-weight").send_keys(str(item.weight))
    self.driver.find_element_by_xpath("//span[contains(text(), 'Select category')]").click()
    self.driver.find_element_by_xpath("//a[contains(text(), '"+item.amazon_category+"')]").click()
    self.driver.find_element_by_id("estimate-new-announce").click()
    amazon_fees = self.driver.find_element_by_id("afn-seller-proceeds").get_attribute("value")
    session = Database().session
    session.query(Item).filter(Item.id == item.id).update({"amazon_fee": float(amazon_fees[1:])})
    session.commit()
    self.driver.manage().delete_all_cookies()
    
  
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
    category = Database().session.query(Category).get(int(category_id))
    kew_words = category.title.split("_")

if __name__ == "__main__":
  AmazonItem()