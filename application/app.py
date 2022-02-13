"""Module that creates Flask app and sets up routing."""
import nltk
from flask import Flask

from application import views

app = Flask(__name__)
app.add_url_rule("/", view_func=views.index)
app.add_url_rule("/categories", view_func=views.categories)
app.add_url_rule("/category/<int:category_id>", view_func=views.category)
app.add_url_rule("/items", view_func=views.items)
app.add_url_rule("/item/<int:item_id>", view_func=views.item)
app.add_url_rule("/api/scrape/all", view_func=views.api_scrape_all, methods=["POST"])
app.add_url_rule(
    "/api/scrape/aliexpress", view_func=views.api_scrape_aliexpress, methods=["POST"]
)
app.add_url_rule(
    "/api/scrape/amazon/fees", view_func=views.api_scrape_amazon_fees, methods=["POST"]
)
app.add_url_rule(
    "/api/scrape/amazon/categories",
    view_func=views.api_scrape_amazon_categories,
    methods=["POST"],
)
app.add_url_rule(
    "/api/scrape/shopify/categories",
    view_func=views.api_scrape_shopify_categories,
    methods=["POST"],
)
app.add_url_rule(
    "/api/run/calculator",
    view_func=views.api_run_calculator,
    methods=["POST"],
)


# TODO: Investigate moving this.
def install_requirements():
    """Install necessary nltk packages used for language utils."""
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")


def start():
    """DEV: Easy to use interface to download needed requirements and start flask app."""
    install_requirements()
    app.run(host='0.0.0.0')


def wsgi():
    """PROD: Easy to use interface to download needed requirements and start flask app."""
    install_requirements()
    return app
