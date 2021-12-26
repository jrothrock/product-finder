from scraper.sites.aliexpress import Aliexpress
from scraper.sites.amazon.item import AmazonItem
from scraper.sites.amazon.category import AmazonCategory
from scraper.sites.shopify import ShopifyCategory


def scrape_aliexpress():
    Aliexpress.run()


def scrape_amazon_fees():
    AmazonItem.run()


def scrape_amazon_categories():
    AmazonCategory.run()


def scrape_shopify_categories():
    ShopifyCategory.run()


def scrape_all():
    scrape_aliexpress()
    scrape_amazon_fees()
    scrape_amazon_categories()
    scrape_shopify_categories()
