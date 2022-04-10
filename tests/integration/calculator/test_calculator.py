import sys
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import broker
import calculator
from database.category import Category as CategoryModel
from database.db import Category as CategoryDB
from database.db import Database
from database.db import Item as ItemDB
from database.item import Item as ItemModel


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


def _setup_mock_values(amazon_fee):
    category = CategoryModel().new(
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
        amazon_fee=amazon_fee,
    )

    item = ItemModel().new(
        title="Test",
        price=10,
        url="https://www.aliexpress.com/item/1005003185690192.html",
        image_url="https://ae01.alicdn.com/kf/Ha56356295023483f8e4b3e122602862by/REDRAGON-Fizz-K617-RGB-USB-Mini-Mechanical-Gaming-Keyboard-Red-Switch-61-Keys-Wired-detachable-cable.jpg_Q90.jpg_.webp",
        shipping_price=5,
        shipping_price_10_units=4,
        quantity=100,
        amazon_category="1",
        category_id=category.id,
        dimensions=None,
        weight={"weight": None, "measurement": None},
        amazon_fee=amazon_fee,
    )

    return (item, category)


def _setup_redis_values(key, record):
    """Add the test category record to redis."""
    broker.redis().rpush(key, record.id)


def _setup_test(amazon_fee):
    """Sets up the test. Creating mocks, values, etc."""
    sys.modules["database.db"] = _setup_mock_database_klass()
    _remove_previous_db_records()
    _remove_previous_redis_records()

    item, category = _setup_mock_values(amazon_fee)
    _setup_redis_values("test:queue:category:calculator", category)
    _setup_redis_values("test:queue:item:calculator", item)

    return item, category


@pytest.mark.parametrize("amazon_fee", [(10), (0)])
def test_calculate_items(amazon_fee):
    item, _ = _setup_test(amazon_fee)

    calculator.calculate_items()

    db = Database()
    session = db.get_session()
    updated_item = session.query(ItemDB).get(int(item.id))

    assert updated_item.break_even_sale_price != 0
    assert updated_item.break_even_amazon_sale_price != 0


@pytest.mark.parametrize("amazon_fee", [(10), (0)])
def test_calculate_categories(amazon_fee):
    _, category = _setup_test(amazon_fee)

    calculator.calculate_categories()

    db = Database()
    session = db.get_session()
    updated_category = session.query(CategoryDB).get(int(category.id))

    assert updated_category.average_min_break_even != 0
    assert updated_category.average_min_break_even_amazon != 0
