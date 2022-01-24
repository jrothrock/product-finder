"""Subpack that holds all of the modules used for scraping various sites."""
from scraper.sites.aliexpress import Aliexpress
from scraper.sites.amazon.fees import AmazonFee
from scraper.sites.amazon.category import AmazonCategory
from scraper.sites.shopify import ShopifyCategory


def scrape_aliexpress():
    """Easy to use interface to run Aliexpress scraper."""
    Aliexpress.run()


def scrape_amazon_fees():
    """Easy to use interface to run Amazon fees scraper."""
    AmazonFee.run_category_fees()
    AmazonFee.run_item_fees()


def scrape_amazon_categories():
    """Easy to use interface to run Amazon categories scraper."""
    AmazonCategory.run()


def scrape_shopify_categories():
    """Easy to use interface to run Shopify sites count scraper."""
    ShopifyCategory.run()


def scrape_all():
    """Easy to use interface to run all scrapers."""
    scrape_aliexpress()
    scrape_amazon_categories()
    scrape_amazon_fees()
    scrape_shopify_categories()
