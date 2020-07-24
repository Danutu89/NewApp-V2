from flask import Blueprint, make_response, jsonify, request, url_for

from sqlalchemy import desc, func, or_, asc, and_
import datetime as dt
import json
from sqlalchemy.schema import Sequence
from app import db, translate, socket, config
import readtime
from webpush import send_notification
import os

from models import Post, Post_Likes, Post_Tags, Post_Tag, User_Following, User, Post_Info, \
    Notification, Languages, Saved_Posts

from .modules.utilities import SaveImage, cleanhtml
from modules import AuthOptional, AuthRequired
from .modules.serializer import PostSchemaOnly, NewPostSchema, NewPostInfoSchema, NewPostTagsSchema

post = Blueprint('post', __name__, url_prefix='/api/v2/post')

@post.route("/<int:id>")
@AuthOptional
def index(id, *args, **kwargs):
    post = Post.get().filter_by(id=id).first_or_404()
    currentUser = None

    if kwargs['auth']:
        currentUser = User.get().filter_by(name=kwargs['token']['name']).first()

    PostSchemaOnly.context['currentUser'] = currentUser

    return make_response(PostSchemaOnly.dump(post), 200)

@post.route("/new", methods=['POST'])
@AuthRequired
def new(*args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()

    if not currentUser.role.permissions.add_post:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing permissions'}), 401)

    if not request.form['data']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)
        
    data = json.loads(str(request.form['data']))

    if not data['title'] or not data['content'] or not data['tags']:
        return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

    index = str(db.session.execute(Sequence('post_id_seq')))
    thumbnail_link = None
    if data['image']:
        thumbnail = SaveImage(index)
        thumbnail_link = url_for('static', filename='thumbail_post/{}'.format(thumbnail))
    else:
        thumbnail_link = 'none'

    lang = translate.getLanguageForText(str(cleanhtml(data['content'])).encode('utf-8-sig'))

    langQuery = Languages.get().filter_by(code=lang.iso_tag).first()

    if langQuery is None:
        new_lang = Languages(name=lang.language, code=lang.iso_tag)
        new_lang.add()
        langQuery = new_lang

    tags_ids = []
    tags = []

    for tag in data['tags']:
        check = Post_Tag.get().filter_by(name=tag).first()

        if check is None:
            new_tag = Post_Tag(name=tag, count=1)
            new_tag.add()
            check = new_tag
        else:
            setattr(check, 'count', Post_Tag.count + 1)
            check.save()

        tags_ids.append(check.id)

    for tag_id in tags_ids:
        tags.append({"post": index, "tag_id": tag_id})

    nPost = NewPostSchema().load(
        {   
            "id": int(index),
            "title": data['title'], 
            "read_time": str(readtime.of_html(data['content'])),
            "author_id": currentUser.id, 
            "language_id": langQuery.id, 
            "info": {
                "thumbnail": thumbnail_link, 
                "text": data['content'],
                "tags": tags
                },
            "link": '/post/' + (str(data['title']).replace(' ', '-')).replace('?','') + '-' + str(index)
        }
    )

    nPost.add()

    for user in currentUser.followed:
        not_id = str(db.session.execute(Sequence('notification_id_seq')))
        notification = Notification(
            id=int(not_id),
            author=currentUser.id,
            user=user.user,
            type=5,
            title=nPost.title,
            body='{} shared a new post'.format(currentUser.name),
            link= nPost.link + '?notification_id='+str(not_id)
        )
        send_notification(user.user, {
            'text': '{} shared a new post'.format(currentUser.name),
            'link':  nPost.link + '?notification_id='+str(not_id),
            'icon': currentUser.info.avatar_img,
            'id': int(not_id)
        })
        notification.add()

    return make_response(jsonify({'operation': 'success','link': nPost.link}), 200)

