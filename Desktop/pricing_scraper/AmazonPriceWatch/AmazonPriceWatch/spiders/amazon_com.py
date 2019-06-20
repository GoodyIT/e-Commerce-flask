# -*- coding: utf-8 -*-
import scrapy, csv, pprint, re, json, configparser
from urllib.parse import urlparse


class AmazonComSpider(scrapy.Spider):
    name = 'amazon_com'
    allowed_domains = ['amazon.com']
    start_urls = ['https://amazon.com/']
    first_part = 'https://www.amazon.com'

    active_config = 'midas'
    LOGIN_EMAIL = None
    LOGIN_PASSWORD = None
    collection = None
    LOGGED_IN = False
    cart_page_url = 'https://www.amazon.com/gp/cart/view.html?ref_=nav_cart'
    products_passed = []
    fieldnames = ['ID', 'Name', 'Price', 'Group', 'Category', 'Vendor', 'URL']
    changed_product_ids = []
    input_file = 'test_items.tsv'
    #output_file = 'test_items_output.tsv'


    def __init__(self, category = None, *args, **kwargs):
        config = configparser.ConfigParser()
        config.read('D:/inventory_flask_app/test/Desktop/pricing_scraper/AmazonPriceWatch/credentials.ini')
        # self.LOGIN_EMAIL = config[self.active_config]['email']
        # self.LOGIN_PASSWORD = config[self.active_config]['password']
        self.LOGIN_EMAIL = "midasdev711@gmail.com"
        self.LOGIN_PASSWORD = "boy wonder"
        self.LOGGED_IN = False
        self.collection = []
        with open(self.input_file, newline = '') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames = self.fieldnames, dialect = 'excel-tab')
            for row in reader:
                self.collection.append(row)

    def closed(self, reason):
        with open(self.input_file, 'w', newline = '') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames, dialect = 'excel-tab')
            for row in self.collection:
                if row['ID'] in self.changed_product_ids:
                    writer.writerow(row)

    def start_requests(self):
        yield scrapy.Request(
            url = self.start_urls[0],
            callback = self.goto_homepage,
            meta = {'dont_cache': True}
        )

    def goto_homepage(self, response):
        login_form_page_url = response.xpath('//a[contains(@href, "sign")]/@href').extract_first()
        yield scrapy.Request(
            url = login_form_page_url,
            callback = self.fill_login_form,
            meta = {'dont_cache': True}
        )

    def fill_login_form(self, response):
        print('#########################')
        print('USER: ' + self.LOGIN_EMAIL)
        print('#########################')

        yield scrapy.FormRequest.from_response(
            response,
            formname = 'signIn',
            formdata = {'email': self.LOGIN_EMAIL, 'password': self.LOGIN_PASSWORD},
            callback = self.after_login
        )

    def after_login(self, response):
        print('#########################')
        print('after_login')
        print('#########################')

        # check login succeed before going on
        if b"authentication failed" in response.body:
            self.logger.error("Login failed")
        else:
            self.LOGGED_IN = True
            self.logger.info("Login successful")
            # Empty cart before adding any products
            # go to cart again to empty
            yield scrapy.Request(
                self.cart_page_url,
                dont_filter = True,
                callback = self.empty_cart
            )

    def get_next_product(self):
        print('#########################')
        print('get_next_product')
        print('#########################')

        product_id = None
        product_url = None
        for product in self.collection:
            if 'URL' in product and product['URL']:
                url_data = urlparse(product['URL'])
                if url_data.hostname == 'www.amazon.com':
                    product_id = str(product['ID'])
                    product_url = product['URL']
                    if not product_id in self.products_passed:
                        break
        if product_id and not product_id in self.products_passed:
            return {'product_id': product_id, 'product_url': product_url}
        else:
            return None

    def product_page(self, response):
        print('#########################')
        print('product_page')
        print('#########################')

        product_id = response.meta.get('product_id')
        if response.xpath('//input[@name="submit.add-to-cart"]'):
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
            self.products_passed.append(product_id)
            self.logger.info("This product is not available!")
            # empty cart for the next iteration
            yield scrapy.Request(
                self.cart_page_url,
                dont_filter = True,
                callback = self.empty_cart
            )

    def added_to_cart(self, response):
        print('#########################')
        print('added_to_card')
        print('#########################')

        product_id = response.meta.get('product_id')
        # go to cart
        yield scrapy.Request(
            self.cart_page_url,
            meta = {'product_id': product_id},
            dont_filter = True,
            callback = self.cart_page
        )

    def cart_page(self, response):
        print('#########################')
        print('cart_page')
        print('#########################')

        product_id = response.meta.get('product_id')
        yield scrapy.FormRequest.from_response(
            response,
            formid = 'gutterCartViewForm',
            meta = {'product_id': product_id},
            dont_filter = True,
            callback = self.checkout_page
        )

    def checkout_page(self, response):
        print('#########################')
        print('checkout_page')
        print('#########################')

        product_id = response.meta.get('product_id')
        h1_text = response.xpath('//h1/text()').extract_first().strip()
        print('@@@@@@@@@@@@@@@@@@@@@')
        print(h1_text)
        print('@@@@@@@@@@@@@@@@@@@@@')
        if h1_text == 'Sign in':
            yield scrapy.FormRequest.from_response(
                response,
                formname = 'signIn',
                formdata = {'email': self.LOGIN_EMAIL, 'password': self.LOGIN_PASSWORD},
                meta = {'product_id': product_id},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Select a shipping address':
            frac_url = response.xpath('//div[@id="address-book-entry-0"]/div[contains(@class, "ship-to-this-address")]//a/@href').extract_first()
            url = self.first_part + frac_url
            yield scrapy.Request(
                url,
                meta = {'product_id': product_id},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Choose your shipping options':
            yield scrapy.FormRequest.from_response(
                response,
                formid = 'shippingOptionFormId',
                meta = {'product_id': product_id},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Select a payment method':
            yield scrapy.FormRequest.from_response(
                response,
                formnumber = 0,
                clickdata = {'id': 'continue-top'},
                meta = {'product_id': product_id},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Your Amazon Prime Free Preview has ended':
            url = response.xpath('//a[contains(@class, "prime-nothanks-button")]/@href').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                meta = {'product_id': product_id},
                dont_filter = True,
                callback = self.checkout_page
            )
        else:
            title_text = response.xpath('//title/text()').extract_first().strip()
            print('@@@@@@@@@@@@@@@@@@@@@')
            print(title_text)
            print('@@@@@@@@@@@@@@@@@@@@@')
            if title_text == 'Preparing your order':
                div_sel = response.xpath('//div[@id="subtotals-marketplace-table"]')
                price_str = div_sel.xpath('.//td[contains(@class, "grand-total-price")]/strong/text()').extract_first()
                if price_str:
                    price = float(price_str.replace('USD', '').strip())
                    for i in range(0, len(self.collection)):
                        if self.collection[i]['ID'] == product_id and self.collection[i]['Price'] != price:
                            self.collection[i]['Price'] = price
                            self.changed_product_ids.append(product_id)
                            break
                    self.products_passed.append(product_id)
                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                    print(product_id)
                    print(price)
                    print(self.products_passed)
                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            else:
                self.logger.error("Checkout failed")
            # go to cart again to empty
            yield scrapy.Request(
                self.cart_page_url,
                dont_filter = True,
                callback = self.empty_cart
            )

    def empty_cart(self, response):
        print('#########################')
        print('empty_card')
        print('#########################')

        del_sel = response.xpath('//form[@id="activeCartViewForm"]//input[@type="submit"][@value="Delete"]/@name')
        if del_sel:
            del_name = del_sel.extract_first()
            yield scrapy.FormRequest.from_response(
                response,
                formid = 'activeCartViewForm',
                clickdata = {'name': del_name},
                callback = self.empty_cart
            )
        else:
            self.logger.info("Cart is empty")
            next_product = self.get_next_product()
            if isinstance(next_product, dict):
                yield scrapy.Request(
                    url = next_product['product_url'],
                    meta = {'product_id': next_product['product_id']},
                    dont_filter = True,
                    callback = self.product_page
                )
            else:
                self.logger.info("No more products")
                return None

