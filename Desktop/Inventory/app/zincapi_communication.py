import requests
import json
import configparser


config = configparser.ConfigParser()
config.read('shipping.ini')
_IP_PORT = config['GENERAL']['ip_port']
_CLIENT_TOKEN = config['GENERAL']['client_token']
_AMAZON_EMAIL = config['AMAZON']['email']
_AMAZON_PASSWORD = config['AMAZON']['password']


# maybe we have two types of failing - the request to zincapi could fail
# and the shipping request in the retailer could fail.
(SHIPPING_REQUEST_FAILED, SHIPPING_AWAITING,
 SHIPPING_SHIPPED, SHIPPING_DELIVERED) = ('failed', 'awaiting', 'shipped', 'delivered')


def post_shipping_request(item_id, quantity):
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
 'products': [{'product_id': item_id, 'quantity': quantity}],
 'retailer': 'amazon',

 # put credentials here before running it
 'retailer_credentials': {'email': _AMAZON_EMAIL,
                          'password': _AMAZON_PASSWORD,


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
 #'webhooks': {
              ##'request_failed': "http://188.254.244.234:9000/shipping/status_updated",
              ##'request_succeeded': "http://188.254.244.234:9000/shipping/status_updated",
              #'tracking_obtained': 'http://{0}/shipping/tracking_obtained'.format(_IP_PORT),
              #'status_updated': "http://{0}/shipping/status_updated".format(_IP_PORT)
              #}

}

    data = json.dumps(data)

    response = requests.post('https://api.zinc.io/v1/orders', data=data, auth=(_CLIENT_TOKEN, ''))
    if response.status_code != 200:
        return False

    response_dict = json.loads(response.text)
    if response.status_code == 200 and 'error' not in response_dict:
        return response_dict['request_id']

    return False


def shipping_status_by_request_id(request_id):
    response = requests.get('https://api.zinc.io/v1/orders/{}'.format(request_id), auth=(_CLIENT_TOKEN, ''))
    if response.status_code != 200:
        return SHIPPING_REQUEST_FAILED

    response_dict = json.loads(response.text)

    #pprint.pprint(response_dict)

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


def post_cancellation_request(merchant_order_id, request_id):
    print('-------------- IN CANCELLATION REQUEST -----------------')
    headers = {
        'Content-type': 'application/json'
    }

    data = {
        "merchant_order_id": merchant_order_id,
        "webhooks": {
            "request_succeeded": "https://{0}/shipping/cancellation_order/succeed".format(_IP_PORT),
            "request_failed": "https://{0}/shipping/cancellation_order/failed".format(_IP_PORT)
        }
    }
    data = json.dumps(data)
    url = 'https://api.zinc.io/v1/orders/{0}/cancel'.format(request_id)
    response = requests.post(url, headers=headers, data=data, auth=(_CLIENT_TOKEN, ''))

