import application.app as app
import scraper.scrape as scrape


def run_application():
    app.start()


def main():
    run_application()
    scrape.scrape_amazon_categories()


if __name__ == "__main__":
    main()
