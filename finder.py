import nltk
import threading

from scraper import scrape
import application.app as app

def run_scraper():
  scrape.run()


def run_application():
  app.start()

def main():
  nltk.download('stopwords')
  nltk.download('punkt')
  nltk.download('averaged_perceptron_tagger')
  scraper = threading.Thread(target=run_scraper)
  scraper.start()
  run_application()

if __name__ == "__main__":
  main()