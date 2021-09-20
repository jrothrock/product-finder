import sqlalchemy as db
from IPython import embed

class Database(object):
  def __init__(self):
    self.db = db
    self.engine = db.create_engine('sqlite:///test.sqlite')
    self.connection = self.engine.connect()
    self.metadata = db.MetaData()

  def item(self):
    item = None

    if db.inspect(self.engine).has_table('item') == True:
      item = db.Table('item', self.metadata, autoload=True, autoload_with=self.engine)
    else: 
      item = db.Table('item', self.metadata,
                db.Column('id', db.Integer(), primary_key=True , autoincrement=True),
                db.Column('title', db.String(255), nullable=False),
                db.Column('price', db.Float(), default=0.0), # Accuracy isn't very important here
                db.Column('shipping_price', db.Float(), default=0.0), # Accuracy isn't very important here
                db.Column('shipping_price_10_units', db.Float(), default=0.0), # Accuracy isn't very important here
                db.Column('length', db.Float(), default=0.0),
                db.Column('width', db.Float(), default=0.0),
                db.Column('height', db.Float(), default=0.0),
                db.Column('weight', db.Float(), default=0.0),
                db.Column('average_amazon_searches', db.Integer(), default=0),
                db.Column('average_amazon_price', db.Float(), default=0.0),
                db.Column('number_of_amazon_products', db.Integer(), default=0),
                )
      self.metadata.create_all(self.engine)
    
    return item