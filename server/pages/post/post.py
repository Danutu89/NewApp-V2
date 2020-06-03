from flask import Blueprint, make_response, jsonify, request, url_for

from sqlalchemy import desc, func, or_, asc
import datetime as dt
import json
from sqlalchemy.schema import Sequence
from app import db, translate, socket, config
import readtime
from webpush import send_notification
import os

from models import TagModel, Analyze_Pages, ReplyModel, PostModel, UserModel, Notifications_Model
from .modules.utilities import AuthOptional, AuthRequired, SaveImage, GetReplies, cleanhtml, GetUserPosts

post = Blueprint('post', __name__, url_prefix='/api/v2/post')

@post.route("/<int:id>")
@AuthOptional
def index(id, *args, **kwargs):
    post = PostModel.query.filter_by(id=id).first_or_404()

    post_json = {}
    keywords = ''

    post_json['title'] = post.title
    post_json['link'] = (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id)
    post_json['id'] = post.id
    post_json['text'] = post.text
    post_json['likes'] = post.likes
    post_json['closed'] = post.closed
    post_json['thumbnail'] = post.thumbnail

    for key in str(post.title).split(" "):
        keywords += key + ','

    post_json['keywords'] = keywords
    post_json['description'] = cleanhtml(post.text)[:97]

    if post.closed:
        post_json['closed_on'] = post.closed_on
        post_json['closed_by'] = post.closed_by_name()

    post_json['author'] = {
        'name': post.user_in.name,
        'avatar': post.user_in.avatar,
        'real_name': post.user_in.real_name,
        'id': post.user_in.id,
        'joined_on': str(post.user_in.join_date.ctime())[:-14] + ' ' + str(post.user_in.join_date.ctime())[20:],
        'profession': post.user_in.profession,
        'country': post.user_in.country_name,
        'country_flag': post.user_in.country_flag,
        'posts': GetUserPosts(post),
    }
    post_json['replies'] = GetReplies(post)
    post_json['tags'] = TagModel.query.with_entities(TagModel.name).filter(TagModel.post.contains([post.id])).all()

    if kwargs['auth'] == False:
        return make_response(jsonify(post_json), 200)

    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    post_json['user'] = {
        'liked': True if post.id in currentUser.liked_posts else False, 
        'following': True if post.user_in.id in currentUser.follow else False
    }

    return make_response(jsonify(post_json), 200)

@post.route("/new")
@AuthRequired
def new(*args, **kwargs):
    if request.method != 'POST':
        return make_response(jsonify({'operation': 'error', 'error': 'Invalid method'}), 401)

    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    data = json.loads(str(request.form['data']).decode('utf-8', errors='replace'))

    if not data['token'] or not data['title'] or not data['content'] or not data['title'] or not data['tags']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

    index = db.session.execute(Sequence('posts_id_seq'))
    thumbnail_link = None
    if data['image']:
        thumbnail = SaveImage(index)
        thumbnail_link = url_for('static', filename='thumbail_post/{}'.format(thumbnail))

    lang = translate.getLanguageForText(str(cleanhtml(data['content'])).encode('utf-8-sig'))
    new_post = PostModel(
        index,
        data['title'],
        data['content'],
        None,
        None,
        currentUser.id,
        None,
        False,
        False,
        None,
        None,
        str(lang.iso_tag).lower(),
        thumbnail_link,
        None,
        str(readtime.of_html(data['content']))
    )

    tags = []
    tag_p = str(data['tags']).lower()
    tag = tag_p.replace(" ", "")
    tags = tag.split(",")
    for t in tags:
        temp = TagModel.query.filter_by(name=str(t).lower()).first()
        if temp is not None:
            d = []
            d = list(temp.post)
            d.append(index)
            temp.post = d
        else:
            tag = TagModel(
                None,
                str(t).lower(),
                [index]
            )
            db.session.add(tag)
    for user in currentUser.followed:
        not_id = str(db.session.execute(Sequence('notifications_id_seq')))
        notification = Notifications_Model(
            int(not_id),
            currentUser.id,
            '{} shared a new post'.format(currentUser.name),
            str(data['title']),
            '/post/' + (str(data['title']).replace(' ', '-')).replace('?', '') + '-' + str(index) + '?notification_id='+str(not_id),
            user,
            None,
            None,
            'post'
        )
        send_notification(user, {
            'text': '@{} shared a new post'.format(currentUser.name),
            'link': '/post/' + (str(data['title']).replace(' ', '-')).replace('?', '') + '-' + str(index),
            'icon': currentUser.avatar,
            'id': int(not_id)
        })
        db.session.add(notification)
    db.session.add(new_post)
    db.session.commit()

    return make_response(jsonify(
                            {
                                'operation': 'success',
                                'link': '/post/' + (str(data['title']).replace(' ', '-')).replace('?','') + '-' + str(index)
                            }
                        ), 200)

