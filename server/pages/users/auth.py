from flask import Blueprint, make_response, jsonify, request, render_template
import datetime as dt
from app import config, bcrypt, serializer, BadSignature, BadTimeSignature, SignatureExpired, mail, db
import os
import jwt
from sqlalchemy import desc, func, or_, asc, and_
from models import User, Ip_Location, Languages, User_Info, User_Pers
import requests
import httpagentparser
from flask_mail import Message
from .modules.utilities import generateUserToken, CreateAvatar
from .modules.serializer import NewUserSchema, NewLanguageSchema, NewLocationSchema
from sqlalchemy.schema import Sequence

auth = Blueprint('auth', __name__, url_prefix='/api/v2/users/auth')

@auth.route("/login", methods=['POST'])
def login():
    auth = request.json

    if not auth:
        return make_response(jsonify({'login': 'No credentials'}), 401)

    if not auth['username']:
        return make_response(jsonify({'login': 'No username'}), 401)

    user = User.get().filter(or_(User.name==auth['username'],User.email==auth['username'])).first()

    if not user:
        return make_response(jsonify({'login': 'No user', 'camp': 'user'}), 401)

    if not auth['password']:
        return make_response(jsonify({'login': 'No password'}), 401)

    if bcrypt.check_password_hash(user.password, auth['password']) == False:
        return make_response(jsonify({'login': 'Wrong password', 'camp': 'password'}), 401)
    
    if user.confirmed == False:
        return make_response(jsonify({'login': 'Account not activated'}), 401)

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']
    
    userIP = userIP.split(', ')[0]

    token = generateUserToken(user, userIP)

    return make_response(jsonify({'login': token.decode('UTF-8')}), 200)

@auth.route("/register", methods=['POST'])
def register():
    data = request.json

    if data is None or data['username'] is None or data['email'] is None or data['first_name'] is None or data['last_name'] is None or data[
        'password'] is None:
        return jsonify({'register': 'Error'}), 401

    check = User.get().filter_by(name=data['username']).first()

    if check is not None:
        return jsonify({'register': 'Username taken'}), 401

    check = User.get().filter_by(email=data['email']).first()

    if check is not None:
        return jsonify({'register': 'Email taken'}), 401

    token = serializer.dumps(data['email'], salt='register-confirm')

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']

    userIP = userIP.split(',')[0]

    if userIP == "127.0.0.1":
        userIP = "86.123.189.180"

    resp = requests.get(
        ('https://www.iplocate.io/api/lookup/{}').format(userIP))
    userLoc = resp.json()
    iso_code = userLoc['country_code']
    api_2 = requests.get(
        ("https://restcountries.eu/rest/v2/alpha/{}").format(iso_code))
    result_2 = api_2.json()

    index = str(db.session.execute(Sequence('users_id_seq')))

    msg = Message('Confirm Email Registration', sender='contact@newapp.nl', recipients=[data['email']])
    link = 'https://new-app.dev/?email={}&token={}'.format(data['email'], token)
    msg.html = render_template('email_register.html', register=link, email='contact@newapp.nl')
    mail.send(msg)

    check_loc = Ip_Location.get().filter_by(ip=userIP).first()
    check_lang = Languages.get().filter_by(code=result_2['languages'][0]['iso639_1']).first()

    os.umask(0)
    os.mkdir(config.get('ROOT_PATH')+'/static/users/'+index)

    if check_loc is None:
        ip_loc_index = str(db.session.execute(Sequence('ip_location_id_seq')))
        loc_index = str(db.session.execute(Sequence('location_id_seq')))

    new_user_json = {
        "id": index,
        "confirmed": False,
        "email": data['email'],
        "info": {
            "avatar_img": CreateAvatar({"id": index, "first_name": data['first_name'], "last_name": data['last_name']}),
            "user": index,
            "first_name": data['first_name'],
            "last_name": data['last_name']
        },
        "pers": {
            "user": index
        },
        "name": data['username'],
        "role_id": 2,
        "status_id": 2,
        "password": data["password"]
    }

    if check_lang is None:
        new_user_json["language"] = {
            "code": result_2['languages'][0]['iso639_1'],
            "name": result_2['languages'][0]['name'],
        }
    else:
        new_user_json["language"] = NewLanguageSchema().dump(check_lang)

    if check_loc is None:
        new_user_json["location"] = {
            "ip": userIP,
            "id": ip_loc_index,
            "location": {
                "id": loc_index,
                "city": userLoc['city'],
                "country": userLoc['country'],
                "flag": result_2['languages'][0]['iso639_1'],
                "iso": userLoc['country_code'],
                "latitude": str(userLoc['latitude']),
                "longitude": str(userLoc['longitude']),
            }
        }
    else:
        new_user_json["location"] = NewLocationSchema().dump(check_loc)

    new_user = NewUserSchema().load(new_user_json)
    new_user.add()

    return make_response(jsonify({'register': 'success'}), 200)

@auth.route('/register/confirm', methods=['POST'])
def confirm():

    data = request.json

    try:
        email_token = serializer.loads(data['token'], salt='register-confirm', max_age=300)
    except SignatureExpired:
        return jsonify({'confirm': 'Invalid Token'}), 401
    except BadTimeSignature:
        return jsonify({'confirm': 'Invalid Token'}), 401
    except BadSignature:
        return jsonify({'confirm': 'Invalid Token'}), 401

    user = User.get().filter_by(email=data['email']).first()
    user.confirmed = True

    user.save()

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']
    
    userIP = userIP.split(', ')[0]

    token = generateUserToken(user, userIP)

    return make_response(jsonify({'confirm': 'success', 'token': token}), 200)


@auth.route('/register/check/username/<string:user>', methods=['GET'])
def check_username(user):
    check = User.get().filter_by(name=user).first()

    if check is not None:
        json = {'check': True}
    else:
        json = {'check': False}

    return make_response(jsonify(json), 200)


@auth.route('/register/check/email/<string:email>', methods=['GET'])
def check_email(email):
    check = User.get().filter_by(email=email).first()

    if check is not None:
        json = {'check': True}
    else:
        json = {'check': False}

    return make_response(jsonify(json), 200)