from redis import Redis
from sqlalchemy.orm.exc import NoResultFound

from database.db import Category as CategoryDB, Database as db

from IPython import embed
class Category(db):

  def __init__(self):
    super().__init__()

  def find_or_create(self, **kwargs):
    title = self.create_title(kwargs["category_words"])
    try:
      category = self.session.query(CategoryDB).filter_by(title=title).one() # filter on name
    except NoResultFound:
      category = self.new(**kwargs)
    
    return category

  def new(self, **kwargs):
    title = self.create_title(kwargs["category_words"])
    new_category = CategoryDB(title=title)
    self.session.add(new_category)
    self.session.commit()
    self.session.refresh(new_category)
    self.add_to_redis_queue(new_category)
    return new_category
  
  def create_title(self, values):
    # TODO need to investigate why values is type None
    if values == None or len(values) == 0:
      return ""
    else:
      values.sort()
      return '_'.join(values)

  def add_to_redis_queue(self, new_category):
    Redis().lpush("queue:category", new_category.id)
