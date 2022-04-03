import os
import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from database.category import Category as CategoryModel
from database.db import Category as CategoryDB
from database.db import Database
from scraper.sites.amazon import category
import broker


@patch(
    "database.db.Database._engine",
    MagicMock(return_value="sqlite:///database/test.sqlite"),
)
def _setup_mock_database_klass():
    return Database

def _remove_previous_db_records():
  session = Database().session
  session.query(CategoryDB).delete()
  session.close()

def _remove_previous_redis_records():
  redis = broker.redis()
  for key in redis.scan_iter("test:*"):
    redis.delete(key)

def _setup_mock_values():
    return CategoryModel().new(
        category_words=["Espresso", "Machine"], amazon_category="1"
    )


def _setup_test():
  """Sets up the test. Creating mocks, values, etc."""
  sys.modules["database.db"] = _setup_mock_database_klass()
  _remove_previous_db_records()
  _remove_previous_redis_records()

  new_category = _setup_mock_values()

  return new_category


# This test is being skipped as it has been found challenging to mock selenium requests.
# It uses urllib3 under the hood (which could be mocked), but finding the correct responses,
# say for the firefox downloader, is difficult. It may be possible to create a seperate method
# in the classes and have selenium read from a file in test mode instead of the url,
# but that can be done later. Additionally, redis needs to be mocked.

# However, removing the skip and running testing/Run and Debug in vscode locally is quite useful.
@pytest.mark.skip()
def test_run():
    new_category = _setup_test()
    assert len(broker.redis().lrange("test:queue:category:amazon:listings", 0, -1)) == 1

    category.AmazonCategory.run()

    updated_category = Database().session.query(CategoryDB).get(int(new_category.id))

    assert len(broker.redis().lrange("test:queue:category:amazon:listings", 0, -1)) == 0
    assert len(broker.redis().lrange("test:queue:category:amazon:fees", 0, -1)) == 1
    assert updated_category.amazon_total_results != 0
    assert updated_category.amazon_min_price != 0
    assert updated_category.amazon_max_price != 0
    assert updated_category.amazon_deviation_price != 0
    assert updated_category.amazon_average_price != 0
    assert updated_category.amazon_min_rating != 0
    assert updated_category.amazon_max_rating != 0
    assert updated_category.amazon_deviation_rating != 0
    assert updated_category.amazon_average_rating != 0
    assert updated_category.amazon_average_number_of_ratings != 0
    assert updated_category.amazon_average_length != 0
    assert updated_category.amazon_average_width != 0
    assert updated_category.amazon_average_height != 0
    assert updated_category.amazon_deviation_dimensions != 0
    assert updated_category.amazon_average_weight != 0
    assert updated_category.amazon_deviation_weight != 0
