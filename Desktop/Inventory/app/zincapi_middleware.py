from werkzeug.wrappers import Request

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

            print('type(environ) ------------------- >', type(environ))

            request = Request(environ)

            pprint.pprint(self._flask_app.request.json)
            pass

        #item = request.json
        #print('-------- item --------- ', item)


        return self.app(environ, start_response)

