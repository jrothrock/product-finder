"""Category module which holds procedures commonly used when creating category records."""
import os

from sqlalchemy.orm.exc import NoResultFound

import broker
import database.db
from database.db import Category as CategoryDB

CATEGORY_AMAZON_LISTINGS_QUEUE = (
    "test:queue:category:amazon:listings"
    if os.getenv("TEST_ENV")
    else "queue:category:amazon:listings"
)


class Category:
    """Class which holds procedures commonly used when creating category records."""

    def __init__(self):
        """Instantiate database communication and Redis."""
        self.redis = broker.redis()
        self.session = database.db.database_instance.get_session()

    def _title_cohort(self) -> int:
        """Return the title cohort version."""
        return 1

    def _create_title(self, values: list[str]) -> str:
        """Create the title for the record."""
        # TODO need to investigate why values is type None
        if values is None or len(values) == 0:
            return ""
        else:
            values.sort()
            return "_".join(values)

    def _add_to_redis_queue(self, new_category: CategoryDB) -> None:
        """Add category id to the Amazon category queue."""
        self.redis.rpush(CATEGORY_AMAZON_LISTINGS_QUEUE, new_category.id)

    def find_or_create(self, **kwargs) -> CategoryDB:
        """Find or creates a category record based on the title."""
        title = self._create_title(kwargs["category_words"])
        try:
            category = (
                self.session.query(CategoryDB).filter_by(title=title).one()
            )  # filter on name
        except NoResultFound:
            category = self.new(**kwargs)

        self.session.close()
        return category

    def new(self, **kwargs) -> CategoryDB:
        """Create a category recored."""
        title = self._create_title(kwargs.pop("category_words"))
        title_version = self._title_cohort()

        updated_arguments = {"title": title, "title_version": title_version, **kwargs}
        new_category = CategoryDB(**updated_arguments)
        self.session.add(new_category)
        self.session.commit()
        self.session.refresh(new_category)

        self._add_to_redis_queue(new_category)
        self.session.close()

        return new_category
