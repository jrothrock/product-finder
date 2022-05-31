"""Module which scrapes the Amazon category."""
import logging
import os
import re
import statistics
import time

import utils.language_utils as language_utils
import utils.unit_conversions as unit_conversions
from database.db import Category as CategoryDB
from scraper._types import ScraperContext

CATEGORY_SHOPIFY_QUEUE = (
    "test:queue:category:shopify" if os.getenv("TEST_ENV") else "queue:category:shopify"
)

CATEGORY_AMAZON_FEES_QUEUE = (
    "test:queue:category:amazon:fees"
    if os.getenv("TEST_ENV")
    else "queue:category:amazon:fees"
)

CATEGORY_CALCULATOR_QUEUE = (
    "test:queue:category:calculator"
    if os.getenv("TEST_ENV")
    else "queue:category:calculator"
)

CATEGORY_AMAZON_LISTINGS_QUEUE = (
    "test:queue:category:amazon:listings"
    if os.getenv("TEST_ENV")
    else "queue:category:amazon:listings"
)


def _get_price_from_text(price_text: str) -> float:
    """Pull the numeric price from a text string."""
    return float(price_text[1:-1].strip().replace(",", ""))


def _get_number_of_products(number_of_products_text: str) -> float:
    """Pull the number of products for that category."""
    if found_number_of_products := re.search(
        "of (over)?(.+) results", number_of_products_text
    ):
        return int(found_number_of_products.group(2).strip().replace(",", ""))
    else:
        return 0


def _get_review_from_text(review_text: str) -> float:
    """Pull the average review for a specific product."""
    if found_stars := re.search("(.+) (out|Stars)", review_text):
        return float(found_stars.group(1))
    else:
        return 0.0


def _get_number_of_ratings_from_text(num_ratings_text: str) -> float:
    """Get the total number of ratings for a specific product."""
    return int(num_ratings_text.strip().replace(",", ""))


def _calculate_dimensions_and_weight(
    context: ScraperContext, product_links: list[str]
) -> dict[str, float]:
    """Perform calculations of dimensions and weight for an Amazon category."""
    category_lengths: list[float] = []
    category_widths: list[float] = []
    category_heights: list[float] = []
    category_weights: list[float] = []

    # uses higher than 3 to eliminate sponsored products
    for product_link in product_links[4:8]:
        try:
            product_dimensions_and_weight = _get_amazon_product_dimensions_and_weight(
                context, product_link
            )
            category_lengths.append(product_dimensions_and_weight.get("length", 0.0))
            category_widths.append(product_dimensions_and_weight.get("width", 0.0))
            category_heights.append(product_dimensions_and_weight.get("height", 0.0))
            category_weights.append(product_dimensions_and_weight.get("weight", 0.0))
        except Exception as e:
            logging.exception(
                f"Exception getting amazon product dimensions and weight: {e.__dict__}"
            )

    category_dimensions = [
        length * width * height
        for length, width, height in zip(
            category_lengths, category_widths, category_heights
        )
    ]

    amazon_average_length = (
        (sum(category_lengths) / len(category_lengths))
        if len(category_lengths)
        else 0.0
    )
    amazon_average_width = (
        (sum(category_widths) / len(category_widths)) if len(category_widths) else 0.0
    )
    amazon_average_height = (
        (sum(category_heights) / len(category_heights))
        if len(category_heights)
        else 0.0
    )
    amazon_deviation_dimensions = (
        statistics.pstdev(category_dimensions) if len(category_dimensions) else 0.0
    )
    amazon_average_weight = (
        (sum(category_weights) / len(category_weights))
        if len(category_weights)
        else 0.0
    )
    amazon_deviation_weight = (
        statistics.pstdev(category_weights) if len(category_dimensions) else 0.0
    )

    return {
        "amazon_average_length": amazon_average_length,
        "amazon_average_width": amazon_average_width,
        "amazon_average_height": amazon_average_height,
        "amazon_deviation_dimensions": amazon_deviation_dimensions,
        "amazon_average_weight": amazon_average_weight,
        "amazon_deviation_weight": amazon_deviation_weight,
    }


def _get_category_dimensions_and_weight(context: ScraperContext):
    """Get the dimensions and weights for a category by averaging a few of the category's products."""
    product_link_elems = context.browser.find_elements_by_xpath(
        "//div[contains(@class, 's-result-list')]//div[contains(@class, 'a-section')]//h2/a[contains(@class, 'a-link-normal')]"
    )
    product_links = [
        product_link_elem.get_attribute("href")
        for product_link_elem in product_link_elems
    ]

    return _calculate_dimensions_and_weight(context, product_links)


def _get_amazon_product_dimensions_and_weight(
    context: ScraperContext, url: str
) -> dict[str, float]:
    """Calculate dimensions and weight for Amazon product."""
    context.browser.get(url)

    product_details_elem = context.browser.find_element_by_xpath(
        "//table[contains(@id, 'productDetails_detailBullets_sections1')]"
    )
    dimensions = language_utils.get_dimensions(
        product_details_elem.get_attribute("innerHTML")
    )
    weights = language_utils.get_weight(product_details_elem.get_attribute("innerHTML"))

    length: float = float(dimensions["length"])
    width: float = float(dimensions["width"])
    height: float = float(dimensions["height"])
    dimension_measurement: str = str(dimensions["measurement"])

    length_in_inches = unit_conversions.convert_to_inches(length, dimension_measurement)
    width_in_inches = unit_conversions.convert_to_inches(width, dimension_measurement)
    height_in_inches = unit_conversions.convert_to_inches(height, dimension_measurement)

    weight: float = float(weights["weight"])
    weight_measurement: str = str(weights["measurement"])

    weight_in_pounds = unit_conversions.convert_to_pounds(weight, weight_measurement)

    return {
        "length": length_in_inches,
        "width": width_in_inches,
        "height": height_in_inches,
        "weight": weight_in_pounds,
    }


