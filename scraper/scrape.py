from scraper.sites.aliexpress import Aliexpress
from scraper.sites.amazon import AmazonItem, AmazonCategory

def scrape_items():
  Aliexpress()

def scrape_amazon_fees():
  AmazonItem()

def run():
  scrape_items()
  scrape_amazon_fees()
  