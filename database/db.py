import sqlalchemy as db
from sqlalchemy import (
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

from IPython import embed

mapper_registry = registry()


@mapper_registry.mapped
class Item:
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
    item_processed = Column(Boolean, default=False)


@mapper_registry.mapped
class Category:
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    amazon_min_price = Column(Float, default=0.0)
    amazon_max_price = Column(Float, default=0.0)
    amazon_average_price = Column(Float, default=0.0)
    amazon_total_results = Column(Integer, default=0)
    amazon_max_rating = Column(Float, default=0.0)
    amazon_min_rating = Column(Float, default=0.0)
    amazon_average_rating = Column(Float, default=0.0)
    amazon_average_number_of_ratings = Column(Float, default=0.0)
    number_of_shopify_sites = Column(Integer, default=0)


class Database:
    def __init__(self):
        self.db = db
        self.engine = create_engine(
            "sqlite:///database/test.sqlite", connect_args={"check_same_thread": False}
        )
        Base = mapper_registry.generate_base()
        Base.metadata.create_all(
            self.engine, Base.metadata.tables.values(), checkfirst=True
        )
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
