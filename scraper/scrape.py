from scraper.sites.aliexpress import Aliexpress
from scraper.sites.amazon.fees import AmazonFee
from scraper.sites.amazon.category import AmazonCategory
from scraper.sites.shopify import ShopifyCategory


def scrape_aliexpress():
    Aliexpress.run()


def scrape_amazon_fees():
    AmazonFee.run_category_fees()
    AmazonFee.run_item_fees()


def scrape_amazon_categories():
    AmazonCategory.run()


def scrape_shopify_categories():
    ShopifyCategory.run()


def scrape_all():
    scrape_aliexpress()
    scrape_amazon_categories()
    scrape_amazon_fees()
    scrape_shopify_categories()
