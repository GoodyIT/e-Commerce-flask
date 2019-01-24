import json

from pymongo import MongoClient
from werkzeug.wrappers import Request

#from app import db
from .zincapi_communication import post_shipping_request, post_cancellation_request

class ZincapiMiddleware(object):

    def __init__(self, wsgi_app, app):
        self.app = wsgi_app
        self._flask_app = app

    def __call__(self, environ, start_response):
        print('--------------------------')
        print('Function called, HTTP_HOST = ', environ['HTTP_HOST'])
        print('--------------------------')
        import pprint
        if '/orders' == environ['PATH_INFO'] and 'POST' == environ['REQUEST_METHOD']:
            #print('type(environ) ------------------- >', type(environ))
            request = Request(environ)

            client = MongoClient('mongodb://localhost:27017/')
            db = client.test_inv

            order_id = json.loads(request.data.decode("utf-8"))['id']
            new_order = db.Queue.find_one({'order_id':order_id})
            request_id = post_shipping_request(new_order['item_id'], new_order['quantity'])

            new_order['shipped'] = 'awaiting'
            if request_id:
                new_order['request_id'] = request_id

            db.Queue.remove({'order_id':item['id']})
            db.Orders.insert_one(new_order)

            #print('========================================')
            #print('request_id ==> ', '\n', request_id)
            #print('========================================')

        # elif is shpping on load (listen ajax call)
             # get all orders and call shipping status

        return self.app(environ, start_response)

