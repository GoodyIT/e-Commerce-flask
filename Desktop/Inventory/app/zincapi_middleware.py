import json

from pymongo import MongoClient
from werkzeug.wrappers import Request

from .zincapi_communication import post_shipping_request, post_cancellation_request, shipping_status_by_request_id

class ZincapiMiddleware(object):

    def __init__(self, wsgi_app, app):
        self.app = wsgi_app
        self._flask_app = app

    def __call__(self, environ, start_response):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.test_inv
        request = Request(environ)

        if request.url == "http://{0}/shipping/status_updated".format('188.254.244.234:9000'): # put your ip:port

            print('IN STATUS UPDATED HOOK')

            status_dict = json.loads(request.data.decode("utf-8"))

            status = None
            merchant_order_id = None
            if 'code' in status_dict and status_dict['code'] == 'request_processing':
                status = 'awaiting'

            elif '_type' in status_dict and status_dict['_type'] == 'error':
                # Request done processing.
                # We can do more precise checks on the status dict.
                # For now return awaiting in this case.
                status = 'awaiting'

            elif '_type' in status_dict and status_dict['_type'] == 'order_response':
                # here we know that the order was successfully placed
                status = 'shipped'
                merchant_order_id = status_dict['merchant_order_ids'][0]['merchant_order_id']
            if status is not None:
                db.Orders.update_one({'request_id': status_dict['request_id']}, {'$set': {'shipped': status}})
            if merchant_order_id is not None:
                db.Orders.update_one({'request_id': status_dict['request_id']}, {'$set': {'merchant_order_id': merchant_order_id}})

            print('==========================================')
            print('SHIPPING STATUS ==> ', status)
            print('MERCHANT ORDER ID ==> ', merchant_order_id)
            print('==========================================')

        elif request.url == 'http://{0}/shipping/tracking_obtained'.format('188.254.244.234:9000'): # put your ip:port
            status_dict = json.loads(request.data.decode("utf-8"))

            print('IN TRACKING OBTAINED HOOK')

            try:
                delivery_status = status_dict['tracking'][0]['delivery_status']
            except:
                delivery_status = None

            print('DELIVERY STATUS ==> ', delivery_status)

            if delivery_status == 'Delivered':
                db.Orders.update_one({'request_id': status_dict['request_id']}, {'$set': {'shipped': 'delivered'}})

        elif '/orders' == environ['PATH_INFO'] and 'POST' == environ['REQUEST_METHOD']:

            order_id = json.loads(request.data.decode("utf-8"))['id']
            new_order = db.Queue.find_one({'order_id': order_id})
            request_id = post_shipping_request(new_order['order_id'], new_order['quantity'])

            new_order['shipped'] = 'awaiting'
            if request_id:
                new_order['request_id'] = request_id

            db.Queue.remove({'order_id': order_id})
            db.Orders.insert_one(new_order)

            print('========================================')
            print('POST SHIPPING REQUEST')
            print('========================================')

        elif request.url == 'https://{0}/shipping/cancellation_order/succeed'.format('188.254.244.234:9000'): # put your ip:port
            # Order is cancelled successfully
            pass

        elif request.url == "https://{0}/shipping/cancellation_order/failed".format('188.254.244.234:9000'): # put your ip:port
            # Order cansellation faild for some reason
            pass

        #elif '/shipping' == environ['PATH_INFO'] and 'GET' == environ['REQUEST_METHOD']:
            #orders = db.Orders.find()
            #for order in orders:
                #shipped_status = 'awaiting'

                #try:
                    #request_id = order['request_id']
                #except KeyError:
                    ##request_id = post_shipping_request(order['order_id'], order['quantity'])
                    #pass
                #else:
                    #shipped_status = shipping_status_by_request_id(request_id)

                #db.Orders.update_one({'_id': order['_id']}, {'$set': {'shipped': shipped_status}})

        return self.app(environ, start_response)

