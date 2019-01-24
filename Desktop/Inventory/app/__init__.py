from flask import Flask
from pymongo import MongoClient
from flask_login import LoginManager

from .config import Config
from .zincapi_middleware import ZincapiMiddleware

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
client = MongoClient('mongodb://localhost:27017/')
db = client.test_inv

app.wsgi_app = ZincapiMiddleware(app.wsgi_app, app)

from app import routes
