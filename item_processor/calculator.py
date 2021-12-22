import redis


class ItemCalculator:
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

    def __init__(self):
        self.redis = redis.Redis()

    def with_shopify():
        pass

    def get_items(self):
        item_ids = self.redis.lrange("queue:item", 0, -1)
