from flask import Blueprint, make_response, jsonify, request
from .modules.utilities import AuthOptional, AuthRequired, GetItemForKeyN
from sqlalchemy import desc, func, or_, asc
from sqlalchemy.schema import Sequence
import datetime as dt
from app import db, socket
from webpush import send_notification

from models import TagModel, Notifications_Model, PostModel, UserModel, Subscriber

notifications = Blueprint('notifications', __name__, url_prefix='/api/v2/users/notifications')

@notifications.route("/")
@AuthRequired
def index(*args, **kwargs):
    extended = request.args.get('ex')
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    if extended == 'true':
        notifications = {'notify': {'new': [], 'posts': [], 'comments': [], 'likes': [], 'follows': []},
                         'count_new': currentUser.get_not_count(currentUser.id)}
        temp = {}

        for val, n in enumerate(currentUser.n_receiver):

            if val == 50:
                break

            temp['body'] = n.body
            temp['checked'] = n.checked
            temp['id'] = n.id
            temp['title'] = n.title
            temp['link'] = n.link
            temp['category'] = n.category
            temp['author'] = {
                'avatar': n.author.avatar,
                'name': n.author.name
            }
            temp['time_ago'] = n.time_ago()

            if n.checked == False:
                notifications['notify']['new'].append(temp.copy())
            if n.category == 'post':
                notifications['notify']['posts'].append(temp.copy())
            elif n.category == 'reply':
                notifications['notify']['comments'].append(temp.copy())
            elif n.category == 'like':
                notifications['notify']['likes'].append(temp.copy())
            elif n.category == 'follow':
                notifications['notify']['follows'].append(temp.copy())

        notifications['notify']['new'].sort(key=GetItemForKeyN, reverse=True)
        notifications['notify']['posts'].sort(key=GetItemForKeyN, reverse=True)
        notifications['notify']['comments'].sort(key=GetItemForKeyN, reverse=True)
        notifications['notify']['likes'].sort(key=GetItemForKeyN, reverse=True)
        notifications['notify']['follows'].sort(key=GetItemForKeyN, reverse=True)

    else:
        limit = currentUser.get_not_count(currentUser.id) if currentUser.get_not_count(currentUser.id) < 10 else 10

        notifications = {'notify': [], 'count_new': currentUser.get_not_count(currentUser.id), 'count': limit}
        temp = {}

        for n in currentUser.n_receiver:
            if n.checked == False:
                temp['body'] = n.body
                temp['checked'] = n.checked
                temp['id'] = n.id
                temp['title'] = n.title
                temp['link'] = n.link
                temp['category'] = n.category
                temp['author'] = {
                    'avatar': n.author.avatar,
                    'name': n.author.name
                }
                temp['time_ago'] = n.time_ago()
                notifications['notify'].append(temp.copy())

        notifications['notify'].sort(key=GetItemForKeyN, reverse=True)
        notifications['notify'] = notifications['notify'][:limit]

    return make_response(jsonify(notifications), 200)

@notifications.route("/check/<int:id>")
@AuthRequired
def check(id, *args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first()
    notification = Notifications_Model.query.filter_by(id=id).first()

    if notification is None:
        return make_response(jsonify({'operation': 'failed'}), 401)

    if notification.for_user != currentUser.id:
        return make_response(jsonify({'operation': 'failed'}), 401)

    notification.checked = True

    db.session.commit()

    return make_response(jsonify({'operation': 'success'}), 200)


@notifications.route("/subscribe", methods=['POST'])
@AuthRequired
def subscribe(*args, **kwargs):
    if request.method != 'POST':
        return make_response(jsonify({'operation': 'failed'}), 401)

    data = request.json
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    sub = Subscriber(None, currentUser.id, None, None, str(data['sub_info']), True)
    db.session.add(sub)
    db.session.commit()
    return make_response(jsonify({'operation': 'success'}), 200)