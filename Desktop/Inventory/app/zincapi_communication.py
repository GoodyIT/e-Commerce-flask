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
              #'request_failed': 'http://mywebsite.com/zinc/requrest_failed',
              #'request_succeeded': 'http://mywebsite.com/zinc/request_succeeded',
              #'tracking_obtained': 'http://mywebsite.com/zinc/tracking_obtained',
              'status_updated': "http://79.100.23.126:5000/shipping/status_updated"
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


def shipping_status_by_request_id(request_id):
    response = requests.get('https://api.zinc.io/v1/orders/{}'.format(request_id), auth=('', '')) # put token as a first argument in auth
    if response.status_code != 200:
        return SHIPPING_REQUEST_FAILED

    response_dict = json.loads(response.text)

    pprint.pprint(response_dict)

    if 'code' in response_dict and response_dict['code'] == 'request_processing':
        return SHIPPING_AWAITING

    elif '_type' in response_dict and response_dict['_type'] == 'error':
        # Request done processing.
        # Could contain "message": "Request is currently processing and will complete soon."
        # or not only. For now return awaiting in this case.
        return SHIPPING_AWAITING

    elif '_type' in response_dict and response_dict['_type'] == 'order_response':
        # check response_dict for details
        pass

    else:
        # check response_dict for details
        pass



if __name__ == '__main__':
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    db = client.test_inv
    orders = db.Orders.find()
    #request_id = '0e4e89ef12f157f7e3a14cad954a1fae'
    request_id = post_shipping_request(orders[0])
    status = shipping_status_by_request_id(request_id)
    print(status)
