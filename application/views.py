import math

from flask import render_template, jsonify, request
from sqlalchemy import text
from IPython import embed

import tasks
from database.db import Database, Item as ItemDB, Category as CategoryDB, func

PAGE_SIZE = 50


def index():
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
    tasks.scrape_all()
    return jsonify(success=True)


def api_scrape_aliexpress():
    tasks.scrape_aliexpress()
    return jsonify(success=True)


def api_scrape_amazon_fees():
    tasks.scrape_amazon_fees()
    return jsonify(success=True)


def api_scrape_amazon_categories():
    tasks.scrape_amazon_categories()
    return jsonify(success=True)


def api_scrape_shopify_categories():
    tasks.scrape_shopify_categories()
    return jsonify(success=True)


def api_run_calculator():
    tasks.calculate_all()
    return jsonify(success=True)