def _get_amazon_category(context: ScraperContext, category_id: str) -> None:
    """Scrape the amazon category and calculate needed values, then update record in database."""
    category = context.pg_session.query(CategoryDB).get(int(category_id))
    key_words = category.title.split("_")
    context.browser.get(
        "https://www.amazon.com/s?k=" + "+".join(key_words) + "&ref=nb_sb_noss"
    )

    time.sleep(2)

    number_of_products_elem = context.browser.find_element_by_xpath(
        "//div[contains(@class, 's-breadcrumb')]//div[contains(@class, 'a-spacing-top-small')]/*[1]"
    ).text
    amazon_total_results = _get_number_of_products(number_of_products_elem)

    prices = [
        _get_price_from_text(price_elem.get_attribute("innerHTML"))
        for price_elem in context.browser.find_elements_by_xpath(
            "//span[contains(@class, 'a-price')]//span[contains(@class, 'a-offscreen')]"
        )
    ]

    ratings = [
        _get_review_from_text(rating_elem.get_attribute("innerHTML"))
        for rating_elem in context.browser.find_elements_by_xpath(
            "//div[contains(@class, 's-result-item')]//span[contains(@class, 'a-icon-alt')]"
        )
    ]

    number_of_ratings = [
        _get_number_of_ratings_from_text(num_rating_elem.get_attribute("innerHTML"))
        for num_rating_elem in context.browser.find_elements_by_xpath(
            "//div[contains(@class, 's-result-list')]//div[contains(@class, 'a-section')]//div[contains(@class, 'a-row')]//span/a[contains(@class, 'a-link-normal')]//span[contains(@class, 'a-size-base')]"
        )
    ]

    prices = list(filter(lambda x: x is not None, prices))
    ratings = list(filter(lambda x: x is not None, ratings))
    number_of_ratings = list(filter(lambda x: x is not None, number_of_ratings))

    amazon_min_price = min(prices) if len(prices) else None
    amazon_max_price = max(prices) if len(prices) else None
    amazon_deviation_price = statistics.pstdev(prices) if len(prices) else None
    amazon_average_price = (sum(prices) / len(prices)) if len(prices) else None
    amazon_min_rating = min(ratings) if len(ratings) else None
    amazon_max_rating = max(ratings) if len(ratings) else None
    amazon_deviation_rating = statistics.pstdev(ratings) if len(ratings) else None
    amazon_average_rating = (sum(ratings) / len(ratings)) if len(ratings) else None
    amazon_average_number_of_ratings = (
        (sum(number_of_ratings) / len(number_of_ratings))
        if len(number_of_ratings)
        else None
    )

    try:
        category_dimensions_and_weight_dict = _get_category_dimensions_and_weight(
            context
        )
    except Exception as e:
        logging.exception(
            f"Exception getting category dimensions and weight: {e.__dict__}"
        )
        category_dimensions_and_weight_dict = {}

    context.pg_session.query(CategoryDB).filter(CategoryDB.id == category.id).update(
        {
            "amazon_total_results": int(amazon_total_results),
            "amazon_min_price": amazon_min_price,
            "amazon_max_price": amazon_max_price,
            "amazon_deviation_price": amazon_deviation_price,
            "amazon_average_price": amazon_average_price,
            "amazon_min_rating": amazon_min_rating,
            "amazon_max_rating": amazon_max_rating,
            "amazon_deviation_rating": amazon_deviation_rating,
            "amazon_average_rating": amazon_average_rating,
            "amazon_average_number_of_ratings": amazon_average_number_of_ratings,
            "amazon_average_length": category_dimensions_and_weight_dict.get(
                "amazon_average_length", None
            ),
            "amazon_average_width": category_dimensions_and_weight_dict.get(
                "amazon_average_width", None
            ),
            "amazon_average_height": category_dimensions_and_weight_dict.get(
                "amazon_average_height", None
            ),
            "amazon_deviation_dimensions": category_dimensions_and_weight_dict.get(
                "amazon_deviation_dimensions", None
            ),
            "amazon_average_weight": category_dimensions_and_weight_dict.get(
                "amazon_average_weight", None
            ),
            "amazon_deviation_weight": category_dimensions_and_weight_dict.get(
                "amazon_deviation_weight", None
            ),
        }
    )
    context.pg_session.commit()
    context.redis.rpush(CATEGORY_SHOPIFY_QUEUE, category.id)

    category_dimensions_and_weight_dict_values = (
        category_dimensions_and_weight_dict.values()
    )
    if None not in category_dimensions_and_weight_dict_values:
        context.redis.rpush(CATEGORY_AMAZON_FEES_QUEUE, category.id)
    else:
        context.redis.rpush(CATEGORY_CALCULATOR_QUEUE, category.id)


def _process_categories(context: ScraperContext, category_ids: list[str]) -> None:
    """Check the Amazon category for the Amazon queue."""
    for category_id in category_ids:
        try:
            _get_amazon_category(context, category_id)
        except Exception as e:
            logging.exception(f"Exception scraping amazon categories: {e.__dict__}")
            pass


def scrape_amazon_categories() -> None:
    """Check the Amazon queue and process the categories."""
    context = ScraperContext.new()
    category_ids = context.redis.lrange(CATEGORY_AMAZON_LISTINGS_QUEUE, 0, -1)
    context.redis.delete(CATEGORY_AMAZON_LISTINGS_QUEUE)

    _process_categories(context, category_ids)
