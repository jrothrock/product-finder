from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
import sqlalchemy as db
from sqlalchemy.orm import registry
from sqlalchemy.orm import sessionmaker
from IPython import embed

mapper_registry = registry()

@mapper_registry.mapped
class Item:
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    category_id = Column(ForeignKey("category.id"))
    title = Column(String)
    price = Column(Float, default=0.0)
    shipping_price = Column(Float, default=0.0)
    shipping_price_10_units = Column(Float, default=0.0)
    length = Column(Float, default=0.0)
    width = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)
    url = Column(String)

@mapper_registry.mapped
class Category:
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    title = Column(String)

class Database:
  def __init__(self):
    self.db = db
    self.engine = db.create_engine('sqlite:///test.sqlite')
    Base = mapper_registry.generate_base()
    Base.metadata.create_all(self.engine, Base.metadata.tables.values(),checkfirst=True)
    self.connection = self.engine.connect()
    self.metadata = db.MetaData()
    Session = sessionmaker(bind=self.engine)
    self.session = Session()