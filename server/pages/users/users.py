from flask import Blueprint, make_response, jsonify, request

from sqlalchemy import desc, func, or_, asc, and_
import datetime as dt
from app import config
from models import User, Post, Post_Tags, Post_Tag, User_Following, Post_Comments, User_Tags, Social_Types, User_Social, User_Settings
import os
from .modules.utilities import jwt, config, SaveImage, generateUserToken, CreateAvatar
from modules import AuthOptional, AuthRequired
import json
from .modules.serializer import UserSchema, SettingsSchema, SocialSchema, UserMinSchema

users = Blueprint('users', __name__, url_prefix='/api/v2/users')


@users.route("/<string:name>")
@AuthOptional
def user(name, *args, **kwargs):
    user = User.get().filter_by(name=name).first_or_404()
    posts = Post.get().filter_by(author_id=user.id).order_by(desc(Post.created_on)).paginate(page=1, per_page=5)

    currentUser = None

    if kwargs['auth']:
        currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()

    serializer = UserSchema(many=False)

    serializer.context['currentUser'] = currentUser
    serializer.context['posts'] = posts

    user_json = serializer.dump(user)

    return make_response(jsonify(user_json), 200)


@users.route('/settings/<string:name>', methods=['GET', 'POST'])
@AuthRequired
def settings(*args, **kwargs):

    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()

    socials = Social_Types.get().all()

    if request.method == 'POST':
        data = json.loads(request.form['data'].encode().decode('utf-8'))

        print(data)

        if 'info' in data.keys():

            if 'avatar_img' in data['info'].keys():
                if data['info']['avatar_img']:
                    data['info']['avatar_img'] = SaveImage(currentUser.id, 'profile')
            if 'cover_img' in data['info'].keys():
                if data['info']['cover_img']:
                    data['info']['cover_img'] = SaveImage(currentUser.id, 'cover')

            for value, key in data['info'].items():
                setattr(currentUser.info, value, key)

        if 'pers' in data.keys():

            for value, key in data['pers'].items():
                setattr(currentUser.pers, value, key)

        socials_ids = [s.id for s in currentUser.social]

        d_socials = socials_ids

        for social in data['social']:
            if social['id'] == 'new':
                new_social = User_Social(
                    user=currentUser.id, 
                    type=social['social']['id'], 
                    link=social['link']
                )
                new_social.add()
            elif social['id']:
                user_social = User_Social.get().filter_by(id=social['id']).first()
                user_social.link = social['link']
                user_social.save()
                
                d_socials.remove(user_social.id)

        User_Social.get().filter_by(user=currentUser.id).filter(User_Social.id.in_(d_socials)).delete(synchronize_session='fetch')

        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            userIP = request.environ['REMOTE_ADDR']
        else:
            userIP = request.environ['HTTP_X_FORWARDED_FOR']
        
        currentUser.save()
        userIP = userIP.split(', ')[0]

        token = generateUserToken(currentUser, userIP)

        return make_response(jsonify({'operation': 'success', 'token': token.decode('UTF-8')}), 200)

    settings_temp = SettingsSchema(exclude=('info.full_name',)).dump(currentUser)

    user_s = User_Settings.get().all()
    settings_perm = {
        'social': settings_temp['social']
    }

    for s in user_s:
        try:
            if not settings_perm[s.type]:
                settings_perm[s.type] = {}
        except:
            settings_perm[s.type] = {}
        
        settings_perm[s.type][s.key] = {
            'type': s.type,
            'name': s.name,
            'value': settings_temp[s.category][s.key],
            'key': s.key,
            'category': s.category
        }

    settings = {
        "settings": settings_perm,
        "utilities": {
            "socials": SocialSchema(many=True).dump(socials)
        }
    }

    return make_response(jsonify(settings), 200)

@users.route('/', methods=['GET'])
@AuthRequired
def users_list(*args, **kwargs):
    users = User.get().all()

    return make_response(jsonify(UserMinSchema(many=True).dump(users)), 200)

@users.route('/set/default/avatar', methods=['GET'])
@AuthRequired
def avatar(*args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()

    os.umask(0)
    os.mkdir(config.get('ROOT_PATH')+'/static/users/'+str(currentUser.id))
    CreateAvatar({"id": currentUser.id, "first_name": currentUser.info.first_name, "last_name": currentUser.info.last_name})

