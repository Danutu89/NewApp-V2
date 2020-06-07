from functools import wraps
from flask import request, make_response, jsonify
import jwt
import os
import datetime as dt
from sqlalchemy import desc, func, or_, asc
from app import config

from models import Analyze_Pages, TagModel, PostModel

def AuthRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.headers['Token']
            decoded = jwt.decode(token_header, config['JWT_KEY'])
            kwargs['token'] = decoded
            print(kwargs['token'])
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