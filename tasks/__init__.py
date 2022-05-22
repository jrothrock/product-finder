"""Background tasks subpackage used for periodicly scraping product sites."""
import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_postrun
from psutil import Process

import broker
import calculator
import scraper
from utils import nltk as _nltk

app = Celery("tasks", broker=f"{broker.REDIS_URL}/0")


@app.on_after_configure.connect
def install_nltk_resources(**kwargs):
    """Install the neccessary nltk resources."""
    _nltk.download_nltk_resources()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up the periodic tasks to run."""
    sender.add_periodic_task(
        crontab(minute=0), scrape_aliexpress.s(), name="Scape Aliexpress"
    )

    sender.add_periodic_task(
        crontab(minute=15), scrape_amazon_categories.s(), name="Scape Amazon Categories"
    )

    sender.add_periodic_task(
        crontab(minute=30), scrape_amazon_fees.s(), name="Scape Amazon Fees"
    )

    sender.add_periodic_task(
        crontab(minute=45),
        scrape_shopify_categories.s(),
        name="Scape Shopify Categories",
    )

    sender.add_periodic_task(crontab(minute=50), calculate_all.s(), name="Calculate")


@app.task
def scrape_aliexpress():
    """Periodic task to scrape Aliexpress products."""
    scraper.scrape_aliexpress()


@app.task
def scrape_amazon_categories():
    """Periodic task to scrape Amazon Categories."""
    scraper.scrape_amazon_categories()


@app.task
def scrape_amazon_fees():
    """Periodic task to scrape both Amazon Fees for Categories and Items."""
    scraper.scrape_amazon_fees()


@app.task
def scrape_shopify_categories():
    """Periodic task to scrape Shopify store counts for Category."""
    scraper.scrape_shopify_categories()


@app.task
def scrape_all():
    """Periodic task to scrape all product related sites."""
    scraper.scrape_all()


@app.task
def calculate_all():
    """Periodic tasks to run calculations on all products."""
    calculator.calculate_all()


@task_postrun.connect
def reap_child_processes(**kwargs):
    """DIRTY! Will reap all child processes after each task runs."""
    # See the following issues:
    #  * https://github.com/celery/celery/issues/2353
    #  * https://github.com/jrothrock/product-finder/issues/31
    # We need to kill all spawned child processes -- mainly firefox.
    process_id = os.getpid()
    process = Process(process_id)
    for child in process.children(recursive=True):
        child.kill()
