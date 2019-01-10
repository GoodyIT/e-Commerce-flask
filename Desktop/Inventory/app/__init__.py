from flask import Flask
from .config import Config
from pymongo import MongoClient
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
client = MongoClient('mongodb://localhost:27017/')
db = client.test_inv

from app import routes
