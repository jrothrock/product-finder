import logging

import redis

import utils.system as system
from database.db import Database, Category as CategoryDB

AD_CONVERSION_PERCENTAGE = 0.02
LOW_CPC_DOLLARS = 0.1
MEDIUM_CPC_DOLLARS = 0.4
HIGH_CPC_DOLLARS = 5
RETURN_RATE_PERCENTAGE = 0.05
SHOPIFY_MONTHLY_DOLLARS = 29.00
RETURN_ON_AD_SPEND_PERCENTAGE = 400
DOMAIN_YEARLY_DOLLARS = 15
EMAIL_MONTHLY_DOLLARS = 7
LLC_YEARLY_DOLLARS = 50
VIRTUAL_ADDRESS_MONTHLY_DOLALRS = 30

# May use later
# FIVERR_COPYWRITING_DESCRIPTION = 30 # 300 words at 10 cents a word


class CategoryCalculator:
    def __init__(self):
        self.redis = redis.Redis()

    def _check_categories(self):
        category_ids = self.redis.lrange("queue:category:calculator", 0, -1)
        self.redis.delete("queue:category:calculator")
        self._process_categories(category_ids)
    
    def _process_categories(self, category_ids):
        for category_id in category_ids:
          try:
              self._calculate_category(category_id)
          except KeyboardInterrupt:
              system.exit()
          except Exception as e:
              logging.exception(
                  f"Exception calculations catgory: {e.__dict__}"
              )
              pass
        
    def _calculate_category(category_id):
        pass
      
    @classmethod
    def run(cls):
        cls()._check_categories()


class ItemCalculator:
    def __init__(self):
        self.redis = redis.Redis()

    def _check_items(self):
        item_ids = self.redis.lrange("queue:item:calculator", 0, -1)
        self.redis.delete("queue:item:calculator")
        self._process_items(item_ids)

    def _process_items(self, item_ids):
        for category_id in item_ids:
            try:
                self._calculate_category(category_id)
            except KeyboardInterrupt:
                system.exit()
            except Exception as e:
                logging.exception(
                    f"Exception calculations item: {e.__dict__}"
                )
                pass
      
    def _calculate_category(self, category_id):
        pass

    @classmethod
    def run(cls):
        cls()._check_items()


def calculate_categories():
  CategoryCalculator.run()

def calculate_items():
  ItemCalculator.run()

def calculate_all():
  calculate_categories()
  calculate_items()
