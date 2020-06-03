from functools import wraps
from flask import request, make_response, jsonify
import jwt
import os
import datetime as dt
from sqlalchemy import desc, func, or_, asc

from models import Analyze_Pages, TagModel, PostModel

def AuthRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.headers['Token']
            decoded = jwt.decode(token_header, os.environ['JWT_KEY'])
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
            decoded = jwt.decode(token_header)
            kwargs['token'] = decoded
            kwargs['auth'] = True
        except Exception as e:
            kwargs['auth'] = False
        return f(*args, **kwargs)
    return decorated