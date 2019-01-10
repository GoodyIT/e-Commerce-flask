from app import db, login
from uuid import uuid4 as uid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time

Users = db.Users

class User:
    def __init__(self, username):
        self.username = username

    # login manager
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.username

    # set uid
    @staticmethod
    def setUID():
        temp = uid()
        return temp.__str__()

    # password hash
    @staticmethod
    def setHash(pw):
        return generate_password_hash(pw)
    @staticmethod
    def checkPassword(hash, pw):
        return check_password_hash(hash, pw)
