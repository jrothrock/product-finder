import dataclasses

import redis
from selenium import webdriver
from sqlalchemy.orm import Session

import broker
import database.db
from database.category import Category as CategoryModel
from database.item import Item as ItemModel
from scraper.core.drivers import Driver


@dataclasses.dataclass(frozen=True)
class ScraperContext:
    """An easy to access class with various library and models instances."""

    redis: redis.client
    pg_session: Session
    browser: webdriver
    category: CategoryModel
    item: ItemModel

    @classmethod
    def new(cls):
        """Will create a new ScraperContext and return it."""
        return cls(
            redis=broker.redis(),
            pg_session=database.db.database_instance.get_session(),
            browser=Driver().get_driver(),
            category=CategoryModel(),
            item=ItemModel(),
        )
