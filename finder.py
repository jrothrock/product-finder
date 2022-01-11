import application.app as app
import scraper.scrape as scrape
import calculator.calculator as calculator


def run_application():
    # app.start()
    # scrape.scrape_aliexpress()
    # scrape.scrape_amazon_categories()
    # scrape.scrape_amazon_fees()
    # scrape.scrape_shopify_categories()
    calculator.calculate_all()


def main():
    run_application()


if __name__ == "__main__":
    main()
