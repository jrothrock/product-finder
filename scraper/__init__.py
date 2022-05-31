"""Subpackage that holds all of the modules used for scraping various sites."""
import scraper.sites.aliexpress
import scraper.sites.amazon.category
import scraper.sites.amazon.fees
import scraper.sites.shopify


def scrape_aliexpress():
    """Easy to use interface to run Aliexpress scraper."""
    scraper.sites.aliexpress.scrape_pages()


def scrape_amazon_fees():
    """Easy to use interface to run Amazon fees scraper."""
    scraper.sites.amazon.fees.scrape_category_fees()
    scraper.sites.amazon.fees.scrape_item_fees()


def scrape_amazon_categories():
    """Easy to use interface to run Amazon categories scraper."""
    scraper.sites.amazon.category.scrape_amazon_categories()


def scrape_shopify_categories():
    """Easy to use interface to run Shopify sites count scraper."""
    scraper.sites.shopify.scrape_categories()


def scrape_all():
    """Easy to use interface to run all scrapers."""
    scrape_aliexpress()
    scrape_amazon_categories()
    scrape_amazon_fees()
    scrape_shopify_categories()
