# -*- coding: utf-8 -*-
import time
from urllib.parse import urlparse

import scrapy, csv, pprint, re, json, configparser



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
    SHIPPING_OPT_1 = 'Cheapest'
    SHIPPING_OPT_2 = 'Fastest'
    shipping_option = None
    shipping_name = None
    cart_page_url = 'https://www.amazon.com/gp/cart/view.html?ref_=nav_cart'
    products_passed = []
    fieldnames = [
        'ID',
        'Name',
        'Price',
        'Cheapest - Option',
        'Cheapest - Shipping Cost',
        'Cheapest - Taxes & Fees',
        'Cheapest ETA - Days',
        'Fastest - Option',
        'Fastest Option - Days',
        'Fastest - Shipping Cost',
        'Fastest - Taxes & Fees',
        'Group',
        'Category',
        'Vendor',
        'URL',
    ]
    fields_match = {
        'Estimated tax to be collected': '%s - Taxes & Fees',
        'Shipping & handling': '%s - Shipping Cost',
    }
    input_file = 'test_items.tsv'

    def __init__(self, category = None, *args, **kwargs):
        config = configparser.ConfigParser()
        config.read('D:/inventory_flask_app/test/Desktop/pricing_scraper/AmazonPriceWatch/credentials.ini')
        self.LOGIN_EMAIL = "midasdev711@gmail.com"
        self.LOGIN_PASSWORD = "boy wonder"
        self.LOGGED_IN = False
        self.collection = []
        with open(self.input_file, newline = '') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames = self.fieldnames, dialect = 'excel-tab')
            for row in reader:
                pprint.pprint(row)
                # Skip header row
                if row['ID'] != 'ID':
                    self.collection.append(row)

    def response_html_path(self, request):
        """
        Args:
            request (scrapy.http.request.Request): request that produced the
                response.
        """
        strtime = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime())
        return 'html/rado.nyc/{}.html'.format(strtime)

    def closed(self, reason):
        with open(self.input_file, 'w', newline = '') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = self.fieldnames, dialect = 'excel-tab')
            writer.writeheader()
            for row in self.collection:
                writer.writerow(row)

    def start_requests(self):
        yield scrapy.Request(
            url = self.start_urls[0],
            callback = self.goto_homepage,
            meta = {'dont_cache': True, 'save_html': True}
        )

    def goto_homepage(self, response):
        login_form_page_url = response.xpath('//a[contains(@href, "sign")]/@href').extract_first()
        yield scrapy.Request(
            url = login_form_page_url,
            callback = self.fill_login_form,
            meta = {'dont_cache': True, 'save_html': True}
        )

    def fill_login_form(self, response):
        print('#########################')
        print('USER: ' + self.LOGIN_EMAIL)
        print('#########################')
        yield scrapy.FormRequest.from_response(
            response,
            formname = 'signIn',
            formdata = {'email': self.LOGIN_EMAIL, 'password': self.LOGIN_PASSWORD},
            callback = self.after_login,
            meta = {'save_html': True}
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
                callback = self.empty_cart,
                meta = {'save_html': True}
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
                meta = {'product_id': product_id, 'save_html': True},
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
                callback = self.empty_cart,
                meta = {'save_html': True}
            )

    def added_to_cart(self, response):
        print('#########################')
        print('added_to_card')
        print('#########################')
        product_id = response.meta.get('product_id')
        self.shipping_option = self.SHIPPING_OPT_1
        # go to cart
        yield scrapy.Request(
            self.cart_page_url,
            meta = {'product_id': product_id, 'save_html': True},
            dont_filter = True,
            callback = self.cart_page,
        )

    def cart_page(self, response):
        print('#########################')
        print('cart_page')
        print('#########################')
        product_id = response.meta.get('product_id')
        yield scrapy.FormRequest.from_response(
            response,
            formid = 'gutterCartViewForm',
            meta = {'product_id': product_id, 'save_html': True},
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
                meta = {'product_id': product_id, 'save_html': True},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Select a shipping address':
            frac_url = response.xpath('//div[@id="address-book-entry-0"]/div[contains(@class, "ship-to-this-address")]//a/@href').extract_first()
            url = self.first_part + frac_url
            yield scrapy.Request(
                url,
                meta = {'product_id': product_id, 'save_html': True},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Choose your shipping options':
            radios_sel = response.xpath('//input[@name="order_0_ShippingSpeed"]')
            is_first = True
            for radio_sel in radios_sel:
                if is_first:
                    cheapest_radio_sel = radio_sel
                    is_first = False
                else:
                    fastest_radio_sel = radio_sel
            if self.shipping_option == self.SHIPPING_OPT_1:
                curr_radio_sel = fastest_radio_sel
            else:
                curr_radio_sel = cheapest_radio_sel
            value = curr_radio_sel.xpath('./@value').extract_first()
            self.shipping_name = self._get_shipping_name(curr_radio_sel)
            yield scrapy.FormRequest.from_response(
                response,
                formid = 'shippingOptionFormId',
                formdata = {'order_0_ShippingSpeed': value},
                meta = {'product_id': product_id, 'save_html': True},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Select a payment method':
            yield scrapy.FormRequest.from_response(
                response,
                formnumber = 0,
                clickdata = {'id': 'continue-top'},
                meta = {'product_id': product_id, 'save_html': True},
                dont_filter = True,
                callback = self.checkout_page
            )
        elif h1_text == 'Your Amazon Prime Free Preview has ended':
            url = response.xpath('//a[contains(@class, "prime-nothanks-button")]/@href').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(
                url,
                meta = {'product_id': product_id, 'save_html': True},
                dont_filter = True,
                callback = self.checkout_page
            )
        else:
            title_text = response.xpath('//title/text()').extract_first().strip()
            print('@@@@@@@@@@@@@@@@@@@@@')
            print(title_text)
            print('@@@@@@@@@@@@@@@@@@@@@')
            if title_text == 'Preparing your order':
                print('@@@@@@@@@@@@@@@')
                print(self.shipping_name)
                print('@@@@@@@@@@@@@@@')
                if self.shipping_option == self.SHIPPING_OPT_1:
                    self._get_prices(response)
                    self.shipping_option = self.SHIPPING_OPT_2
                    # go to cart
                    yield scrapy.Request(
                        self.cart_page_url,
                        meta = {'product_id': product_id, 'save_html': True},
                        dont_filter = True,
                        callback = self.cart_page
                    )
                else:
                    self._get_prices(response)
                    self.products_passed.append(product_id)
                    for i in range(0, len(self.collection)):
                        if self.collection[i]['ID'] == product_id:
                            break
                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                    print(product_id)
                    print(self.collection[i])
                    print(self.products_passed)
                    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                    # go to cart again to empty
                    yield scrapy.Request(
                        self.cart_page_url,
                        dont_filter = True,
                        callback = self.empty_cart,
                        meta = {'save_html': True}
                    )
            elif title_text == 'Complete your Amazon Prime sign up':
                yield scrapy.FormRequest.from_response(
                    response,
                    formname = 'optout2',
                    clickdata = {'name': 'action.checkoutAcceptOffer'},
                    meta = {'product_id': product_id, 'save_html': True},
                    dont_filter = True,
                    callback = self.checkout_page
                )
            else:
                if response.xpath('//form[@id="address-list"]'):
                    print('@@@@@@@@@@@@@@@@@@@@@')
                    print('Choose a shipping address (Prime)')
                    print('@@@@@@@@@@@@@@@@@@@@@')
                    yield scrapy.FormRequest.from_response(
                        response,
                        formid = 'address-list',
                        clickdata = {'data-testid': 'Address_selectShipToThisAddress'},
                        meta = {'product_id': product_id, 'save_html': True},
                        dont_filter = True,
                        callback = self.checkout_page
                    )
                elif response.xpath('//input[@aria-labelledby="useThisPaymentMethodButtonId-announce"]'):
                    print('@@@@@@@@@@@@@@@@@@@@@')
                    print('Choose a payment method (Prime)')
                    print('@@@@@@@@@@@@@@@@@@@@@')
                    yield scrapy.FormRequest.from_response(
                        response,
                        formnumber = 2,
                        clickdata = {'ria-labelledby': 'useThisPaymentMethodButtonId-announce'},
                        meta = {'product_id': product_id, 'save_html': True},
                        dont_filter = True,
                        callback = self.checkout_page
                    )
                else:
                    print('@@@@@@@@@@@@@@@@@@@@@')
                    print('Choose a shipping option (Prime)')
                    print('@@@@@@@@@@@@@@@@@@@@@')
                    self.logger.error("Checkout failed")
                    # go to cart again to empty
                    yield scrapy.Request(
                        self.cart_page_url,
                        dont_filter = True,
                        callback = self.empty_cart,
                        meta = {'save_html': True}
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
                callback = self.empty_cart,
                meta = {'save_html': True}
            )
        else:
            self.logger.info("Cart is empty")
            next_product = self.get_next_product()
            if isinstance(next_product, dict):
                yield scrapy.Request(
                    url = next_product['product_url'],
                    meta = {'product_id': next_product['product_id'], 'save_html': True},
                    dont_filter = True,
                    callback = self.product_page
                )
            else:
                self.logger.info("No more products")
                return None

    def _get_shipping_name(self, radio_sel):
        name = radio_sel.xpath('./../following-sibling::div[contains(@class, "description")]/text()').extract_first()
        name = name.strip()
        name = re.sub('\$[0-9\.]+', '', name)
        return name.strip()

    def _get_prices(self, response):
        product_id = response.meta.get('product_id')
        # get list index
        for i in range(0, len(self.collection)):
            if self.collection[i]['ID'] == product_id:
                break
        key = '%s - Option' % self.shipping_option
        self.collection[i][key] = self.shipping_name
        div_sel = response.xpath('//div[@id="subtotals-marketplace-table"]')
        rows_sel = div_sel.xpath('./table//tr[contains(@class, "order-summary-unidenfitied-style")]')
        for row_sel in rows_sel:
            label = row_sel.xpath('./td[contains(@class, "a-text-left")]/text()').extract_first().strip('*:')
            price = self._price_to_float(row_sel.xpath('./td[contains(@class, "a-text-right")]/text()').extract_first())
            if label == 'Items':
                self.collection[i]['Price'] = price
            elif label in self.fields_match:
                key = self.fields_match[label] % self.shipping_option
                self.collection[i][key] = price
        # Days
        keys = ['Cheapest ETA - Days', 'Fastest Option - Days']
        for key in keys:
            self.collection[i][key] = 'n/a'

    def _price_to_float(self, price_str):
        if price_str:
            return float(price_str.replace('USD', '').strip())
        else:
            return None
