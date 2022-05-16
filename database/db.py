"""Module that houses procedures and schemas for the database."""
# Honestly, I should have gone with a non relational database.
import os

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import func  # noqa: F401
from sqlalchemy.orm import registry
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists

mapper_registry = registry()


@mapper_registry.mapped
class Item:
    """Schema for Item records."""

    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    category_id = Column(ForeignKey("category.id"))
    title = Column(String)
    price = Column(Float, default=0.0)
    shipping_price = Column(Float, default=0.0)
    shipping_price_10_units = Column(Float, default=0.0)
    amazon_category = Column(String)
    amazon_fee = Column(Float, default=0.0)
    single_break_even_price = Column(Float, default=0.0)
    multi_break_even_price = Column(Float, default=0.0)
    unit_discount_percentage = Column(Float, default=0.0)
    unit_discount_minimum_volume = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)
    length = Column(Float, default=0.0)
    width = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)
    url = Column(String)
    image_url = Column(String)
    break_even_sale_price = Column(Float, default=0)
    break_even_amazon_sale_price = Column(Float, default=0)
    hidden = Column(Boolean, default=False)


@mapper_registry.mapped
class Category:
    """Schema for Item records."""

    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    amazon_category = Column(String)
    amazon_min_price = Column(Float, default=0.0)
    amazon_max_price = Column(Float, default=0.0)
    amazon_average_price = Column(Float, default=0.0)
    amazon_deviation_price = Column(Float, default=0.0)
    amazon_total_results = Column(Integer, default=0)
    amazon_max_rating = Column(Float, default=0.0)
    amazon_min_rating = Column(Float, default=0.0)
    amazon_deviation_rating = Column(Float, default=0.0)
    amazon_average_rating = Column(Float, default=0.0)
    amazon_average_number_of_ratings = Column(Float, default=0.0)
    amazon_average_length = Column(Float, default=0.0)
    amazon_average_width = Column(Float, default=0.0)
    amazon_average_height = Column(Float, default=0.0)
    amazon_deviation_dimensions = Column(Float, default=0.0)
    amazon_average_weight = Column(Float, default=0.0)
    amazon_deviation_weight = Column(Float, default=0.0)
    amazon_fee = Column(Float, default=0.0)
    number_of_shopify_sites = Column(Integer, default=0)
    average_min_break_even = Column(Float, default=0)
    average_min_break_even_amazon = Column(Float, default=0)
    hidden = Column(Boolean, default=False)
    title_version = Column(Integer, default=1)


class Database:
    """Class which sets up procedures used for communicating with database."""

    @classmethod
    def _engine_url(cls):
        """Will return the DATABASE_URL. Useful for mocking."""
        return os.environ.get("DATABASE_URL", "sqlite:///database/finder.sqlite")

    def _database_configurations(self):
        """Will return the configuration when setting up the engine."""
        configuration = (
            {} if os.environ.get("DATABASE_TYPE") else {"check_same_thread": False}
        )

        return configuration

    def __init__(self):
        """Instantiate communication with the database."""
        self.engine = create_engine(
            self._engine_url(), connect_args=self._database_configurations()
        )
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        Base = mapper_registry.generate_base()
        Base.metadata.create_all(
            self.engine, Base.metadata.tables.values(), checkfirst=True
        )

        self.connection = self.engine.connect()

    def get_session(self):
        """Will return the session if it exists, if not it will create one."""
        if not hasattr(self, "session"):
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

        return self.session

    def cleanup(self):
        """Need to cleanup the db session if it still exists."""
        if hasattr(self, "session"):
            self.session.close()


database_instance = Database()
