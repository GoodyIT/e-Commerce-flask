from app.api import db
from uuid import uuid4 as uid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time

Users = db.Users

def getUser(username):
    return db.Users.find_one({'id':username})

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
    def get_first(self):
        user = getUser(self.username)
        if user is not None:
            return user['first']
        return None

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
    # validations
    @staticmethod
    def validate_username(name):
        ''' validates if a user exists '''
        user = db.Users.find_one({'id':name})
        if user is not None:
            return False
        return True
    @staticmethod
    def validate_email(name):
        ''' validates if a email exists '''
        email = db.Users.find_one({'id':name})
        if email is not None:
            return False
        return True
    @staticmethod
    def validate_admin(name):
        ''' validates if a user exists '''
        user = db.Users.find_one({'id':name})
        if user is not None:
            if user['admin'] == True:
                return True
        return False
    @staticmethod
    def createUser(new_user):
        '''
        Creates a new user
        new_user: info of user (array)
        '''
        # checks for player
        if self.validate_username(newuser['username']):
            return False
        User.insert_one(new_user)
        return True
