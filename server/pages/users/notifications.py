from flask import Blueprint, make_response, jsonify, request
from modules import AuthOptional, AuthRequired
from .modules.utilities import GetItemForKeyN
from sqlalchemy import desc, func, or_, asc
from sqlalchemy.schema import Sequence
import datetime as dt
from app import db, socket
from webpush import send_notification

from models import Notification, User, Notification_Subscriber

notifications = Blueprint('notifications', __name__, url_prefix='/api/v2/users/notifications')

@notifications.route("/")
@AuthRequired
def index(*args, **kwargs):
    extended = request.args.get('ex')
    currentUser = User.get().filter_by(id=kwargs['token']['id']).first_or_404()

    if extended == 'true':
        notifications = {'notify': {'new': [], 'posts': [], 'comments': [], 'likes': [], 'follows': []},
                         'count_new': currentUser.get_not_count()}
        temp = {}

        for val, n in enumerate(currentUser.notifications):

            if val == 50:
                break

            temp['body'] = n.body
            temp['checked'] = n.checked
            temp['title'] = n.title
            temp['link'] = n.link
            temp['category'] = n.type.name
            temp['author'] = {
                'avatar': n.author.info.avatar,
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
        not_count = currentUser.get_not_count()
        limit = not_count if not_count < 10 else 10

        notifications = {'notify': [], 'count_new': not_count, 'count': limit}
        temp = {}

        for n in currentUser.n_receiver:
            if n.checked == False:
                temp['body'] = n.body
                temp['checked'] = n.checked
                temp['title'] = n.title
                temp['link'] = n.link
                temp['category'] = n.type.name
                temp['author'] = {
                    'avatar': n.author.info.avatar,
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
    currentUser = User.get().filter_by(id=kwargs['token']['id']).first()
    notification = Notification.get().filter_by(id=id).first()

    if notification is None:
        return make_response(jsonify({'operation': 'failed'}), 401)

    if notification.for_user != currentUser.id:
        return make_response(jsonify({'operation': 'failed'}), 401)

    notification.checked = True

    notification.save()

    return make_response(jsonify({'operation': 'success'}), 200)


@notifications.route("/subscribe", methods=['POST'])
@AuthRequired
def subscribe(*args, **kwargs):
    if request.method != 'POST':
        return make_response(jsonify({'operation': 'failed'}), 401)

    data = request.json
    currentUser = User.get().filter_by(id=kwargs['token']['id']).first_or_404()

    sub = Notification_Subscriber(
            user=currentUser.id, 
            info=str(data['sub_info']), 
            is_active=True
        )
    sub.add()
    return make_response(jsonify({'operation': 'success'}), 200)