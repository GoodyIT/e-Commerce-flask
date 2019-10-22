from pymongo import MongoClient
from flask import Blueprint
from flask_login import current_user

admin_bp = Blueprint('admin', __name__, template_folder='templates')

client = MongoClient('mongodb://localhost:27017/')
db = client.test_inv

from . import routes
