from utils.database import Category as CategoryDB
from utils.database import Database as db
from IPython import embed
from sqlalchemy.orm.exc import NoResultFound

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
    return new_category
  
  def create_title(self, values):
    # TODO need to investigate why values is type None
    if values == None or len(values) == 0:
      return ""
    else:
      values.sort()
      return '_'.join(values)
