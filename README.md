# Item finder.

Finds whether a certain item on Aliexpress or Alibaba can be sold on Amazon profitably. Use ahrefs to calculate whether there is significant search volume if in niche area

# Design

TBD on whether cron based or daemons. Probably will use PostgreSQL and Redis (maybe). 

Items are first scraped on Aliexpress or Alibaba

Uses statsd and grafana to track scraping errors (low priority)

Flask server which does a basic load of items out of PostgreSQL and presents them on a page. Will need to figure out a way to paginate, or just sort them 

# Potential items sites:
Alibaba
Aliexpress
DHGate
...

# Todo:
Customs
 - figure out costs
Returns
 - figure out costs (may just be worth calling these lost)

Incorporate other selling modes such as Ebay or Shopify

Work on items dimensions regex. I think I may have some disconnect between what python actual does and what regex101 shows
May want to to put threads into Flask's `g` variable, as well as keeping the state it is in (running, finished, etc.)
## Issues. 

Ebay only allows a few items to be sold (may require membership or a few sales, can't remember)

Shopify will require google shopping feeds and a Return on Advertising will have to be calculated in the item processor

Additionally, with the two above, shipping will have to be calculated either through USPS using the dimensions scraped

This is curently done for Amazon using the FBA page:
https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index

Check implications of using `check_same_thread=true` which fixed the sqlalchemy thread error.