@post.route('/delete/<int:id>')
@AuthRequired
def delete(id, *args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first()
    post = PostModel.query.filter_by(id=id).first()

    if currentUser.id != post.user_in.id and currentUser.roleinfo.delete_post_permission == False:
        return make_response(jsonify({'operation': 'failed'}), 401)

    if post.thumbnail:
        try:
            picture_fn = 'post_' + str(id) + '.webp'
            os.remove(os.path.join(
                config['UPLOAD_FOLDER_POST'], picture_fn))
        except:
            pass

    PostModel.query.filter_by(id=id).delete()
    ReplyModel.query.filter_by(post_id=id).delete()
    tags = TagModel.query.filter(
        TagModel.post.contains([id])).all()
    for t in tags:
        x = list(t.post)
        x.remove(id)
        t.post = x

    db.session.commit()
    return make_response(jsonify({'operation': 'success'}), 200)

@post.route('/close/<int:id>')
@AuthRequired
def close(id, *args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first()
    post = PostModel.query.filter_by(id=id).first()

    if not currentUser.roleinfo.close_post_permission:
        return make_response(jsonify({'operation': 'failed'}), 401)

    post.closed = True
    post.closed_on = dt.datetime.now()
    post.closed_by = currentUser.id
    db.session.commit()

    return make_response(jsonify({'operation': 'success'}), 200)


@post.route("/edit/<int:id>", methods=['GET', 'POST'])
@AuthRequired
def edit(id, *args, **kwargs):
    post = PostModel.query.filter_by(id=id).first()

    if request.method == 'POST':
        data = request.json
        post.text = data['text']
        post.title = data['title']
        post_link = (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id)
        db.session.commit()

        return make_response(jsonify({'operation': 'success', 'link': post_link}), 200)

    post_json = {}
    post_json['title'] = post.title
    post_json['text'] = post.text
    post_json['id'] = post.id

    return make_response(jsonify(post_json), 200)


@post.route("/like/<int:id>")
@AuthRequired
def like(id, *args, **kwargs):
    user = UserModel.query.filter_by(id=kwargs['token']['id']).first()

    like = list(user.liked_posts)
    post = PostModel.query.filter_by(id=id).first()
    not_id = str(db.session.execute(Sequence('notifications_id_seq')))

    if like is not None:
        if id in like:
            like.remove(id)
            response = jsonify({'operation': 'unliked'})
            post.likes = post.likes - 1
            notify = Notifications_Model(
                int(not_id),
                user.id,
                '{} unliked your post'.format(user.name),
                post.title,
                '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
                    post.id) + '?notification_id=' + not_id,
                post.user_in.id,
                False,
                None,
                'unlike'
            )
            send_notification(post.user_in.id, {
                'text': '@{} unliked your post'.format(user.name),
                'link': '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
                'icon': user.avatar,
                'id': not_id
            })

            not_check = Notifications_Model.query.filter_by(
                title='{} unliked your post'.format(user.name)).filter_by(body=str(post.title)).first()
        else:
            response = jsonify({'operation': 'liked'})
            post.likes = post.likes + 1
            like.append(id)
            notify = Notifications_Model(
                int(not_id),
                user.id,
                '{} liked your post'.format(user.name),
                post.title,
                '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
                    post.id) + '?notification_id=' + not_id,
                post.user_in.id,
                False,
                None,
                'like'
            )
            send_notification(post.user_in.id, {
                'text': '@{} liked your post'.format(user.name),
                'link': '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
                'icon': user.avatar,
                'id': not_id
            })
            not_check = Notifications_Model.query.filter_by(
                title='{} liked your post'.format(user.name)).filter_by(body=post.title).first()
    else:
        response = jsonify({'operation': 'liked'})
        post.likes = post.likes + 1
        like.append(id)
        notify = Notifications_Model(
            int(not_id),
            user.id,
            '{} liked your post'.format(user.name),
            post.title,
            '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
                post.id) + '?notification_id=' + not_id,
            post.user_in.id,
            False,
            None,
            'like'
        )
        send_notification(post.user_in.id, {
            'text': '@{} liked your post'.format(user.name),
            'link': '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
            'icon': user.avatar,
            'id': not_id
        })
        not_check = Notifications_Model.query.filter_by(
            title='{} liked your post'.format(user.name)).filter_by(body=post.title).first()

    socket.emit("notification", room="notification-{}".format(post.user_in.id))

    if not_check is not None:
        not_check.checked = False
    else:
        db.session.add(notify)

    user.liked_posts = like
    db.session.commit()

    return make_response(response, 200)

@post.route("/save/<int:id>")
@AuthRequired
def save(id, *args, **kwargs):
    user = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()

    posts = list(user.saved_posts)

    if posts is not None:
        if id in posts:
            posts.remove(id)
            response = jsonify({'operation': 'deleted'})
        else:
            response = jsonify({'operation': 'saved'})
            posts.append(id)
    else:
        response = jsonify({'operation': 'saved'})
        posts.append(id)

    user.saved_posts = posts
    db.session.commit()

    return make_response(response, 200)
