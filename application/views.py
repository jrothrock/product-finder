from flask import render_template

from database.db import Database, Item as ItemDB, Category as CategoryDB

def index():
  records = Database().session.query(ItemDB, CategoryDB).join(CategoryDB).all()
  return render_template('index.html', records=records)