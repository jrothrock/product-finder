"""Module for adding logic to the various routes."""
import math

from flask import jsonify
from flask import render_template
from flask import request
from sqlalchemy import text

import tasks
from database.db import Category as CategoryDB
from database.db import Database
from database.db import Item as ItemDB
from database.db import func

PAGE_SIZE = 50


def index():
    """Logic for showing categories and items on index/home page."""
    session = Database().session
    item_count = session.query(func.count(ItemDB.id)).scalar()
    category_count = session.query(func.count(CategoryDB.id)).scalar()

    current_page = int(request.args.get("page", 1))
    zero_index_page = abs(current_page - 1)
    has_next_page = (math.ceil(item_count / PAGE_SIZE) - current_page) > 0

    records = (
        session.query(
            ItemDB,
            CategoryDB,
            (CategoryDB.amazon_average_price - ItemDB.break_even_sale_price).label(
                "profit"
            ),
        )
        .join(CategoryDB)
        .order_by(text("profit desc"))
        .limit(PAGE_SIZE)
        .offset(PAGE_SIZE * zero_index_page)
        .all()
    )

    session.close()
    return render_template(
        "index.html",
        records=records,
        item_count=item_count,
        category_count=category_count,
        current_page=current_page,
        has_next_page=has_next_page,
    )


def categories():
    """Logic for categories on the categories page."""
    session = Database().session
    category_count = session.query(func.count(CategoryDB.id)).scalar()

    current_page = int(request.args.get("page", 1))
    zero_index_page = abs(current_page - 1)
    has_next_page = (math.ceil(category_count / PAGE_SIZE) - current_page) > 0

    records = (
        session.query(
            CategoryDB,
            (
                CategoryDB.amazon_average_price
                - CategoryDB.average_min_break_even_amazon
            ).label("profit"),
        )
        .order_by(text("profit desc"))
        .limit(PAGE_SIZE)
        .offset(PAGE_SIZE * zero_index_page)
        .all()
    )

    session.close()
    return render_template(
        "categories.html",
        records=records,
        category_count=category_count,
        current_page=current_page,
        has_next_page=has_next_page,
    )


def category(category_id):
    """Logic for showing a specific category page."""
    session = Database().session
    item_count = (
        session.query(ItemDB, CategoryDB)
        .join(CategoryDB)
        .filter(CategoryDB.id == category_id)
        .count()
    )

    current_page = int(request.args.get("page", 1))
    zero_index_page = abs(current_page - 1)
    has_next_page = (math.ceil(item_count / PAGE_SIZE) - current_page) > 0

    records = (
        session.query(
            ItemDB,
            CategoryDB,
            (CategoryDB.amazon_average_price - ItemDB.break_even_sale_price).label(
                "profit"
            ),
        )
        .join(CategoryDB)
        .filter(CategoryDB.id == category_id)
        .limit(PAGE_SIZE)
        .offset(PAGE_SIZE * zero_index_page)
        .all()
    )

    session.close()
    return render_template(
        "category.html",
        records=records,
        count=item_count,
        current_page=current_page,
        has_next_page=has_next_page,
    )


def items():
    """Logic for showing items on the item page."""
    session = Database().session
    item_count = session.query(func.count(ItemDB.id)).scalar()

    current_page = int(request.args.get("page", 1))
    zero_index_page = abs(current_page - 1)
    has_next_page = (math.ceil(item_count / PAGE_SIZE) - current_page) > 0

    records = (
        session.query(
            ItemDB,
            CategoryDB,
            (CategoryDB.amazon_average_price - ItemDB.break_even_sale_price).label(
                "profit"
            ),
        )
        .join(CategoryDB)
        .limit(PAGE_SIZE)
        .offset(PAGE_SIZE * zero_index_page)
        .all()
    )

    session.close()
    return render_template(
        "items.html",
        item_count=item_count,
        records=records,
        current_page=current_page,
        has_next_page=has_next_page,
    )


def item(item_id):
    """Logic for showing a specific item page."""
    session = Database().session

    records = (
        session.query(
            ItemDB,
            CategoryDB,
            (CategoryDB.amazon_average_price - ItemDB.break_even_sale_price).label(
                "profit"
            ),
        )
        .join(CategoryDB)
        .filter(ItemDB.id == item_id)
        .all()
    )

    session.close()
    return render_template("item.html", records=records)


def api_scrape_all():
    """Logic for starting scraping all task."""
    tasks.scrape_all.delay()
    return jsonify(success=True)


def api_scrape_aliexpress():
    """Logic for starting alixpress scraping task."""
    tasks.scrape_aliexpress.delay()
    return jsonify(success=True)


def api_scrape_amazon_fees():
    """Logic for starting amazon fees scraping task."""
    tasks.scrape_amazon_fees.delay()
    return jsonify(success=True)


def api_scrape_amazon_categories():
    """Logic for starting amazon categories scraping task."""
    tasks.scrape_amazon_categories.delay()
    return jsonify(success=True)


def api_scrape_shopify_categories():
    """Logic for starting shopify categories scraping task."""
    tasks.scrape_shopify_categories.delay()
    return jsonify(success=True)


def api_run_calculator():
    """Logic for starting calculations task."""
    tasks.calculate_all.delay()
    return jsonify(success=True)
