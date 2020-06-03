from flask import Blueprint, make_response, jsonify, request
from .modules.utilities import AuthOptional, AuthRequired, GetItemForKeyN
from sqlalchemy import desc, func, or_, asc
from sqlalchemy.schema import Sequence
import datetime as dt
from app import db, socket
from webpush import send_notification

from models import ConversationModel, ConversationsModel, Notifications_Model, PostModel, UserModel

direct = Blueprint('direct', __name__, url_prefix='/api/v2/users/direct')

@direct.route("/", methods=['GET', 'POST'])
@AuthRequired
def index(*args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first()

    if request.method == 'GET':

        conv = ConversationModel.query.filter(ConversationModel.members.contains([currentUser.id])).all()

        conv_json = {'conversations': []}

        for c in conv:

            members = [x for i,x in enumerate(c.members) if x!=currentUser.id]
            users = UserModel.query.filter(UserModel.id.in_(members)).all()
            members_json = []
            last_text = ""

            for m in users:
                members_json.append({
                    'name': m.name,
                    'real_name': m.real_name,
                    'avatar': m.avatar,
                })

            if c.last_message is not None:
                last_text = c.last_message.message

            conv_json['conversations'].append({
                'room': 'direct-'+str(c.id),
                'id': c.id,
                'members': members_json,
                'last_message': {
                    'on': c.last_message_on,
                    'text': last_text,
                    'seen': c.seen
                }
            })

        return make_response(jsonify(conv_json), 200)

    if request.method == 'POST':
        
        data = request.json

        if not data:
            return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)


        users = UserModel.query.with_entities(UserModel.id).filter(UserModel.name.in_(data['users'])).all()
        users = list(sum(users, ())) 
        users.append(currentUser.id)

        new_conv = ConversationModel(
            id = None,
            members = users,
            seen = True,
            last_message_on = None,
            last_message_id = None
        )

        db.session.add(new_conv)
        db.session.commit()

        return make_response(jsonify({'operation': 'success'}), 200)


@direct.route("/chat/<int:id>")
@AuthRequired
def chat(id, *args, **kwargs):
    currentUser = UserModel.query.filter_by(id=kwargs['token']['id']).first()

    if request.method == 'GET':
        messages = ConversationsModel.query.filter_by(conversation_id=id).order_by(asc(ConversationsModel.id)).all()

        messages_json = []
        last_date = None

        for index,m in enumerate(messages, start=0):
            if m.author.id == currentUser.id:
                mine = True
            else:
                mine = False
            
            if last_date is None:
                last_date = messages[index].created_on
            else:
                last_date = messages[index-1].created_on

            if (m.created_on - last_date).days >= 1:
                new_day_from_last = True
            else:
                new_day_from_last = False


            if m.created_on.date() == last_date.date():
                new_day = False
            else:
                new_day = True

            messages_json.append({
                'text': m.message,
                'on': m.date_sent(),
                'at': m.when_sent(),
                'datetime': m.created_on,
                'author': {
                    'name': m.author.name,
                    'realname': m.author.real_name,
                    'avatar': m.author.avatar
                },
                'mine': mine,
                'new_day_from_last': new_day_from_last,
                'new_day': new_day
            })

        return make_response(jsonify(messages_json), 200)
    
    if request.method == 'POST':
        data = request.json

        if not data:
            return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)

        
        new_message = ConversationsModel(
            id = None,
            message = data['text'],
            user = currentUser.id,
            created_on = None,
            conversation_id = id
        )

        db.session.add(new_message)
        db.session.commit()

        return make_response(jsonify({'operation': 'success'}), 200)
        