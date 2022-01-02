import threading

from flask import render_template, jsonify

from calculator.calculator import Calculator
from scraper import scrape
from database.db import Database, Item as ItemDB, Category as CategoryDB, func


def index():
    session = Database().session
    item_count = session.query(func.count(ItemDB.id)).scalar()
    category_count = session.query(func.count(CategoryDB.id)).scalar()
    records = session.query(ItemDB, CategoryDB).join(CategoryDB).all()
    session.close()
    return render_template(
        "index.html",
        records=records,
        item_count=item_count,
        category_count=category_count,
    )


def categories():
    session = Database().session
    category_count = session.query(func.count(CategoryDB.id)).scalar()
    records = session.query(CategoryDB).all()
    session.close()
    return render_template(
        "categories.html", records=records, category_count=category_count
    )


def category(category_id):
    session = Database().session
    records = (
        session.query(ItemDB, CategoryDB)
        .join(CategoryDB)
        .filter(CategoryDB.id == category_id)
        .all()
    )
    count = (
        session.query(ItemDB, CategoryDB)
        .join(CategoryDB)
        .filter(CategoryDB.id == category_id)
        .count()
    )
    session.close()
    return render_template("category.html", records=records, count=count)


def calculations():
    return render_template("calculations.html")


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


def api_scrape_amazon_categories():
    scraper = threading.Thread(target=scrape.scrape_amazon_categories())
    scraper.start()
    return jsonify(success=True)


def api_scrape_shopify_categories():
    scraper = threading.Thread(target=scrape.scrape_shopify_categories())
    scraper.start()
    return jsonify(success=True)


def api_run_calculator():
    return jsonify(success=True)
