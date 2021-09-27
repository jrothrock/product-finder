from drivers import *
from IPython import embed
from utils.language_utils import LanguageUtils
from utils.database import *
from category import Category as CategoryModel
from item import Item as ItemModel
import re
import time 
class Aliexpress(Driver):
  def __init__(self):
    super().__init__()
    self.category = CategoryModel()
    self.item = ItemModel()
    self.scrape_pages()

  def scrape_pages(self):
    # TODO make the urls and amazon_category more dynamic
    self.driver.get("https://www.aliexpress.com/category/15/home-garden.html?&SortType=create_desc")
    amazon_category = 1
    pages = 0
    while True:
      current_url = self.driver.current_url
      self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
      url_elements = self.driver.find_elements(By.CLASS_NAME, 'awV9E')
      urls = [url_elem.get_attribute("href") for url_elem in url_elements]
      for link in urls:
        self.scrape_page(link, amazon_category)

      self.driver.get(current_url)
      self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight - 1750);')
      pages += 1

      if pages >= 3:
        # embed()
        # Database().session.query(Item, Category).join(Category).first()
        # Database().session.query(Item, Category).join(Category).first().Item.__dict__
        break
      self.driver.find_element_by_class_name('next-next').click()


  def scrape_page(self, link, amazon_category):
    time.sleep(1)
    self.driver.get(link)
    self.driver.execute_script('window.scrollTo(0,1000)')
    WebDriverWait(self.driver, 12).until(EC.visibility_of_element_located((By.ID, "product-description")))

    description_element = self.driver.find_element_by_id('product-description')
    title_element = self.driver.find_element_by_class_name('product-title-text')
    quantity_element = self.driver.find_element_by_class_name('product-quantity-tip')

    category_words = LanguageUtils.get_important_title_words(title_element.text, description_element.text)
    dimensions = LanguageUtils.get_dimensions(description_element.text)
    weight_or_material = LanguageUtils.get_weight_or_material(description_element.text)
    quantity =  LanguageUtils.get_units_available(quantity_element.text)
    price = self.scrape_price()
  
    try:
      shipping_price = self.scrape_shipping_price()
      shipping_price_10_units = self.scrape_shipping_price(ten_units=True)
    except:
      # investigate more later. Sometimes boxes will appear asking where to ship from.
      shipping_price = 0.0
      shipping_price_10_units = 0.0

    if len(self.driver.find_elements(By.CLASS_NAME, 'product-quantity-package')) > 0:
      packaging_element = self.driver.find_element_by_class_name('product-quantity-package')
      unit_discounts = LanguageUtils.get_unit_discounts(packaging_element.text)
    else:
      unit_discounts = {"discount": 0, "discount_amount": 0}

    # Find or create the category if it doesn't exist
    # then create the item and assign it the category
    category = self.category.find_or_create(
      category_words=category_words
    )

    self.item.find_or_create(
      title=title_element.text,
      category_id=category.id, 
      dimensions=dimensions, 
      price=price, 
      shipping_price=shipping_price, 
      shipping_price_10_units=shipping_price_10_units,
      url=self.driver.current_url,
      weight_or_material=weight_or_material,
      unit_discounts=unit_discounts,
      quantity=quantity,
      amazon_category=amazon_category
    )

  def scrape_price(self):
    price_element = None
    if len(self.driver.find_elements(By.CLASS_NAME, 'product-price-value')) > 0:
      price_element = self.driver.find_element_by_class_name('product-price-value')
    else: 
      price_element = self.driver.find_element_by_class_name('uniform-banner-box-discounts')
    
    price_regex = re.search('.(\d+\.\d+).*', price_element.text, re.IGNORECASE)
    if price_regex:
      return float(price_regex.group(1))
    else:
      return -1

    
  def scrape_shipping_price(self, ten_units=False):
    if ten_units == True:
      for _x in range(9):
        self.driver.find_element_by_class_name('next-after').find_element_by_class_name('next-btn').click()
    
    shipping_price_element = self.driver.find_element_by_class_name('product-shipping-price')
    if shipping_price_element.text == "Free Shipping":
      return 0.0
    else:
      price_regex = re.search('.(\d+\.\d+).*', shipping_price_element.text, re.IGNORECASE)
      if price_regex:
        return float(price_regex.group(1))

if __name__ == "__main__":
  Aliexpress()