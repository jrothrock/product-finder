"""Category module which holds procedures commonly used when creating category records."""
import redis
from sqlalchemy.orm.exc import NoResultFound

from database.db import Category as CategoryDB
from database.db import Database as db


class Category(db):
    """Class which holds procedures commonly used when creating category records."""

    def __init__(self):
        """Instantiate database communication and Redis."""
        super().__init__()
        self.redis = redis.Redis()

    def find_or_create(self, **kwargs):
        """Find or creates a category record based on the title."""
        title = self._create_title(kwargs["category_words"])
        try:
            category = (
                self.session.query(CategoryDB).filter_by(title=title).one()
            )  # filter on name
        except NoResultFound:
            category = self.new(**kwargs)

        return category

    def new(self, **kwargs):
        """Create a category recored."""
        title = self._create_title(kwargs.get("category_words"))
        title_version = self._title_cohort()
        new_category = CategoryDB(
            title=title,
            amazon_category=kwargs.get("amazon_category"),
            title_version=title_version,
        )
        self.session.add(new_category)
        self.session.commit()
        self.session.refresh(new_category)
        self._add_to_redis_queue(new_category)
        return new_category

    def _title_cohort(self):
        """Return the title cohort version."""
        return 1

    def _create_title(self, values):
        """Create the title for the record."""
        # TODO need to investigate why values is type None
        if values is None or len(values) == 0:
            return ""
        else:
            values.sort()
            return "_".join(values)

    def _add_to_redis_queue(self, new_category):
        """Add category id to the Amazon category queue."""
        self.redis.rpush("queue:category:amazon:listings", new_category.id)
