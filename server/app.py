# -*- coding: utf-8 -*-
from flask import Flask, jsonify, make_response, json
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadTimeSignature, SignatureExpired
from flask_mail import Mail
import os
import jwt
from cryptography.fernet import Fernet
import logging
import datetime as time
from retinasdk import FullClient
from flask_compress import Compress
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from geopy.geocoders import Nominatim
import flask_whooshalchemy as wa
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import re

app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///newappv2?client_encoding=utf8"
#danutu:468255@localhost
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
app.config['MAIL_SERVER'] = 'smtp.zoho.eu'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contact@newapp.nl'
app.config['MAIL_PASSWORD'] = 'FCsteaua89'
app.config['JWT_ALGORITHM'] = "HS256"
app.config['JWT_KEY'] = "mRo48tU4ebP6jIshqaoNf2HAnesrCGHm"
app.config['CIPHER_KEY'] = "vgF_Yo8-IutJs-AcwWPnuNBgRSgncuVo1yfc9uqSiiU="
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['UPLOAD_FOLDER_PROFILE'] = app.root_path + '/static/users/'
app.config['UPLOAD_FOLDER_POST'] = app.root_path + '/static/posts/thumbnail_post'
app.config['UPLOAD_FOLDER_IMAGES'] = app.root_path + '/static/posts/images'
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
app.config['ROOT_PATH'] = app.root_path

config = app.config

app.secret_key = config.get('JWT_KEY')

Compress(app)
JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
bcrypt = Bcrypt(app)
socket = SocketIO(app, manage_session=False, async_mode='eventlet')
geolocator = Nominatim(user_agent="NewApp")
translate = FullClient("7eaa96e0-be79-11e9-8f72-af685da1b20e", apiServer="http://api.cortical.io/rest",
                       retinaName="en_associative")
ma = Marshmallow(app)
cipher_suite = Fernet(config.get('CIPHER_KEY'))
serializer = URLSafeTimedSerializer(config.get('JWT_KEY'))

import sockets

@app.errorhandler(404)
def server_error(error):
    return make_response(jsonify({'error': 404}), 404)

@app.errorhandler(400)
def server_error(error):
    return make_response(jsonify({'error': 400}), 400)


@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 500}), 500)


from pages.home.home import home
from pages.users.auth import auth
from pages.users.users import users
from pages.follow.follow import follow
from pages.users.notifications import notifications
from pages.users.direct import direct
from pages.post.post import post
from pages.post.replies import replies
from pages.analytics.analytics import analytics

app.register_blueprint(home)
app.register_blueprint(post)
app.register_blueprint(replies)
app.register_blueprint(users)
app.register_blueprint(notifications)
app.register_blueprint(direct)
app.register_blueprint(auth)
app.register_blueprint(follow)
app.register_blueprint(analytics)

@app.route("/api/v2")
def getApi():
    routes = {}
    for rule in app.url_map.iter_rules():
        routes[rule.endpoint] = re.sub('<[^>]+>',"",'%s' % rule)     
    return make_response(jsonify(routes), 200)

gunicorn_error_logger = logging.getLogger('gunicorn.info')

app.logger.setLevel(logging.INFO)

if __name__ == "__main__":
    socket.run(app, threading=True,host='0.0.0.0',port=8000);
    #app.run(app, host='0.0.0.0', port=8000, debug=True)
