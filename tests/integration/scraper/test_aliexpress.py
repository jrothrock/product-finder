import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import broker
import scraper.sites.aliexpress
from database.db import Category as CategoryDB
from database.db import Database
from database.db import Item as ItemDB
from database.db import func


@patch(
    "database.db.Database._engine_url",
    MagicMock(return_value="sqlite:///database/test.sqlite"),
)
def _setup_mock_database_klass():
    return Database


def _remove_previous_db_records():
    db = Database()
    session = db.get_session()
    session.query(ItemDB).delete()
    session.query(CategoryDB).delete()
    session.close()


def _remove_previous_redis_records():
    redis = broker.redis()
    for key in redis.scan_iter("test:*"):
        redis.delete(key)


def _setup_test():
    """Sets up the test. Creating mocks, values, etc."""
    sys.modules["database.db"] = _setup_mock_database_klass()
    _remove_previous_db_records()
    _remove_previous_redis_records()


# This test is being skipped as it has been found challenging to mock selenium requests.
# It uses urllib3 under the hood (which could be mocked), but finding the correct responses,
# say for the firefox downloader, is difficult. It may be possible to create a seperate method
# in the classes and have selenium read from a file in test mode instead of the url,
# but that can be done later. Additionally, redis needs to be mocked.

# However, removing the skip and running testing/Run and Debug in vscode locally is quite useful.
@pytest.mark.skip()
def test_run():
    _setup_test()
    assert len(broker.redis().lrange("test:queue:item:amazon:fees", 0, -1)) == 0

    scraper.sites.aliexpress.scrape_pages()

    db = Database()
    session = db.get_session()
    category_count = session.query(func.count(CategoryDB.id)).scalar()
    item_count = item_count = session.query(func.count(ItemDB.id)).scalar()

    assert category_count != 0
    assert item_count != 0
