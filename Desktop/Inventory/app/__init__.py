from flask import Flask, redirect, url_for, request
from flask_login import LoginManager
from .config import Config

from app.api.routes import api, db
from app.admin.routes import admin_bp
from app.api.data import User
from app.admin.data import User

import os

def create_app(debug=False):
    app = Flask(__name__, static_url_path='/static')
    app.debug = debug
    app.config['SECRET_KEY'] = '0E919ADBAFC5BA1043670BA71996B983'

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.url_map.strict_slashes = False

    # login
    login = LoginManager(app)
    login.login_view = 'api.store_login'
    login.init_app(app)

    @login.user_loader
    def load_user(username):

        current_user = None
        if request.blueprint == 'admin':
            admin = db.Users.find_one({'id':username})
            if admin and admin['admin'] == True:
                current_user = User(admin['id'])
        elif request.blueprint == 'api':
            user = db.Users.find_one({'id':username})
            if user:
                current_user = User(user['id'])
        return current_user

    # Unauthorized Handler
    @login.unauthorized_handler
    def unauth_handler():
        # if request url is api, redirect to api.login
        if request.blueprint == 'api':
            return redirect(url_for('api.store_login'))
        # if request url is admin, redirect to admin.login
        elif request.blueprint == 'admin':
            return redirect(url_for('admin.login'))

    # API Blueprint
    app.register_blueprint(api)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
