import requests
import pprint
import json


# maybe we have two types of failing - the request to zincapi could fail
# and the shipping request in the retailer could fail.
(SHIPPING_REQUEST_FAILED, SHIPPING_AWAITING,
 SHIPPING_SHIPPED, SHIPPING_DELIVERED) = ('failed', 'awaiting', 'shipped', 'delivered')


def post_shipping_request(order):
    data = {
        'billing_address': {'address_line1': '84 Massachusetts Ave',
                     'address_line2': '',
                     'city': 'Cambridge',
                     'country': 'US',
                     'first_name': 'William',
                     'last_name': 'Rogers',
                     'phone_number': '5551234567',
                     'state': 'MA',
                     'zip_code': '02139'},
 #'client_notes': {'any_other_field': ['any value'],
                  #'our_internal_order_id': 'abc123'},
 #'gift_message': 'Here is your package, Tim! Enjoy!',
 #'is_gift': True,
 'max_price': 0,
 'payment_method': {'expiration_month': 1,
                    'expiration_year': 2020,
                    'name_on_card': 'Ben Bitdiddle',
                    'number': '5555555555554444',
                    'security_code': '123',
                    'use_gift': False},
 'products': [{'product_id': order["item_id"], 'quantity': order["quantity"]}],
 'retailer': 'amazon',

 # put credentials here before running it
 'retailer_credentials': {'email': '',
                          'password': '',


                          #'verification_code': '942240',
                          #'totp_2fa_key': '3DE4 3ERE 23WE WIKJ GRSQ VOBG CO3D '
                                          #'METM 2NO2 OGUX Z7U4 DP2H UYMA'
                                          },
 'shipping': {'max_days': 5, 'max_price': 0, 'order_by': 'price'},
 'shipping_address': {'address_line1': '77 Massachusetts Avenue',
                      'address_line2': '',
                      'city': 'Cambridge',
                      'country': 'US',
                      'first_name': 'Tim',
                      'last_name': 'Beaver',
                      'phone_number': '5551230101',
                      'state': 'MA',
                      'zip_code': '02139'},
 'webhooks': {
              #'request_failed': "http://188.254.244.234:9000/shipping/status_updated",
              #'request_succeeded': "http://188.254.244.234:9000/shipping/status_updated",
              'tracking_obtained': 'http://188.254.244.234:9000/shipping/tracking_obtained', # replace with your IP
              'status_updated': "http://188.254.244.234:9000/shipping/status_updated" # replace with your IP
              }

}

    data = json.dumps(data)

    response = requests.post('https://api.zinc.io/v1/orders', data=data, auth=('', '')) # put token as a first argument in auth
    if response.status_code != 200:
        return False

    response_dict = json.loads(response.text)
    if response.status_code == 200 and 'error' not in response_dict:
        return response_dict['request_id']

    return False
