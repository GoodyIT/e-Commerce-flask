import json
from pymongo import MongoClient
from werkzeug.wrappers import Request
from .zincapi_communication import post_shipping_request, post_cancellation_request, shipping_status_by_request_id

class ZincapiMiddleware(object):

    def __init__(self, wsgi_app, socketio):
        self.app = wsgi_app
        self.socketio = socketio

    def __call__(self, environ, start_response):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.test_inv
        request = Request(environ)

        print('request.url = ', request.url)

        if 'shipping/status_updated' in request.url:

            print('IN STATUS UPDATED HOOK')

            status_dict = json.loads(request.data.decode("utf-8"))

            #print('----------------------------', '\n', status_dict, '\n', '----------------------------')

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
                item_id = status_dict['request']['products'][0]['product_id']
                db.Orders.update_one({'item_id': item_id}, {'$set': {'shipped': status}})
            if merchant_order_id is not None:
                item_id = status_dict['request']['products'][0]['product_id']
                db.Orders.update_one({'item_id': item_id}, {'$set': {'merchant_order_id': merchant_order_id}})

            print('==========================================')
            print('SHIPPING STATUS ==> ', status)
            print('MERCHANT ORDER ID ==> ', merchant_order_id)
            print('==========================================')

            self.socketio.emit('my event', {'message': 'got it!'}, namespace='/test')


        elif 'shipping/tracking_obtained' in request.url:
            status_dict = json.loads(request.data.decode("utf-8"))

            print('IN TRACKING OBTAINED HOOK')

            try:
                delivery_status = status_dict['tracking'][0]['delivery_status']
            except:
                delivery_status = None

            print('DELIVERY STATUS ==> ', delivery_status)

            if delivery_status == 'Delivered':
                merchant_order_id = status_dict['tracking'][0]['merchant_order_id']
                db.Orders.update_one({'merchant_order_id': merchant_order_id}, {'$set': {'shipped': 'delivered'}})

        elif '/orders' == environ['PATH_INFO'] and 'POST' == environ['REQUEST_METHOD']:

            order_id = json.loads(request.data.decode("utf-8"))['id']
            new_order = db.Queue.find_one({'order_id': order_id})
            request_id = post_shipping_request(new_order['item_id'], new_order['quantity'])

            print('request_id = ', request_id)

            new_order['shipped'] = 'awaiting'
            if request_id:
                new_order['request_id'] = request_id

            db.Queue.remove({'order_id': order_id})
            db.Orders.insert_one(new_order)

            print('========================================')
            print('POST SHIPPING REQUEST')
            print('========================================')

        elif '/products' == environ['PATH_INFO'] and 'POST' == environ['REQUEST_METHOD']:
            order_id = json.loads(request.data.decode("utf-8"))['id']

            order = db.Orders.find_one({'order_id':order_id})
            post_cancellation_request(order['merchant_order_id'], order['request_id'])

        elif '/shipping/cancellation_order/succeed' in request.url:
            status_dict = json.loads(request.data.decode("utf-8"))
            merchant_order_id = status_dict['merchant_order_id']
            db.Orders.update({'merchant_order_id': merchant_order_id}, {'$set': {'shipped': 'cancelled'}})

        elif 'cancellation_order/failed' in request.url:
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


        def my_start_response(status, headers, exc_info=None):
            # status = '200 OK'
            return start_response(status, headers, exc_info)

        return self.app(environ, my_start_response)

