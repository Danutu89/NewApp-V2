from flask import Blueprint, make_response, jsonify, request
from .modules.utilities import AuthOptional, AuthRequired, GetTrending
from sqlalchemy import desc, func, or_, asc
import datetime as dt

from models import TagModel, Analyze_Pages, PostModel, UserModel

home = Blueprint('home', __name__, url_prefix='/api/v2/home')

@home.route("/", methods=['GET'])
@AuthOptional
def index(*args, **kwargs):

    page = request.args.get('page')
    if not page:
        page = 1
    else:
        page = int(page)

    tag = request.args.get('tag')
    if tag:
        tag = str(request.args.get('tag')).replace(' ', '+')

    mode = request.args.get('mode')
    search = request.args.get('search')
    user = request.args.get('user')

    if kwargs['auth']:
        currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first_or_404()
        query = PostModel.query.filter_by(approved=True)\
                    .filter(or_(PostModel.lang.like(currentUser.lang), PostModel.lang.like('en')))
    else:
        query = PostModel.query.filter_by(approved=True)

    if tag:
        tag_posts = TagModel.query.filter_by(name=tag).first_or_404()
        query = query.filter(PostModel.id.in_(tag_posts.post))
    elif mode == 'saved':
        if kwargs['auth'] == False:
            make_response(jsonify({'auth': 'Invalid token.'}), 401)
        query = query.filter(PostModel.id.in_(currentUser.saved_posts))
    elif mode == 'recent':
        query = query
    elif mode == 'discuss' or mode == 'questions' or mode == 'tutorials':
        if mode == 'discuss':
            tg = TagModel.query.filter(TagModel.name.in_(['discuss', 'talk'])).order_by(
                desc(func.array_length(TagModel.post, 1))).all()
        elif mode == 'tutorials':
            tg = TagModel.query.filter(TagModel.name.in_(['tutorial', 'howto', 'tutorials', 'how_to'])).order_by(
                desc(func.array_length(TagModel.post, 1))).all()
        elif mode == 'questions':
            tg = TagModel.query.filter(TagModel.name.in_(['help', 'question'])).order_by(
                desc(func.array_length(TagModel.post, 1))).all()
        
        tgi = []
        for t in tg:
            tgi.extend(t.post)

        query = query.filter(PostModel.id.in_(tgi))
    elif search:
        query = query.whoosh_search(search)
    elif user:
        query = query.filter_by(user=user)
    else:
        if kwargs['auth']:
            if len(currentUser.int_tags) > 0:
                tg = TagModel.query.filter(TagModel.name.in_(currentUser.int_tags)).order_by(
                    desc(func.array_length(TagModel.post, 1))).all()
                tgi = []
                for t in tg:
                    tgi.extend(t.post)
                if len(currentUser.follow) > 0:
                    query = query.filter(or_(PostModel.id.in_(tgi), PostModel.user.in_(currentUser.follow)))
                else:
                    query = query.filter(PostModel.id.in_(tgi))
            else:
                if len(currentUser.follow) > 0:
                    query = query.filter(PostModel.user.in_(currentUser.follow))
    
    posts = query.order_by(desc(PostModel.posted_on)).paginate(page=page,per_page=9)

    tagsQuery = TagModel.query.with_entities(TagModel.name)

    if kwargs['auth']:
        tagsQuery = tagsQuery.filter(~TagModel.name.in_(currentUser.int_tags))

    tags = tagsQuery.order_by(desc(func.array_length(TagModel.post, 1))).limit(10).all()

    posts_list = []
    posts_json = {}
    for post in posts.items:
        posts_json['title'] = post.title
        posts_json['id'] = post.id
        posts_json['thumbnail'] = post.thumbnail
        posts_json['posted_on'] = post.time_ago()
        posts_json['author'] = {
            'name': post.user_in.name,
            'avatar': post.user_in.avatar,
            'real_name': post.user_in.real_name
        }
        posts_json['likes'] = post.likes
        posts_json['read_time'] = post.read_time
        posts_json['link'] = (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id)
        posts_json['tags'] = TagModel.query.with_entities(TagModel.name).filter(TagModel.post.contains([post.id])).all()
        if kwargs['auth']:
            if post.id in currentUser.saved_posts:
                posts_json['saved'] = True
            else:
                posts_json['saved'] = False

        posts_list.append(posts_json.copy())
        posts_json.clear()


    if user or page > 1:
        home_json = {
            'posts': {
                'list': posts_list,
                'hasnext': True if posts.has_next else False
            }
        }
    else:
        home_json = {
            'posts': {
                'list': posts_list,
                'hasnext': True if posts.has_next else False
            },
            'trending': GetTrending(),
            'utilities': {
                    'tags': tags,
                    'search': search if search else None
                }
            ,'user': {
                'flw_tags': currentUser.int_tags if kwargs['auth'] else None
            },
        }

    return make_response(jsonify(home_json), 200)
