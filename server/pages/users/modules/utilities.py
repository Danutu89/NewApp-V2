from functools import wraps
from flask import request, make_response, jsonify
import jwt
from app import config
import datetime as dt
from sqlalchemy import desc, func, or_, asc
import re
import os
from PIL import Image
from webptools import webplib as webp

from models import UserModel, TagModel, PostModel

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def AuthRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.headers['Token']
            decoded = jwt.decode(token_header, config['JWT_KEY'])
            kwargs['token'] = decoded
        except Exception as e:
            make_response(jsonify({'auth': 'Invalid token.'}), 401)
        return f(*args, **kwargs)
    return decorated


def AuthOptional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.headers['Token']
            decoded = jwt.decode(token_header, config['JWT_KEY'])
            kwargs['token'] = decoded
            kwargs['auth'] = True
        except Exception as e:
            kwargs['auth'] = False
        return f(*args, **kwargs)
    return decorated

def SaveImage(userId, type):
    if type == 'profile':
        file_name, file_ext = os.path.splitext(request.files['avatarimg'].filename)
        users = UserModel.filter_by(id=userId).first()
        picture_fn = 'user_' + str(userId) + str(file_ext)
        picture_path = os.path.join(config['UPLOAD_FOLDER_PROFILE'], picture_fn)
    elif type == 'cover':
        file_name, file_ext = os.path.splitext(request.files['coverimg'].filename)
        users = UserModel.filter_by(id=userId).first()
        picture_fn = 'user_' + str(userId) + str(file_ext)
        picture_path = os.path.join(config['UPLOAD_FOLDER_PROFILE_COVER'], picture_fn)

    if type == 'profile':
        i = Image.open(request.files['avatarimg'])
        output_size = (500, 500)
        i.thumbnail(output_size)
    elif type == 'cover':
        i = Image.open(request.files['coverimg'])

    i.save(picture_path)

    if type == 'profile':
        webp.cwebp(os.path.join(config['UPLOAD_FOLDER_PROFILE'], picture_fn),
                   os.path.join(config['UPLOAD_FOLDER_PROFILE'], 'user_' + str(userId) + '.webp'), "-q 80")
    elif type == 'cover':
        webp.cwebp(os.path.join(config['UPLOAD_FOLDER_PROFILE_COVER'], picture_fn),
                   os.path.join(config['UPLOAD_FOLDER_PROFILE_COVER'], 'user_' + str(userId) + '.webp'), "-q 80")

    picture_fn = 'user_' + str(userId) + '.webp'

    return picture_fn


def GetItemForKeyN(value):
    return value['id']