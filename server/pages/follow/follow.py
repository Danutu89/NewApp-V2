from flask import Blueprint, make_response, jsonify, request
from .modules.utilities import AuthOptional, AuthRequired
from sqlalchemy import desc, func, or_, asc
from sqlalchemy.schema import Sequence
import datetime as dt
from app import db, socket
from webpush import send_notification

from models import TagModel, Notifications_Model, PostModel, UserModel

follow = Blueprint('follow', __name__, url_prefix='/api/v2/follow')

@follow.route("/tag/<string:tag>")
@AuthRequired
def tag(tag, *args, **kwargs):
    curruentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()
    int_tags = list(curruentUser.int_tags)

    if int_tags is not None:
        if tag in int_tags:
            int_tags.remove(tag)
            response = jsonify({'operation': 'unfollowed'})
        else:
            response = jsonify({'operation': 'followed'})
            int_tags.append(tag)
    else:
        response = jsonify({'operation': 'followed'})
        int_tags.append(tag)

    curruentUser.int_tags = int_tags
    db.session.commit()

    return make_response(response, 200)

@follow.route("/user/<int:id>")
@AuthRequired
def user(id, *args, **kwargs):
    user = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()
    not_id = str(db.session.execute(Sequence('notifications_id_seq')))

    follow = list(user.follow)
    followed = UserModel.query.filter_by(id=id).first()
    user_followed = list(followed.followed)
    if follow is not None:
        if id in follow:
            follow.remove(id)
            user_followed.remove(user.id)
            response = jsonify({'operation': 'unfollowed'})
            notify = Notifications_Model(
                int(not_id),
                user.id,
                '{} unfolowed you'.format(user.name),
                user.name,
                '/user/' + str(user.name) + '?notification_id=' + not_id,
                id,
                False,
                None,
                'follow'
            )
            send_notification(id, {
                'text': '@{} unfolowed you'.format(user.name),
                'link': '/user/' + str(user.name),
                'icon': user.avatar,
                'id': not_id
            })
            socket.emit("notification", room="notification-{}".format(id))
        else:
            follow.append(id)
            user_followed.append(user.id)
            response = jsonify({'operation': 'followed'})
            notify = Notifications_Model(
                int(not_id),
                user.id,
                '{} started folowing you'.format(user.name),
                user.name,
                '/user/' + str(user.name),
                id,
                False,
                None,
                'follow'
            )
            send_notification(id, {
                'text': '@{} started folowing you'.format(user.name),
                'link': '/user/' + str(user.name),
                'icon': user.avatar,
                'id': not_id
            })
            socket.emit("notification", room="notification-{}".format(id))
    else:
        follow.append(id)
        user_followed.append(user.id)
        response = jsonify({'operation': 'followed'})
        notify = Notifications_Model(
            int(not_id),
            user.id,
            '{} started folowing you'.format(user.name),
            user.name,
            '/user/' + str(user.name),
            id,
            False,
            None,
            'follow'
        )
        send_notification(id, {
            'text': '@{} started folowing you'.format(user.name),
            'link': '/user/' + str(user.name),
            'icon': user.avatar,
            'id': not_id
        })
        socket.emit("notification", room="notification-{}".format(id))

    db.session.add(notify)
    user.follow = follow
    followed.followed = user_followed
    db.session.commit()

    return make_response(response, 200)

