import nltk
from application import views

from flask import Flask
from flask import render_template

app = Flask(__name__)
app.add_url_rule('/', view_func=views.index)
app.add_url_rule('/categories', view_func=views.categories)
app.add_url_rule('/scrape/all', view_func=views.api_scrape_all, methods=['POST'])
app.add_url_rule('/scrape/aliexpress', view_func=views.api_scrape_aliexpress, methods=['POST'])
app.add_url_rule('/scrape/amazon/fees', view_func=views.api_scrape_amazon_fees, methods=['POST'])
app.add_url_rule('/scrape/amazon/categories', view_func=views.api_scrape_amazon_categories, methods=['POST'])

def install_requirements():
  nltk.download('stopwords')
  nltk.download('punkt')
  nltk.download('averaged_perceptron_tagger')

def start():
  install_requirements()
  app.run()