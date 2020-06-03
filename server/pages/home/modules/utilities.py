from functools import wraps
from flask import request, make_response, jsonify
import jwt
from app import config
import datetime as dt
from sqlalchemy import desc, func, or_, asc

from models import Analyze_Pages, TagModel, PostModel

def AuthRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.headers['Token']
            decoded = jwt.decode(token_header, config['JWT_KEY'])
            kwargs['token'] = decoded
        except Exception as e:
            make_response(jsonify({'auth': 'Invalid token.'}), 401)
        return f(*args, **kwargs)
    return decorated


def AuthOptional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token_header = request.headers['Token']
            decoded = jwt.decode(token_header, config['JWT_KEY'])
            kwargs['token'] = decoded
            kwargs['auth'] = True
        except Exception as e:
            kwargs['auth'] = False
        return f(*args, **kwargs)
    return decorated



def GetTrending():
    now = dt.datetime.now()
    back_days = now - dt.timedelta(days=2)

    posts = PostModel.query.order_by(
        desc(PostModel.posted_on)).filter_by(approved=True).all()
    analyses = Analyze_Pages.query.filter(
        Analyze_Pages.first_visited.between('{}-{}-{}'.format(back_days.year, back_days.month, back_days.day),
                                            '{}-{}-{}'.format(now.year, now.month, now.day))).all()

    trending_list = []
    today_date = dt.date.today()
    for post in posts:
        published_on = post.posted_on

        day_1 = 0
        day_0 = 0

        for analyze in analyses:
            if analyze.name == '/post/{post.title}/id={post.id}':
                if (today_date - analyze.first_visited).days < 2:
                    day_1 += analyze.visits
                if (today_date - analyze.first_visited).days < 1:
                    day_0 += analyze.visits

        total = (day_1 + day_0) / 2
        temp = {
            'trending_value': total,
            'id': post.id,
            'title': post.title,
            'link': (str(post.title).replace(' ', '-')).replace('?', '') + '-' + str(post.id),
            'author': {
                'id': post.user_in.id,
                'name': post.user_in.name,
                'avatar': post.user_in.avatar
            },
            'tags': TagModel.query.with_entities(TagModel.name).filter(TagModel.post.contains([post.id])).all()
        }
        trending_list.append(temp.copy())
        day_1 = 0
        day_0 = 0

    trending_list.sort(key=getItemForKey, reverse=True)

    return trending_list[0:6]

def getItemForKey(value):
    return value['trending_value']