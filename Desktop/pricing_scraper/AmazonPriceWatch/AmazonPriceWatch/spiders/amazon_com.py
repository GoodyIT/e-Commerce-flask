# -*- coding: utf-8 -*-
import scrapy, pymongo, datetime, time, pprint, re, json
from urllib.parse import urlparse
from bson import ObjectId


class AmazonComSpider(scrapy.Spider):
    name = 'amazon_com'
    allowed_domains = ['amazon.com']
    start_urls = ['https://amazon.com/']

    USER_NAME = ''
    PASSWORD = ''
    collection = None
    cart_page_url = 'https://www.amazon.com/gp/cart/view.html?ref_=nav_cart'

    def _build_metadata1(self):
        return ''

    def parse(self, response):
        login_form_page_url = response.xpath('//a[contains(@href, "sign")]/@href').extract_first()
        yield scrapy.Request(
            url = login_form_page_url,
            callback = self.fill_login_form,
            meta = {'dont_cache': True}
        )

    def fill_login_form(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formname = 'signIn',
            formdata = {'email': self.USER_NAME, 'password': self.PASSWORD},
            callback = self.after_login
        )

    def after_login(self, response):
        # check login succeed before going on
        if b"authentication failed" in response.body:
            self.logger.error("Login failed")
        else:
            self.logger.info("Login successful")
            client = pymongo.MongoClient()
            db = client.price_watch
            self.collection = db.products
            for product in self.collection.find():
                if 'URL' in product and product['URL']:
                    url_data = urlparse(product['URL'])
                    if url_data.hostname == 'www.amazon.com':
                        yield scrapy.Request(
                            url = product['URL'],
                            meta = {'product_id': str(product['_id'])},
                            dont_filter = True,
                            callback = self.product_page
                        )

    def product_page(self, response):
        if response.xpath('//input[@name="submit.add-to-cart"]'):
            product_id = response.meta.get('product_id')
            yield scrapy.FormRequest.from_response(
                response,
                formid = 'addToCart',
                clickdata = {'name': 'submit.add-to-cart'},
                formdata = {'quantity': '1'},
                meta = {'product_id': product_id},
                dont_filter = True,
                callback = self.added_to_cart
            )
        else:
            return None

    def added_to_cart(self, response):
        product_id = response.meta.get('product_id')
        # go to cart
        yield scrapy.Request(
            self.cart_page_url,
            meta = {'product_id': product_id},
            dont_filter = True,
            callback = self.cart_page
        )

    def cart_page(self, response):
        product_id = response.meta.get('product_id')
        yield scrapy.FormRequest.from_response(
            response,
            formid = 'gutterCartViewForm',
            meta = {'product_id': product_id},
            dont_filter = True,
            callback = self.checkout_page
        )

    def checkout_page(self, response):
        product_id = response.meta.get('product_id')
        div_sel = response.xpath('//div[@id="subtotals-marketplace-table"]')
        price_str = div_sel.xpath('.//td[contains(@class, "grand-total-price")]/strong/text()').extract_first()
        if price_str:
            price = float(price_str.replace('USD', '').strip())
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
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(product_id)
            print(price)
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        # go to cart again to empty
        yield scrapy.Request(
            self.cart_page_url,
            dont_filter = True,
            callback = self.empty_cart
        )

    def empty_cart(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formid = 'activeCartViewForm',
            clickdata = {'value': 'Delete'},
            callback = self.cart_emptied
        )

    def cart_emptied(self, response):
        self.logger.info("Cart is empty")
        return None

