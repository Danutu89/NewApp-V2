from functools import wraps
from flask import request, make_response, jsonify
import jwt
from app import config
import datetime as dt

def AuthRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.cookies['token']
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
            token_header = request.cookies['token']
            decoded = jwt.decode(token_header, config['JWT_KEY'])
            kwargs['token'] = decoded
            kwargs['auth'] = True
        except Exception as e:
            kwargs['auth'] = False
        return f(*args, **kwargs)
    return decorated