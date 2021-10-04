import threading
from flask import render_template, jsonify

from scraper import scrape

from database.db import Database, Item as ItemDB, Category as CategoryDB, func

def index():
  session = Database().session
  item_count = session.query(func.count(ItemDB.id)).scalar()
  category_count = session.query(func.count(CategoryDB.id)).scalar()
  records = session.query(ItemDB, CategoryDB).join(CategoryDB).all()
  return render_template(
    'index.html', 
    records=records,
    item_count=item_count,
    category_count=category_count
    )

def categories():
  session = Database().session
  category_count = session.query(func.count(CategoryDB.id)).scalar()
  records = session.query(CategoryDB).all()
  return render_template(
    'categories.html', 
    records=records,
    category_count=category_count
    )

def api_scrape_all():
  scraper = threading.Thread(target=scrape.scrape_all())
  scraper.start()
  return jsonify(success=True)

def api_scrape_aliexpress():
  scraper = threading.Thread(target=scrape.scrape_aliexpress())
  scraper.start()
  return jsonify(success=True)

def api_scrape_amazon_fees():
  scraper = threading.Thread(target=scrape.scrape_amazon_fees())
  scraper.start()
  return jsonify(success=True)
  