# -*- coding: utf-8 -*-
from flask import Flask, redirect, request, jsonify, make_response, json, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
from flask_mail import Mail
import os
import jwt
from cryptography.fernet import Fernet
import logging
import datetime as time
from retinasdk import FullClient
from flask_cors import CORS
from flask_compress import Compress
from werkzeug.wrappers import BaseRequest
from werkzeug.exceptions import HTTPException, NotFound
from flask_socketio import SocketIO, join_room, leave_room
from flask_jwt_extended import JWTManager
from geopy.geocoders import Nominatim
import flask_whooshalchemy as wa
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

key_c = "mRo48tU4ebP6jIshqaoNf2HAnesrCGHm"
key_cr = b'vgF_Yo8-IutJs-AcwWPnuNBgRSgncuVo1yfc9uqSiiU='
key_jwt = {
    "kty": "oct",
    "use": "enc",
    "kid": "1",
    "k": "mRo48tU4ebP6jIshqaoNf2HAnesrCGHm",
    "alg": "HS256"
}

app = Flask(__name__, static_url_path='/static')

#CORS(app)
serializer = URLSafeTimedSerializer(key_c)
JWTManager(app)

app.secret_key = key_c
app.config['SESSION_TYPE'] = 'redis'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///newapp?client_encoding=utf8"
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
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['UPLOAD_FOLDER_PROFILE'] = app.root_path + '/static/profile_pics'
app.config['UPLOAD_FOLDER_PROFILE_COVER'] = app.root_path + '/static/profile_cover'
app.config['UPLOAD_FOLDER_POST'] = app.root_path + '/static/thumbnail_post'
app.config['UPLOAD_FOLDER_IMAGES'] = app.root_path + '/static/images/posts'
app.config['UPLOAD_FOLDER_PODCAST_SERIES'] = app.root_path + '/static/images/podcast_series'
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

config = app.config


Compress(app)
db = SQLAlchemy(app)
mail = Mail(app)
db_engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'), echo=False, client_encoding='utf8')
db.configure_mappers()
db.create_all()
bcrypt = Bcrypt(app)
socket = SocketIO(app, manage_session=False, cors_allowed_origins='*', async_mode='eventlet')
geolocator = Nominatim(user_agent="NewApp")

translate = FullClient("7eaa96e0-be79-11e9-8f72-af685da1b20e", apiServer="http://api.cortical.io/rest",
                       retinaName="en_associative")

cipher_suite = Fernet(key_cr)

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


from models import PostModel

wa.whoosh_index(app,PostModel)

from pages.home.home import home
from pages.users.auth import auth
from pages.users.users import users
from pages.follow.follow import follow
from pages.users.notifications import notifications
from pages.users.direct import direct
from pages.post.post import post
from pages.post.replies import replies

app.register_blueprint(home)
app.register_blueprint(post)
app.register_blueprint(replies)
app.register_blueprint(users)
app.register_blueprint(notifications)
app.register_blueprint(direct)
app.register_blueprint(auth)
app.register_blueprint(follow)

@app.route("/api/v2")
def getApi():
    routes = {}
    for rule in app.url_map.iter_rules():
        routes[rule.endpoint] = re.sub('<[^>]+>',"",'%s' % rule)     
    return make_response(jsonify(routes), 200)

gunicorn_error_logger = logging.getLogger('gunicorn.info')

app.logger.setLevel(logging.INFO)
app.logger.info('NewApp Launched successfully')
app.logger.info('Security keys')
app.logger.info('Session keys')
app.logger.info(key_c)
app.logger.info('Cryptography key')
app.logger.info(key_cr)
app.logger.info('JWT Key')
app.logger.info(key_jwt['k'])
app.logger.info('JWT Algorithm')
app.logger.info(key_jwt['alg'])

""" logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) """

if __name__ == "__main__":
    socket.run(app, host='0.0.0.0', port=5000);
    #app.run(host="192.168.1.4")
