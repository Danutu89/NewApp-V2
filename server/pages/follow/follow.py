from flask import Blueprint, make_response, jsonify, request
from modules import AuthOptional, AuthRequired
from sqlalchemy import desc, func, or_, asc, and_
from sqlalchemy.schema import Sequence
import datetime as dt
from app import db, socket
from webpush import send_notification

from models import User, User_Tags, Post_Tag, User_Following, User_Followed, Notification

follow = Blueprint('follow', __name__, url_prefix='/api/v2/follow')

@follow.route("/tag/<string:tag>")
@AuthRequired
def tag(tag, *args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first()
    tagQuery = Post_Tag.get().filter_by(name=tag).first()
    check = User_Tags.get().filter(and_(User_Tags.user==currentUser.id,User_Tags.tag_id==tagQuery.id)).first()

    if check is None:
        new_tag = User_Tags(
            user=currentUser.id,
            tag_id=tagQuery.id
        )
        new_tag.add()
        response = jsonify({'operation': 'followed'})
    else:
        check.delete()
        response = jsonify({'operation': 'unfollowed'})
        db.session.commit()

    return make_response(response, 200)

@follow.route("/user/<string:name>")
@AuthRequired
def user(name, *args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()
    userFollowed = User.get().filter_by(name=name).first()

    check = User_Following.get().filter(and_(User_Following.user==currentUser.id,User_Following.followed==userFollowed.id)).first()

    if check is None:
        new_follow = User_Following(
            user=currentUser.id,
            followed=userFollowed.id
        )
        new_follow.add()
        response = jsonify({'operation': 'followed'})
        body = 'started following you'
    else:
        check.delete()
        body = 'unfollowed you'
        response = jsonify({'operation': 'unfollowed'})

    notification = Notification(
        author=currentUser.id,
        user=userFollowed.id,
        type=1,
        checked=False,
        body=currentUser.name + ' ' + body,
        link='/user/' + str(currentUser.name)
    )
    notification.add()

    if userFollowed.status != 2:
        send_notification(userFollowed.id, {
            'text': currentUser.name + ' ' + body,
            'link': '/user/' + str(currentUser.name),
            'icon': currentUser.info.avatar_img,
            'id': notification.id
        })

    socket.emit("notification", room="notification-{}".format(userFollowed.id))
    return make_response(response, 200)

