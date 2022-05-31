"""Module for scraping number of shopify stores for a particular category."""
import logging
import os
import re
import time

from database.db import Category as CategoryDB
from scraper._types import ScraperContext

CATEGORY_SHOPIFY_QUEUE = (
    "test:queue:category:shopify" if os.getenv("TEST_ENV") else "queue:category:shopify"
)


def _get_number_of_sites(number_of_sites_elem_text: str) -> int:
    """Get integer number of stores from text body."""
    if found_results := re.search("About (.+) results", number_of_sites_elem_text):
        return int(found_results.group(1).strip().replace(",", ""))
    else:
        return 0


def _get_shopify(context: ScraperContext, category_id: str) -> None:
    """Pull the shopify store count for a particular category from Google."""
    category = context.pg_session.query(CategoryDB).get(int(category_id))
    key_words = category.title.split("_")
    context.browser.get(
        "https://www.google.com/search?q=site%3Amyshopify.com+" + "+".join(key_words)
    )
    time.sleep(2)
    number_of_sites_elem = context.browser.find_element_by_xpath(
        "//div[contains(@id, 'result-stats')]"
    )
    number_of_shopify_sites = _get_number_of_sites(
        number_of_sites_elem.get_attribute("innerHTML")
    )

    context.pg_session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
        {
            "number_of_shopify_sites": number_of_shopify_sites,
        }
    )
    context.pg_session.commit()


def _process_categories(context: ScraperContext, category_ids: list[str]) -> None:
    """Process the shopify categories."""
    for category_id in category_ids:
        try:
            _get_shopify(context, category_id)
        except Exception as e:
            logging.exception(
                f"Exception scraping number of shopify sites: {e.__dict__}"
            )
            pass


def scrape_categories() -> None:
    """Check the Shopify category queue and process categories."""
    context = ScraperContext.new()
    category_ids = context.redis.lrange(CATEGORY_SHOPIFY_QUEUE, 0, -1)
    context.redis.delete(CATEGORY_SHOPIFY_QUEUE)

    _process_categories(context, category_ids)
