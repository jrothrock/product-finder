"""Module that houses procedures and schemas for the database."""
# Honestly, I should have gone with a non relational database.
import os

import sqlalchemy as db
from sqlalchemy import (  # noqa: F401
    func,
    Column,
    create_engine,
    MetaData,
    Float,
    String,
    ForeignKey,
    Integer,
    Boolean,
)
from sqlalchemy.orm import registry, sessionmaker

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
    break_even_sale_price = Column(Float, default=False)
    break_even_amazon_sale_price = Column(Float, default=False)
    hidden = Column(Float, default=False)


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
    hidden = Column(Float, default=False)
    title_version = Column(Integer, default=1)


class Database:
    """Class which sets up procedures used for communicating with database."""

    def __init__(self):
        """Instantiate communication with the database."""
        self.db = db
        db_username = os.environ.get("DB_USERNAME")
        db_password = os.environ.get("DB_PASSWORD")
        if db_username:
            engine = (
                f"postgresql://{db_username}:{db_password}@localhost:5432/scraperdb"
            )
        else:
            engine = "sqlite:///database/test.sqlite"
        self.engine = create_engine(engine, connect_args={"check_same_thread": False})
        Base = mapper_registry.generate_base()
        Base.metadata.create_all(
            self.engine, Base.metadata.tables.values(), checkfirst=True
        )
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
