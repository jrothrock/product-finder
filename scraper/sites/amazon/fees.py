"""Module for scraping AmazonFees -- Category and Item."""
import logging
import os
import time
import typing

import utils.mappings as mappings
from database.db import Category as CategoryDB
from database.db import Item as ItemDB
from scraper._types import ScraperContext

ITEM_AMAZON_FEES_QUEUE = (
    "test:queue:item:amazon:fees" if os.getenv("TEST_ENV") else "queue:item:amazon:fees"
)

ITEM_CALCULATOR_QUEUE = (
    "test:queue:item:calculator" if os.getenv("TEST_ENV") else "queue:item:calculator"
)

CATEGORY_CALCULATOR_QUEUE = (
    "test:queue:category:calculator"
    if os.getenv("TEST_ENV")
    else "queue:category:calculator"
)

CATEGORY_AMAZON_FEES_QUEUE = (
    "test:queue:category:amazon:fees"
    if os.getenv("TEST_ENV")
    else "queue:category:amazon:fees"
)


def _add_to_redis_queue(
    context: ScraperContext,
    record_id: str,
    db_klass: typing.Type[ItemDB] | typing.Type[CategoryDB],
) -> None:
    """Add the record id to correct queue to have calculations (re)run on the record later."""
    if db_klass == ItemDB:
        ScraperContext.redis.rpush(ITEM_CALCULATOR_QUEUE, record_id)
    else:
        ScraperContext.redis.rpush(CATEGORY_CALCULATOR_QUEUE, record_id)


def _get_amazon(
    context: ScraperContext,
    record_id: str,
    db_klass: typing.Type[ItemDB] | typing.Type[CategoryDB],
) -> None:
    """
    Scrape the amazon page for a particular category or item.

    Will also update the record with the calculated amazon fee -- can be either a
    item or category record.
    """
    time.sleep(1)
    record = context.pg_session.query(db_klass).get(int(record_id))
    context.browser.get(
        "https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index?lang=en_US"
    )
    time.sleep(1)

    context.browser.find_element_by_xpath(
        "//input[contains(@aria-labelledby, 'link_continue-announce')]"
    ).click()

    record_length = (
        record.length if isinstance(record, ItemDB) else record.amazon_average_length
    )

    context.browser.find_element_by_id("product-length").send_keys(
        str(round(record_length, 2))
    )

    record_width = (
        record.width if isinstance(record, ItemDB) else record.amazon_average_width
    )
    context.browser.find_element_by_id("product-width").send_keys(
        str(round(record_width, 2))
    )

    record_height = (
        record.height if isinstance(record, ItemDB) else record.amazon_average_height
    )
    context.browser.find_element_by_id("product-height").send_keys(
        str(round(record_height, 2))
    )

    record_weight = (
        record.weight if isinstance(record, ItemDB) else record.amazon_average_weight
    )
    context.browser.find_element_by_id("product-weight").send_keys(
        str(round(record_weight, 2))
    )

    context.browser.find_element_by_xpath(
        "//span[contains(text(), 'Select category')]"
    ).click()

    mapped_amazon_category = mappings.map_amazon_category(record.amazon_category)

    context.browser.find_element_by_xpath(
        "//a[contains(text(), '" + mapped_amazon_category + "')]"
    ).click()

    context.browser.find_element_by_id("estimate-new-announce").click()

    context.browser.execute_script(
        "window.scrollTo(0,document.body.scrollHeight - 250);"
    )

    time.sleep(1)

    amazon_fees = context.browser.find_element_by_id(
        "afn-seller-proceeds"
    ).get_attribute("value")
    context.pg_session.query(db_klass).filter(db_klass.id == record.id).update(
        {"amazon_fee": float(amazon_fees[1:])}
    )
    context.pg_session.commit()

    _add_to_redis_queue(context, record_id, db_klass)

    context.browser.delete_all_cookies()


def _process_records(
    context: ScraperContext,
    record_ids: list[str],
    db_klass: typing.Type[ItemDB] | typing.Type[CategoryDB],
):
    """
    Process the records and try and calculate the amazon fees for the record.

    If the fee can't be calculated, add it to calculation queue anyways, the
    calculation task can handle the null values -- though ideally the record would
    have them.
    """
    for record_id in record_ids:
        try:
            _get_amazon(context, record_id, db_klass)
        except Exception as e:
            _add_to_redis_queue(context, record_id, db_klass)
            logging.exception(f"Exception scraping amazon category fees: {e.__dict__}")
            pass


def scrape_category_fees() -> None:
    """Check the Amazon category fees queue and process the categories."""
    context = ScraperContext.new()

    category_ids = context.redis.lrange(CATEGORY_AMAZON_FEES_QUEUE, 0, -1)
    context.redis.delete(CATEGORY_AMAZON_FEES_QUEUE)

    _process_records(context, category_ids, CategoryDB)


def scrape_item_fees() -> None:
    """Check the Amazon item fees queue and process the items."""
    context = ScraperContext.new()

    item_ids = context.redis.lrange(ITEM_AMAZON_FEES_QUEUE, 0, -1)
    context.redis.delete(ITEM_AMAZON_FEES_QUEUE)

    _process_records(context, item_ids, ItemDB)
