import requests
import pprint
import json

(SHIPPING_REQUEST_FAILED, SHIPPING_AWAITING, SHIPPING_SHIPPED, SHIPPING_DELIVERED) = range(4)


def post_shipping_request(order):
    data = {
       "retailer": "amazon",
       "products": [{
           "product_id": order["item_id"],
           "quantity": order["quantity"],
       }],
       "shipping_address": { # we need new db etry
         "first_name": "Tim",
         "last_name": "Beaver",
         "address_line1": "77 Massachusetts Avenue",
         "address_line2": "",
         "zip_code": "02139",
         "city": "Cambridge",
         "state": "MA",
         "country": "US",
         "phone_number": "5551230101"
       },
       "shipping_method": "cheapest",
       "payment_method": { # we need new db etry
         "name_on_card": "Ben Bitdiddle",
         "number": "5555555555554444",
         "security_code": "123",
         "expiration_month": 1,
         "expiration_year": 2015,
       },
       "billing_address": { # we need new db etry
         "first_name": "William",
         "last_name": "Rogers",
         "address_line1": "84 Massachusetts Ave",
         "address_line2": "",
         "zip_code": "02139",
         "city": "Cambridge",
         "state": "MA",
         "country": "US",
         "phone_number": "5551234567"
       },
       "retailer_credentials": { # we need new db entry
         "email": "timbeaver@gmail.com",
         "password": "myRetailerPassword"
       },
    }

    data = json.dumps(data)

    response = requests.post('https://api.zinc.io/v1/orders', data=data, auth=('FD1414B3CEF415B7C40A9E0F', ''))
    if response.status_code != 200:
        return SHIPPING_REQUEST_FAILED

    response_dict = json.loads(response.text)
    if response.status_code == 200 and 'error' not in response_dict:
        return response_dict['request_id']
    return None


def shipping_status_by_request_id(request_id):
    response = requests.get('https://api.zinc.io/v1/orders/{}'.format(request_id), auth=('FD1414B3CEF415B7C40A9E0F', ''))
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
    request_id = post_shipping_request(orders[0])
    status = shipping_status_by_request_id(request_id)
    print(request_id, status)
