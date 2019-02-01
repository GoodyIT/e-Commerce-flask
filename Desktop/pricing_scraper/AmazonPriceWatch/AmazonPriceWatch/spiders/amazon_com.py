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
    FORM_HEADERS = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    collection = None
    cart_page_url = 'https://www.amazon.com/gp/cart/view.html?ref_=nav_cart'

    def _build_metadata1(self):
        return ''

    def parse(self, response):
        login_form_page_url = response.xpath('//a[contains(@href, "sign")]/@href').extract_first()
        print('login_form_page_url = ', login_form_page_url)
        yield scrapy.Request(
            url = login_form_page_url,
            callback = self.fill_login_form,
            meta = {'dont_cache': True}
        )

    def fill_login_form(self, response):
        form_sel = response.xpath('//form[@name="signIn"]')
        action = form_sel.xpath('./@action').extract_first()
        method = form_sel.xpath('./@method').extract_first().upper()
        inputs_sel = form_sel.xpath('.//input')
        body = {}
        for item in inputs_sel:
            typ = item.xpath('./@type').extract_first()

            if typ == 'email':
                key = item.xpath('./@name').extract_first()
                body[key] = self.USER_NAME
            elif typ == 'password':
                key = item.xpath('./@name').extract_first()
                body[key] = self.PASSWORD
            else:
                key = item.xpath('./@name').extract_first()
                val = item.xpath('./@value').extract_first()
                if key is not None:
                    body[key] = val
        import pprint
        pprint.pprint(body)

        print('action = ', action)

        body['metadata1'] = self._build_metadata1()
        yield scrapy.Request(
            action,
            method = method,
            headers = self.FORM_HEADERS,
            body = json.dumps(body),
            meta = {
                'dont_retry': True,
                'dont_cache': True
            },
            dont_filter = True,
            callback = self.after_login,
            errback = self.login_error
        )

    def login_error(self, failure):
        print('#######################')
        print(failure.value.response.status)
        print('#######################')

    def after_login(self, response):
        print('#######################')
        print('after_login')
        print('#######################')
        client = pymongo.MongoClient()
        db = client.price_watch
        self.collection = db.products
        #for product in self.collection.find():
            #if product['URL']:
                #url_data = urlparse(product['URL'])
                #if url_data.hostname == 'www.amazon.com':
        product_url = 'https://www.amazon.com/DECORA-Pieces-Wiggle-Googly-Self-adhesive/dp/B01LWIYJH3/ref=lp_17324748011_1_1?srs=17324748011&ie=UTF8&qid=1544691752&sr=8-1'
        yield scrapy.Request(
            url = product_url, #product['URL'],
            meta = {'product_id': str(123)},#product['_id'])},
            callback = self.product_page
        )

    def product_page(self, response):
        print('#######################')
        print('product_page')
        print('#######################')

        product_id = response.meta.get('product_id')
        form_sel = response.xpath('//form[@id="addToCart"]')
        action = response.urljoin(form_sel.xpath('./@action').extract_first())
        method = form_sel.xpath('./@method').extract_first().upper()
        inputs_sel = form_sel.xpath('.//input')
        body = {}
        for item in inputs_sel:
            typ = item.xpath('./@type').extract_first()
            if typ == 'hidden':
                key = item.xpath('./@name').extract_first()
                val = item.xpath('./@value').extract_first()
                body[key] = val
        body['quantity'] = '1'
        body['submit.add-to-cart'] = 'Add to Cart'
        yield scrapy.Request(
            action,
            method = method,
            headers = self.FORM_HEADERS,
            body = json.dumps(body),
            meta = {
                'dont_retry': True,
                'dont_cache': True,
                'product_id': product_id
            },
            dont_filter = True,
            callback = self.added_to_cart
        )

    def added_to_cart(self, response):
        print('#######################')
        print('added_to_card')
        print('#######################')

        product_id = response.meta.get('product_id')
        # go to cart
        yield scrapy.Request(
            self.cart_page_url,
            meta = {'product_id': product_id},
            dont_filter = True,
            callback = self.cart_page
        )

    def cart_page(self, response):
        print('#######################')
        print('card_page')
        print('#######################')

        product_id = response.meta.get('product_id')
        form_sel = response.xpath('//form[@id="gutterCartViewForm"]')
        action = response.urljoin(form_sel.xpath('./@action').extract_first())
        method = form_sel.xpath('./@method').extract_first().upper()
        inputs_sel = form_sel.xpath('.//input')
        body = {}
        for item in inputs_sel:
            key = item.xpath('./@name').extract_first()
            val = item.xpath('./@value').extract_first()
            body[key] = val
        yield scrapy.Request(
            action,
            method = method,
            body = json.dumps(body),
            meta = {
                'dont_retry': True,
                'dont_cache': True,
                'product_id': product_id
            },
            dont_filter = True,
            callback = self.checkout_page
        )

    def checkout_page(self, response):
        print('#######################')
        print('checkout_page')
        print('#######################')

        product_id = response.meta.get('product_id')
        div_sel = response.xpath('//div[@id="subtotals-marketplace-table"]')
        price_str = div_sel.xpath('.//td[contains(@class, "grand-total-price")]/strong/text()').extract_first()
        price = float(price_str.replace('USD', '').strip())
        # go to cart again to empty
        yield scrapy.Request(
            self.cart_page_url,
            meta = {'product_id': product_id, 'price': price},
            dont_filter = True,
            callback = self.empty_cart
        )

    def empty_cart(self, response):
        print('#######################')
        print('empty_card')
        print('#######################')

        product_id = response.meta.get('product_id')
        price = response.meta.get('price')
        form_sel = response.xpath('//form[@id="activeCartViewForm"]')
        action = response.urljoin(form_sel.xpath('./@action').extract_first())
        method = form_sel.xpath('./@method').extract_first().upper()
        inputs_sel = form_sel.xpath('.//input[@type="hidden"]')
        body = {}
        for item in inputs_sel:
            key = item.xpath('./@name').extract_first()
            val = item.xpath('./@value').extract_first()
            body[key] = val
        delete_sel = form_sel.xpath('.//input[@type="submit"][contains(@name,"delete")]')
        key = delete_sel.xpath('./@name').extract_first()
        val = delete_sel.xpath('./@value').extract_first()
        body[key] = val
        yield scrapy.Request(
            action,
            method = method,
            headers = self.FORM_HEADERS,
            body = json.dumps(body),
            meta = {
                'dont_retry': True,
                'dont_cache': True,
                'product_id': product_id,
                'price': price
            },
            dont_filter = True,
            callback = self.save_price
        )

    def save_price(self, response):
        print('#######################')
        print('save_price')
        print('#######################')

        product_id = response.meta.get('product_id')
        price = response.meta.get('price')
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

