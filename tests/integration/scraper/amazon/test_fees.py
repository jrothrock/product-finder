import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import broker
import scraper.sites.amazon.fees
from database.category import Category as CategoryModel
from database.db import Category as CategoryDB
from database.db import Database


@patch(
    "database.db.Database._engine_url",
    MagicMock(return_value="sqlite:///database/test.sqlite"),
)
def _setup_mock_database_klass():
    return Database


def _remove_previous_db_records():
    db = Database()
    session = db.get_session()
    session.query(CategoryDB).delete()
    session.close()


def _remove_previous_redis_records():
    redis = broker.redis()
    for key in redis.scan_iter("test:*"):
        redis.delete(key)


def _setup_mock_values():
    return CategoryModel().new(
        category_words=["Espresso", "Machine"],
        amazon_category="1",
        amazon_total_results=2,
        amazon_min_price=15,
        amazon_max_price=25,
        amazon_deviation_price=5,
        amazon_average_price=20,
        amazon_min_rating=4.4,
        amazon_max_rating=5,
        amazon_deviation_rating=0.1,
        amazon_average_rating=4.7,
        amazon_average_length=13,
        amazon_average_width=13,
        amazon_average_height=13,
        amazon_deviation_dimensions=0,
        amazon_average_weight=2,
        amazon_deviation_weight=1,
    )


def _setup_redis_values(category):
    """Add the test category record to redis."""
    broker.redis().rpush("test:queue:category:amazon:fees", category.id)


def _setup_test():
    """Sets up the test. Creating mocks, values, etc."""
    sys.modules["database.db"] = _setup_mock_database_klass()
    _remove_previous_db_records()
    _remove_previous_redis_records()

    new_category = _setup_mock_values()
    _setup_redis_values(new_category)

    return new_category


# This test is being skipped as it has been found challenging to mock selenium requests.
# It uses urllib3 under the hood (which could be mocked), but finding the correct responses,
# say for the firefox downloader, is difficult. It may be possible to create a seperate method
# in the classes and have selenium read from a file in test mode instead of the url,
# but that can be done later. Additionally, redis needs to be mocked.

# However, removing the skip and running testing/Run and Debug in vscode locally is quite useful.
@pytest.mark.skip()
def test_run_category_fees():
    new_category = _setup_test()

    scraper.sites.amazon.fees.scrape_category_fees()

    db = Database()
    session = db.get_session()
    updated_category = session.query(CategoryDB).get(int(new_category.id))

    assert updated_category.amazon_fee != 0
