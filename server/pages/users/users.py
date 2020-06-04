from flask import Blueprint, make_response, jsonify, request

from sqlalchemy import desc, func, or_, asc
import datetime as dt
from models import TagModel, ReplyModel, PostModel, UserModel
from .modules.utilities import AuthOptional, AuthRequired, jwt, config, SaveImage, generateUserToken
import json

users = Blueprint('users', __name__, url_prefix='/api/v2/users')


@users.route("/<string:name>")
@AuthOptional
def user(name, *args, **kwargs):
    user = UserModel.query.filter_by(name=name).first_or_404()
    posts = PostModel.query.filter_by(user=user.id).order_by(desc(PostModel.posted_on)).paginate(page=1, per_page=5)

    if user.followed:
        followed = UserModel.query.filter(UserModel.id.in_(user.followed[0:5])).all()

    user_json = {}
    user_follow_list = []
    user_follow_json = {}
    posts_user_list = []
    posts_temp = {}

    for post in posts.items:
        posts_temp['title'] = post.title
        posts_temp['author'] = {
            'name': user.name,
            'avatar': user.avatar
        }
        posts_temp['posted_on'] = post.time_ago()
        posts_temp['tags'] = TagModel.query.with_entities(TagModel.name).filter(TagModel.post.contains([post.id])).all()
        posts_temp['read_time'] = post.read_time
        posts_temp['id'] = post.id
        posts_temp['link'] = (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id)
        posts_user_list.append(posts_temp.copy())

    user_json['id'] = user.id
    user_json['name'] = user.name
    user_json['real_name'] = user.real_name
    user_json['avatar'] = user.avatar
    user_json['cover'] = user.cover
    user_json['bio'] = user.bio
    user_json['profession'] = user.profession
    user_json['country_name'] = user.country_name
    user_json['country_flag'] = user.country_flag
    user_json['join_date'] = str(user.join_date.ctime())[:-14] + ' ' + str(user.join_date.ctime())[20:]
    user_json['followed_count'] = len(user.followed)
    user_json['tags_check'] = True if len(user.int_tags) > 0 else False
    user_json['tags'] = user.int_tags
    user_json['post_count'] = PostModel.query.filter_by(user=user.id).filter_by(approved=True).count()
    user_json['reply_count'] = ReplyModel.query.filter_by(user=user.id).count()
    user_json['post_views'] = 53
    user_json['posts'] = {
        'list': sorted(posts_user_list, key=lambda i: i['id'], reverse=True),
        'hasnext': True if posts.has_next else False
    }
    user_json['follow_check'] = True if len(user.followed) > 0 else False

    if user.facebook or user.twitter or user.github or user.instagram or user.website:
        user_json['social'] = True
        if user.facebook:
            user_json['facebook'] = user.facebook
        if user.instagram:
            user_json['instagram'] = user.instagram
        if user.twitter:
            user_json['twitter'] = user.twitter
        if user.github:
            user_json['github'] = user.github
        if user.website:
            user_json['website'] = user.website

    if user.followed:
        for f in followed:
            user_follow_json['name'] = f.name
            user_follow_json['real_name'] = f.real_name
            user_follow_json['avatar'] = f.avatar
            user_follow_list.append(user_follow_json.copy())

        user_json['follows'] = user_follow_list

    if kwargs['auth'] == False:
        return make_response(jsonify(user_json), 200)

    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    user_json['info'] = {
        'following': True if currentUser.id in user.followed else False
    }

    return make_response(jsonify(user_json), 200)


@users.route('/settings', methods=['GET', 'POST'])
@AuthRequired
def settings(*args, **kwargs):

    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    if request.method == 'POST':
        print(request)
        data = json.loads(request.form['data'].encode().decode('utf-8'))

        # if str(user_info.email).replace(" ", "") != str(data['email']).replace(" ",""):
        for key, setting in data.iteritems():

            if key == "avatar":
                setattr(currentUser, key, '/static/profile_pics/' + SaveImage(currentUser.id, 'profile'))
            elif key == "cover":
                setattr(currentUser, key, '/static/profile_cover/' + SaveImage(currentUser.id, 'cover'))
            else:
                setattr(currentUser, key, setting)

        currentUser.save()

        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            userIP = request.environ['REMOTE_ADDR']
        else:
            userIP = request.environ['HTTP_X_FORWARDED_FOR']
        
        userIP = userIP.split(', ')[0]

        token = generateUserToken(currentUser, userIP)

        return make_response(jsonify({'operation': 'success', 'token': token.decode('UTF-8')}), 200)

    settings_json = {}
    settings_json['name'] = currentUser.name
    settings_json['real_name'] = currentUser.real_name
    settings_json['email'] = currentUser.email
    settings_json['bio'] = currentUser.bio
    settings_json['profession'] = currentUser.profession
    settings_json['instagram'] = currentUser.instagram
    settings_json['facebook'] = currentUser.facebook
    settings_json['github'] = currentUser.github
    settings_json['twitter'] = currentUser.twitter
    settings_json['website'] = currentUser.website
    settings_json['genre'] = currentUser.genre
    settings_json['theme_mode'] = currentUser.theme_mode
    settings_json['theme'] = currentUser.theme
    settings_json['avatar'] = currentUser.avatar
    settings_json['cover'] = currentUser.cover

    return make_response(jsonify({'settings': settings_json}), 200)