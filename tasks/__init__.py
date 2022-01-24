"""Background tasks subpackage used for periodicly scraping product sites."""
from celery import Celery
from celery.schedules import crontab

import scraper
import calculator

app = Celery("tasks", broker="redis://localhost:6379/0")


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
        crontab(minute=30), scrape_amazon_fees.s(), name="Scape Shopify Categories"
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
