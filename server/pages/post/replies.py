from flask import Blueprint, make_response, jsonify, request

from sqlalchemy import desc, func, or_, asc
from sqlalchemy.schema import Sequence
import datetime as dt
import json
from app import db, socket, config
from webpush import send_notification
import os
import re

from models import ReplyModel, PostModel, UserModel, Notifications_Model, ReplyOfReply
from .modules.utilities import AuthOptional, AuthRequired, cleanhtml

replies = Blueprint('replies', __name__, url_prefix='/api/v2/replies')

@replies.route("/delete/<int:reply_id>")
@AuthRequired
def delete(reply_id, *args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first()
    reply = ReplyModel.query.filter_by(id=reply_id).first()

    if currentUser.roleinfo.delete_reply_permission == False and currentUser.id != reply.user:
        return make_response(jsonify({'operation': 'no permission'}), 401)

    ReplyModel.query.filter_by(id=reply_id).delete()
    db.session.commit()

    return make_response(jsonify({'operation': 'success'}), 200)


@replies.route("/edit", methods=['POST'])
@AuthRequired
def edit(*args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    data = request.json

    if not data['r_id'] or not data['content']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

    reply = ReplyModel.query.filter_by(id=data['r_id']).first()

    if currentUser.roleinfo.edit_reply_permission == False and currentUser.id != reply.user:
        return make_response(jsonify({'operation': 'no permission'}), 401)

    reply.text = data['content']

    reply_json = {}

    reply_json['mentions'] = []
    reply_json['content'] = data['content']
    mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(data['content']))

    for mention in mentions:
        check = UserModel.query.filter_by(name=mention).first()
        if check is not None:
            reply_json['mentions'].append(mention)

    db.session.commit()

    return make_response(jsonify({'operation': 'success', 'reply': reply_json}), 200)

@replies.route('/newreply', methods=['POST'])
@AuthRequired
def new(*args, **kwargs):
    data = request.json

    if not data['token'] or not data['post_id'] or not data['content']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

    currentUser = UserModel.query.filter_by(kwargs['token']['id']).first_or_404()

    if data['type'] == 'post':
        new_reply = ReplyModel(None, data['content'], data['post_id'], currentUser.id, None)
        index = db.session.execute(Sequence('replyes_id_seq'))
    else:
        new_reply = ReplyOfReply(None, data['content'], data['reply_id'], currentUser.id, None)
        index = db.session.execute(Sequence('replies_of_replies_id_seq'))

    not_id = str(db.session.execute(Sequence('notifications_id_seq')))
    post = PostModel.query.filter_by(id=data['post_id']).first()
    notify = Notifications_Model(
        int(not_id),
        currentUser.id,
        '{} replied to your post'.format(currentUser.name),
        post.title,
        '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
            post.id) + '?notification_id=' + str(not_id),
        post.user_in.id,
        False,
        None,
        'reply'
    )
    db.session.add(new_reply)
    db.session.commit()
    db.session.add(notify)
    db.session.commit()
    send_notification(post.user_in.id, {
        'text': '{} replied to your {}'.format(currentUser.name, data['type']),
        'link': '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
        'icon': currentUser.avatar,
        'id': not_id
    })
    socket.emit("notification", room="notification-{}".format(post.user_in.id))
    mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(data['content']))
    mentioned = UserModel.query.filter(UserModel.name.in_(mentions)).all()
    for m in mentioned:
        not_id = str(db.session.execute(Sequence('notifications_id_seq')))
        notify = Notifications_Model(
            int(not_id),
            currentUser.id,
            '{} mentioned you in a comment'.format(m.name),
            cleanhtml(data['content'])[:20],
            '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
                post.id) + '?notification_id=' + str(not_id),
            post.user_in.id,
            False,
            None,
            'reply'
        )
        db.session.add(notify)
        db.session.commit()
        send_notification(post.user_in.id, {
            'text': '{}  mentioned you in a comment'.format(currentUser.name),
            'link': '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
                post.id),
            'icon': currentUser.avatar,
            'id': not_id
        })
        socket.emit("notification", room="notification-{}".format(m.id))

    return make_response(jsonify({'operation': 'success', 'reply_id': index}), 200)