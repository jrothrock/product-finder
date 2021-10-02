import sqlalchemy as db
from sqlalchemy.orm import registry, sessionmaker

from IPython import embed

mapper_registry = registry()

@mapper_registry.mapped
class Item:
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.ForeignKey("category.id"))
    title = db.Column(db.String)
    price = db.Column(db.Float, default=0.0)
    shipping_price = db.Column(db.Float, default=0.0)
    shipping_price_10_units = db.Column(db.Float, default=0.0)
    amazon_category = db.Column(db.String)
    amazon_fee = db.Column(db.Float, default=0.0)
    single_break_even_price = db.Column(db.Float, default=0.0)
    multi_break_even_price = db.Column(db.Float, default=0.0)
    unit_discount_percentage = db.Column(db.Float, default=0.0)
    unit_discount_minimum_volume = db.Column(db.Integer, default=0)
    available_quantity = db.Column(db.Integer, default=0)
    length = db.Column(db.Float, default=0.0)
    width = db.Column(db.Float, default=0.0)
    height = db.Column(db.Float, default=0.0)
    weight = db.Column(db.Float, default=0.0)
    url = db.Column(db.String)
    item_processed = db.Column(db.Boolean, default=False)

@mapper_registry.mapped
class Category:
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    amazon_min_price = db.Column(db.Float, default=0.0)
    amazon_max_price = db.Column(db.Float, default=0.0)
    amazon_total_results = db.Column(db.Integer, default=0)
    amazon_max_ratings = db.Column(db.Float, default=0.0)
    amazon_min_ratings = db.Column(db.Float, default=0.0)
    amazon_average_ratings = db.Column(db.Float, default=0.0)

class Database:
  def __init__(self):
    self.db = db
    self.engine = db.create_engine('sqlite:///database/test.sqlite')
    Base = mapper_registry.generate_base()
    Base.metadata.create_all(self.engine, Base.metadata.tables.values(),checkfirst=True)
    self.connection = self.engine.connect()
    self.metadata = db.MetaData()
    Session = sessionmaker(bind=self.engine)
    self.session = Session()