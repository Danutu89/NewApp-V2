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
            return make_response(jsonify({'auth': 'Invalid token.'}), 401)
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

def GetReplies(post):
    replies_json = []
    for reply in post.replyes:
        reply_json = {}
        reply_json['mentions'] = []
        mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(reply.text))

        for mention in mentions:
            check = UserModel.query.filter_by(name=mention).first()
            if check is not None:
                replies_json['mentions'].append(mention)

        reply_json['text'] = reply.text
        reply_json['text_e'] = reply.text
        reply_json['id'] = reply.id
        reply_json['author'] = {
            'name': reply.user_in.name,
            'id': reply.user_in.id,
            'avatar': reply.user_in.avatar,
            'status': reply.user_in.status,
            'status_color': reply.user_in.status_color
        }

        replies_json.append(reply_json.copy())
        reply_json.clear()

    return replies_json

def GetUserPosts(post):
    user_posts = []
    for post in post.user_in.posts:
        user_posts_json = {
            'id': post.id,
            'title': post.title,
            'link': (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
            'author': {
                'id': post.user_in.id,
                'name': post.user_in.name,
                'avatar': post.user_in.avatar
            },
            'tags': TagModel.query.with_entities(TagModel.name).filter(TagModel.post.contains([post.id])).all()
        }
        user_posts.append(user_posts_json.copy())

    return user_posts[0:5]

def SaveImage(post_id):
    # if(form_img.data):
    file_name, file_ext = os.path.splitext(request.files['image'].filename)
    picture_fn = 'post_' + str(post_id) + file_ext
    picture_path = os.path.join(config['UPLOAD_FOLDER_POST'], picture_fn)

    i = Image.open(request.files['image'])
    i.save(picture_path)
    webp.cwebp(os.path.join(config['UPLOAD_FOLDER_POST'], picture_fn),
               os.path.join(config['UPLOAD_FOLDER_POST'], 'post_' + str(post_id) + '.webp'), "-q 80")
    os.remove(os.path.join(config['UPLOAD_FOLDER_POST'], picture_fn))

    picture_fn = 'post_' + str(post_id) + '.webp'

    return picture_fn
