from scraper.sites.aliexpress import Aliexpress
from scraper.sites.amazon import AmazonItem, AmazonCategory


def scrape_aliexpress():
    Aliexpress.run()


def scrape_amazon_fees():
    AmazonItem.run()


def scrape_amazon_categories():
    AmazonCategory.run()


def scrape_all():
    scrape_aliexpress()
    scrape_amazon_fees()
    scrape_amazon_categories()
