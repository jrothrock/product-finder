import nltk
from application import views

from flask import Flask

app = Flask(__name__)
app.add_url_rule("/", view_func=views.index)
app.add_url_rule("/categories", view_func=views.categories)
app.add_url_rule("/category/<int:category_id>", view_func=views.category)
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


def install_requirements():
    nltk.download("stopwords")
    nltk.download("punkt")
    nltk.download("averaged_perceptron_tagger")


def start():
    install_requirements()
    app.run()
