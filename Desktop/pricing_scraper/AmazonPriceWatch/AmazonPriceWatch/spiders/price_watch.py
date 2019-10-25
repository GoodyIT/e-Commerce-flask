# -*- coding: utf-8 -*-
import scrapy, pymongo, datetime, time, pprint, re
from urllib.parse import urlparse
from bson import ObjectId


class PriceWatchSpider(scrapy.Spider):
    name = 'price_watch'
    allowed_domains = [
        'gear.blizzard.com',
        'na.merch.riotgames.com',
        'nanoleaf.me',
        'shop.nordstrom.com',
        'store.steampowered.com',
        'www.amazon.com',
        'www.bestbuy.com',
        'www.kontrolfreek.com',
    ]
    collection = None

    def start_requests(self):
        client = pymongo.MongoClient()
        db = client.price_watch
        self.collection = db.products
        for product in self.collection.find():
            if product['URL']:
                yield scrapy.Request(
                    url = product['URL'],
                    meta = {'product_id': str(product['_id'])},
                    callback = self.parse
                )

    def parse(self, response):
        url_data = urlparse(response.url)
        product_id = response.meta.get('product_id')
        #pprint.pprint([url_data.hostname, product_id])
        price = None
        if url_data.hostname == 'www.amazon.com':
            price_sel = response.xpath('//span[@id="priceblock_ourprice"]/text()')
            #print('%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            #print(response.text)
            #print('%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            if price_sel:
                price_txt = price_sel.extract_first()
                price = float(price_txt.strip().replace('$', '').replace(',', '.').strip())
        elif url_data.hostname == 'store.steampowered.com':
            price_sel = response.xpath('//div[@class="game_purchase_action_bg"]/div[contains(@class, "game_purchase_price")]/text()')
            if price_sel:
                price_txt = price_sel.extract_first()
                price = float(price_txt.strip().replace('€', '').replace(',', '.').strip())
        if price:
            #push_it = False
            push_it = True
            document = self.collection.find_one({'_id': ObjectId(product_id)})
            print('@@@@@@@@@@@@@@@@@@@')
            pprint.pprint(document)
            print('@@@@@@@@@@@@@@@@@@@')
            #if not isinstance(document['Last Check - Price'], list):
                #self.collection.update({}, {'$unset': {'Last Check - Time':1}}, False, True);
                #self.collection.update({}, {'$unset': {'Last Check - Price':1}}, False, True);
                #push_it = True
            #elif document['Last Check - Price'][-1] != price:
                #push_it = True

            if push_it:
                self.collection.update_one(
                    { '_id': ObjectId(product_id) },
                    { '$push': { 'Last Check - Time': datetime.datetime.now() } },
                    upsert = True
                )
                self.collection.update_one(
                    { '_id': ObjectId(product_id) },
                    { '$push': { 'Last Check - Price': price } },
                    upsert = True
                )
                document2 = self.collection.find_one({'_id': ObjectId(product_id)})
                print('###################')
                pprint.pprint(document2)
                print('###################')
