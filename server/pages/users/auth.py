from flask import Blueprint, make_response, jsonify, request, render_template
import datetime as dt
from app import config, bcrypt, serializer, BadSignature, BadTimeSignature, SignatureExpired, mail
import os
import jwt
from models import UserModel, Ip_Coordinates
import requests
import httpagentparser
from flask_mail import Message
from .modules.utilities import generateUserToken


auth = Blueprint('auth', __name__, url_prefix='/api/v2/users/auth')

@auth.route("/login", methods=['POST'])
def login():
    auth = request.json

    if not auth:
        return make_response(jsonify({'login': 'No credentials'}), 401)

    if not auth['username']:
        return make_response(jsonify({'login': 'No username'}), 401)

    user = UserModel.query.filter_by(name=auth['username']).first()

    if not user:
        user = UserModel.query.filter_by(email=auth['username']).first()

    if not user:
        return make_response(jsonify({'login': 'No user', 'camp': 'user'}), 401)

    if not auth['password']:
        return make_response(jsonify({'login': 'No password'}), 401)

    if bcrypt.check_password_hash(user.password, auth['password']) == False:
        return make_response(jsonify({'login': 'Wrong password', 'camp': 'password'}), 401)
    
    if user.activated == False:
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

    if data is None or data['username'] is None or data['email'] is None or data['realname'] is None or data[
        'password'] is None:
        return jsonify({'register': 'Error'}), 401

    check = UserModel.query.filter_by(name=data['username']).first()

    if check is not None:
        return jsonify({'register': 'Username taken'}), 401

    check = UserModel.query.filter_by(email=data['email']).first()

    if check is not None:
        return jsonify({'register': 'Email taken'}), 401

    token = serializer.dumps(data['email'], salt='register-confirm')

    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']

    if userIP == "127.0.0.1":
        userIP = "86.123.189.180"

    ip_user = Ip_Coordinates.query.filter_by(ip=userIP).first()

    try:

        if ip_user is None:
            resp = requests.get(
                ('https://www.iplocate.io/api/lookup/{}').format(userIP))
            userLoc = resp.json()
            iso_code = userLoc['country_code']
            country_name = userLoc['country']
            rest = False
        else:
            resp = requests.get(
                ("https://restcountries.eu/rest/v2/alpha/{}").format(ip_user.location.iso_code))
            userLoc = resp.json()
            country_name = userLoc['name']
            iso_code = ip_user.location.iso_code
            rest = True

        if rest:
            userLanguage = userLoc['languages'][0]['iso639_1']
        else:
            api_2 = requests.get(
                ("https://restcountries.eu/rest/v2/alpha/{}").format(iso_code))
            result_2 = api_2.json()
            userLanguage = result_2['languages'][0]['iso639_1']
    except:
        pass

    msg = Message('Confirm Email Registration', sender='contact@newapp.nl', recipients=[data['email']])
    link = 'https://new-app.dev/?email={}&token={}'.format(data['email'], token)
    msg.html = render_template('email_register.html', register=link, email='contact@newapp.nl')
    mail.send(msg)

    new_user = UserModel(
        name=data['username'].lower(),
        real_name=data['realname'],
        email=data['email'].lower(),
        password=data['password'],
        avatar="https://www.component-creator.com/images/testimonials/defaultuser.png",
        activated=False,
        ip_address=userIP,
        browser=userInfo['browser']['name'],
        #country_name=country_name,
        #country_flag=str(iso_code).lower(),
        lang='ro',
        theme='Light',
        theme_mode='system'
    )
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

    user = UserModel.query.filter_by(email=data['email']).first()
    user.activated = True

    db.session.commit()

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']
    
    userIP = userIP.split(', ')[0]

    token = generateUserToken(user, userIP)

    return jsonify({'confirm': 'success', 'token': token}), 200


@auth.route('/register/check/username/<string:user>', methods=['GET'])
def check_username(user):
    check = UserModel.query.filter_by(name=user).first()

    if check is not None:
        json = {'check': True}
    else:
        json = {'check': False}

    return jsonify(json), 200


@auth.route('/register/check/email/<string:email>', methods=['GET'])
def check_email(email):
    check = UserModel.query.filter_by(email=email).first()

    if check is not None:
        json = {'check': True}
    else:
        json = {'check': False}

    return jsonify(json), 200

