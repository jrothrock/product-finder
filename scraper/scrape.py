from scraper.sites.aliexpress import Aliexpress
from scraper.sites.amazon import AmazonItem, AmazonCategory


def scrape_aliexpress():
    Aliexpress()


def scrape_amazon_fees():
    AmazonItem()


def scrape_amazon_categories():
    AmazonCategory()


def scrape_all():
    scrape_aliexpress()
    scrape_amazon_fees()
    scrape_amazon_categories()

    scrape_amazon_categories()
