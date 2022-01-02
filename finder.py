import application.app as app
import scraper.scrape as scrape


def run_application():
    # app.start()
    scrape.scrape_amazon_categories()


def main():
    run_application()


if __name__ == "__main__":
    main()
