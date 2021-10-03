from application import views

from flask import Flask
from flask import render_template

app = Flask(__name__)
app.add_url_rule('/', view_func=views.index)

def start():
  app.run()