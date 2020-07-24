from flask import Blueprint, make_response, jsonify, request

from sqlalchemy import desc, func, or_, asc
from sqlalchemy.schema import Sequence
import datetime as dt
import json
from app import db, socket, config
from webpush import send_notification
import os
import re

from models import User, Post_Comments, Comment_Reply, Notification, Post

from .modules.serializer import CommentsSchema, RepliesSchema
from modules import AuthOptional, AuthRequired
from .modules.utilities import cleanhtml

replies = Blueprint('replies', __name__, url_prefix='/api/v2/replies')

@replies.route("/delete/<int:reply_id>")
@AuthRequired
def delete(reply_id, *args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()
    reply = Post_Comments.get().filter_by(id=reply_id).first_or_404()

    if currentUser.role.permissions.delete_reply == False and currentUser.id != reply.user:
        return make_response(jsonify({'operation': 'no permission'}), 401)

    reply.delete()

    return make_response(jsonify({'operation': 'success'}), 200)


@replies.route("/edit", methods=['POST'])
@AuthRequired
def edit(*args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()

    data = request.json

    if not data['r_id'] or not data['content']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

    reply = Post_Comments.get().filter_by(id=data['r_id']).first()

    if currentUser.role.permissions.edit_reply == False and currentUser.id != reply.user:
        return make_response(jsonify({'operation': 'no permission'}), 401)

    reply.text = data['content']
    reply.save()

    reply_json = {}

    reply_json['mentions'] = []
    reply_json['content'] = reply.text
    mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(data['content']))

    for mention in mentions:
        check = User.get().filter_by(name=mention).first()
        if check is not None:
            reply_json['mentions'].append(mention)


    return make_response(jsonify({'operation': 'success', 'reply': reply_json}), 200)

@replies.route('/new', methods=['POST'])
@AuthRequired
def new(*args, **kwargs):
    data = request.json

    if not data or not data['post_id'] or not data['content']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

    post = Post.get().filter_by(id=data['post_id']).first()

    if not post:
        return make_response(jsonify({'operation': 'error', 'error': 'No post'}), 401)

    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()

    if data['type'] == 'post':
        new_reply = Post_Comments(post=data['post_id'], text=data['content'], author_id=currentUser.id)
    else:
        new_reply = Comment_Reply(text=data['content'], comment=data['reply_id'], author_id=currentUser.id)
    
    new_reply.add()

    not_id = str(db.session.execute(Sequence('notification_id_seq')))
    
    notify = Notification(
        id=int(not_id),
        author=currentUser.id,
        body='{} replied to your post'.format(currentUser.name),
        title=post.title,
        link=post.link + '?notification_id=' + str(not_id),
        user=post.author.id,
        type=4
    )
    notify.add()
    send_notification(post.author.id, {
        'text': '{} replied to your {}'.format(currentUser.name, data['type']),
        'link': post.link + '?notification_id=' + str(not_id),
        'icon': currentUser.info.avatar_img,
        'id': not_id
    })
    socket.emit("notification", room="notification-{}".format(post.author.id))
    mentions = re.findall("@([a-zA-Z0-9]{1,15})", cleanhtml(data['content']))
    mentioned = User.get().filter(User.name.in_(mentions)).all()
    for m in mentioned:
        not_id = str(db.session.execute(Sequence('notification_id_seq')))
        notify = Notification(
            id=int(not_id),
            author=currentUser.id,
            title='{} mentioned you in a comment'.format(m.name),
            body=cleanhtml(data['content'])[:20],
            link=post.link + '?notification_id=' + str(not_id),
            user=post.author.id,
            type=6
        )
        notify.add()
        send_notification(post.author.id, {
            'text': '{}  mentioned you in a comment'.format(currentUser.name),
            'link': post.link + '?notification_id=' + str(not_id),
            'icon': currentUser.info.avatar_img,
            'id': not_id
        })
        socket.emit("notification", room="notification-{}".format(m.id))

    reply_json = {}

    if data['type'] == 'post':
        serializer = CommentsSchema(many=False)
        serializer.context['currentUser'] = currentUser
        reply_json = serializer.dump(new_reply)
    else:
        serializer = RepliesSchema(many=False)
        serializer.context['currentUser'] = currentUser
        reply_json = serializer.dump(new_reply)

    return make_response(jsonify({'operation': 'success', 'reply': reply_json}), 200)