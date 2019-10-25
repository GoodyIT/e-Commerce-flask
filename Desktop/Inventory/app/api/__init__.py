from flask import Flask, Blueprint
from pymongo import MongoClient
from flask_login import LoginManager

api = Blueprint('api', __name__, template_folder='templates')

client = MongoClient('mongodb://localhost:27017/')
db = client.test_inv

from . import routes
