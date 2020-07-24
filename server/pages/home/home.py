from flask import Blueprint, make_response, jsonify, request
from modules import AuthOptional, AuthRequired
from sqlalchemy import desc, func, or_, asc
import datetime as dt

from models import User, Post, Post_Tag, Post_Tags, Saved_Posts, User_Tags, \
    User_Following

from .modules.serializer import PostsSchema, PostTagsOnlySchema

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

    currentUser = None

    if search:
        query = Post.find(search)
    else:
        query = Post.get()

    if kwargs['auth']:
        currentUser = User.get().filter_by(name=kwargs['token']['name']).first_or_404()
        query = query.filter_by(approved=True)\
                    .filter(or_(Post.language_id == currentUser.language_id, Post.language_id == 1))
    else:
        query = query.filter_by(approved=True)
    
    if tag:
        tagQuery = Post_Tag.get().filter_by(name=tag).first_or_404()
        tags = Post_Tags.get().with_entities(Post_Tags.post).filter_by(tag_id=tagQuery.id).all()
        tags = list(tuple(tags))
        query = query.filter(Post.id.in_(tags))
    elif mode == 'saved':
        if kwargs['auth'] == False:
            return make_response(jsonify({'auth': 'Invalid token.'}), 401)
        saved = Saved_Posts.get().with_entities(Saved_Posts.post).filter_by(user=currentUser.id).all()
        saved = list(tuple(saved))
        query = query.filter(Post.id.in_(saved))

    elif mode == 'recent':
        pass
    elif mode == 'discuss' or mode == 'questions' or mode == 'tutorials':
        if mode == 'discuss':
            tags = ['discuss', 'talk']
        elif mode == 'tutorials':
            tags = ['tutorial', 'howto', 'tutorials', 'how_to']
        elif mode == 'questions':
            tags = ['help', 'question']

        tgs = Post_Tag.get().with_entities(Post_Tag.id).filter(Post_Tag.name.in_(tags)).all()
        tagsQuery = Post_Tags.get().with_entities(Post_Tags.post).filter(Post_Tags.tag_id.in_(tgs)).all()
        tagsQuery = list(tuple(tagsQuery))
        query = query.filter(Post.id.in_(tagsQuery))
    elif user:
        query = query.filter_by(user=user)
    else:
        if kwargs['auth']:
            if len(currentUser.tags) > 0:
                user_tags = User_Tags.get().with_entities(User_Tags.tag_id).filter_by(user=currentUser.id).all()
                tagsQuery = Post_Tags.get().with_entities(Post_Tags.post).filter(Post_Tags.tag_id.in_(user_tags)).all()
                tagsQuery = list(tuple(tagsQuery))

                if len(currentUser.following) > 0:
                    following = User_Following.get().with_entities(User_Following.followed).filter_by(user=currentUser.id).all()
                    following = [f[0] for f in following]
                    query = query.filter(or_(Post.id.in_(tagsQuery), Post.author_id.in_(following)))
                else:
                    query = query.filter(Post.id.in_(tagsQuery))
            else:
                if len(currentUser.following) > 0:
                    following = User_Following.get().with_entities(User_Following.followed).filter_by(user=currentUser.id).all()
                    query = query.filter(Post.author.in_(following))
    
    posts = query.order_by(desc(Post.created_on)).paginate(page=page,per_page=9)

    tagsQuery = Post_Tag.get()

    if kwargs['auth']:
        user_tags = User_Tags.get().filter_by(user=currentUser.id).all()
        user_tags = [tag.tag_id for tag in user_tags]
        tagsQuery = tagsQuery.filter(~Post_Tag.id.in_(user_tags))
        PostsSchema.context['currentUser'] = currentUser
        user_tags = User_Tags.get().with_entities(User_Tags.tag_id).filter_by(user=currentUser.id).all()
        tags_following = Post_Tag.get().filter(Post_Tag.id.in_(user_tags)).all()

    tags = tagsQuery.order_by(desc(Post_Tag.count)).limit(10).all()

    if user or page > 1:
        home_json = {
            'posts': {
                'list': PostsSchema.dump(posts.items),
                'hasnext': True if posts.has_next else False
            }
        }
    else:
        home_json = {
            'posts': {
                'list': PostsSchema.dump(posts.items),
                'hasnext': True if posts.has_next else False
            },
            'trending': [],
            'utilities': {
                    'tags': PostTagsOnlySchema.dump(tags),
                    'search': search if search else None
                }
            ,'user': {
                'flw_tags': PostTagsOnlySchema.dump(tags_following) if kwargs['auth'] else None
            },
        }

    return make_response(jsonify(home_json), 200)