@post.route('/delete/<int:id>')
@AuthRequired
def delete(id, *args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first()
    post = Post.get().filter_by(id=id).first()

    if not post:
        return make_response(jsonify({'operation': 'failed'}), 401)

    if currentUser.id != post.author.id or currentUser.role.permissions.delete_post == False:
        return make_response(jsonify({'operation': 'failed'}), 401)

    if post.info.thumbnail:
        try:
            picture_fn = 'post_' + str(id) + '.webp'
            os.remove(os.path.join(
                config['UPLOAD_FOLDER_POST'], picture_fn))
        except:
            pass

    for post_tag in post.info.tags:
        tagQuery = Post_Tag.get().filter_by(name=post_tag.tag.name).first()
        setattr(tagQuery, 'count', Post_Tag.count - 1)
        tagQuery.save()

    post.delete()
    return make_response(jsonify({'operation': 'success'}), 200)

@post.route('/close/<int:id>')
@AuthRequired
def close(id, *args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first()
    post = Post.get().filter_by(id=id).first()

    if currentUser.id != post.author.id or currentUser.role.permissions.close_post == False:
        return make_response(jsonify({'operation': 'failed'}), 401)

    post.info.closed = True
    post.info.closed_on = dt.datetime.now()
    post.info.closed_by = currentUser.id
    post.save()

    return make_response(jsonify({'operation': 'success'}), 200)


@post.route("/edit/<int:id>", methods=['GET', 'POST'])
@AuthRequired
def edit(id, *args, **kwargs):
    post = Post.get().filter_by(id=id).first()
    

    if request.method == 'POST':
        data = request.json
        post.info.text = str(data['text'])
        post.title = data['title']
        post_link = (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id)
        post.save()

        return make_response(jsonify({'operation': 'success', 'link': post_link}), 200)

    post_json = {}
    post_json['title'] = post.title
    post_json['text'] = post.info.text
    post_json['id'] = post.id

    return make_response(jsonify(post_json), 200)


@post.route("/like/<int:id>")
@AuthRequired
def like(id, *args, **kwargs):
    currentUser = User.get().filter_by(id=kwargs['token']['id']).first()

    post = Post.get().filter_by(id=id).first()
    like = Post_Likes.get().filter(and_(Post_Likes.author==currentUser.id,Post_Likes.post==post.id)).first()
    
    not_id = str(db.session.execute(Sequence('notification_id_seq')))

    if like is not None:
        response = jsonify({'operation': 'disliked'})
        like.delete()
        body='unliked your post'
    else:
        response = jsonify({'operation': 'liked'})
        new_like = Post_Likes(
            post=post.id,
            author=currentUser.id
        )
        new_like.add()
        body='liked your post'

    not_check = Notification.get().filter_by(
        title=currentUser.name + ' ' + body).filter_by(body=post.title).first()

    if not_check is None:
        notify = Notification(
            id=int(not_id),
            author=currentUser.id,
            user=post.author.id,
            type=2,
            title=post.title,
            body=currentUser.name + ' ' + body,
            link='/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(
                post.id) + '?notification_id=' + not_id
        )
        notify.add()
    else:
        not_check.checked = False
        not_check.save()
        
    if post.author.status != 2:
        send_notification(post.author.id, {
            'text': currentUser.name + ' ' + body,
            'link': '/post/' + (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
            'icon': currentUser.info.avatar_img,
            'id': not_id
        })


    socket.emit("notification", room="notification-{}".format(post.author.id))

    return make_response(response, 200)

@post.route("/save/<int:id>")
@AuthRequired
def save(id, *args, **kwargs):
    currentUser = User.get().filter_by(id=kwargs['token']['id']).first_or_404()

    saved = Saved_Posts.get().filter(and_(Saved_Posts.user==currentUser.id,Saved_Posts.post==id)).first()

    if saved is not None:
        saved.delete()
        response = jsonify({'operation': 'deleted'})
    else:
        new_saved = Saved_Posts(
            user=currentUser.id,
            post=id
        )
        new_saved.add()
        response = jsonify({'operation': 'saved'})

    return make_response(response, 200)
