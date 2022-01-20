from celery import Celery
from celery.schedules import crontab

import scraper
import calculator

app = Celery('tasks', broker='redis://localhost:6379/0')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=0), scrape_aliexpress.s(), name='Scape Aliexpress')

    sender.add_periodic_task(crontab(minute=15), scrape_amazon_categories.s(), name='Scape Amazon Categories')

    sender.add_periodic_task(crontab(minute=30), scrape_amazon_fees.s(), name='Scape Shopify Categories')

    sender.add_periodic_task(crontab(minute=45), scrape_shopify_categories.s(), name='Scape Shopify Categories')

    sender.add_periodic_task(crontab(minute=50), calculate_all.s(), name='Calculate')

@app.task
def scrape_aliexpress():
    scraper.scrape_aliexpress()

@app.task
def scrape_amazon_categories():
    scraper.scrape_amazon_categories()

@app.task
def scrape_amazon_fees():
    scraper.scrape_amazon_fees()

@app.task
def scrape_shopify_categories():
    scraper.scrape_shopify_categories()

@app.task
def scrape_all():
    scraper.scrape_all()

@app.task
def calculate_all():
    calculator.calculate_all()
