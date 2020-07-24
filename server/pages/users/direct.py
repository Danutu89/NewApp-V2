from flask import Blueprint, make_response, jsonify, request
from modules import AuthRequired
from sqlalchemy import desc, func, or_, asc, and_
import datetime as dt

from models import User, Conversations, Conversation

direct = Blueprint('direct', __name__, url_prefix='/api/v2/users/direct')

@direct.route("/", methods=['GET', 'POST'])
@AuthRequired
def index(*args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first()

    current_conv = {}

    if request.method == 'POST':
        
        data = request.json

        if not data:
            return make_response(jsonify({'operation': 'error', 'error': 'Missing data'}), 401)


        users = User.get().with_entities(User.id).filter(User.name.in_(data['users'])).all()
        users = list(sum(users, ()))

        user_chats = Conversations.get().with_entities(Conversations.id).filter(Conversations.members.contains(users)).all()
        user_chats = list(sum(user_chats, ()))

        currentUser_chats = Conversations.get().with_entities(Conversations.id).filter(Conversations.members.contains(users)).all()

        currentUser_chats = set(sum(currentUser_chats, ()))
        
        currentUser_chats.intersection(user_chats)
        currentUser_chats = list(currentUser_chats)

        if len(currentUser_chats) > 0:
            conv = Conversations.get().filter(Conversations.id.in_(currentUser_chats)).first()
        else:
            users.append(currentUser.id)

            conv = Conversations(
                members = users,
                seen = True
            )

            conv.add()

        members = [x for i,x in enumerate(conv.members) if x!=currentUser.id]
        users = User.get().filter(User.id.in_(members)).all()
        members_json = []
        last_text = ""

        for m in users:
            members_json.append({
                'name': m.name,
                'real_name': m.info.getFullName(),
                'avatar': m.info.avatar_img,
            })

        if len(conv.chat) > 0:
            last_text = conv.chat[0].message

        current_conv = {
            'room': 'direct-'+str(conv.id),
            'id': conv.id,
            'members': members_json,
            'last_message': {
                'on': conv.chat[0].created_on if len(conv.chat) > 0 else None,
                'text': last_text,
                'seen': conv.seen
            }
        }

    conv_json = {'conversations': [], 'current': current_conv.copy()}

    conv = Conversations.get().filter(Conversations.members.contains([currentUser.id])).all()

    for c in conv:

        members = [x for i,x in enumerate(c.members) if x!=currentUser.id]
        users = User.get().filter(User.id.in_(members)).all()
        members_json = []
        last_text = ""

        for m in users:
            members_json.append({
                'name': m.name,
                'real_name': m.info.getFullName(),
                'avatar': m.info.avatar_img,
            })

        if len(c.chat) > 0:
            last_text = c.chat[0].message

        conv_json['conversations'].append({
            'room': 'direct-'+str(c.id),
            'id': c.id,
            'members': members_json,
            'last_message': {
                'on': c.chat[0].created_on  if len(c.chat) > 0 else None,
                'text': last_text,
                'seen': c.seen
            }
        })


    return make_response(jsonify(conv_json), 200)


@direct.route("/<int:id>", methods=['GET', 'POST'])
@AuthRequired
def chat(id, *args, **kwargs):
    currentUser = User.get().filter_by(name=kwargs['token']['name']).first()

    if request.method == 'GET':
        messages = Conversation.get().filter_by(conversation_id=id).order_by(asc(Conversation.id)).all()

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
                    'realname': m.author.info.getFullName(),
                    'avatar': m.author.info.avatar_img
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

        
        new_message = Conversation(
            message = data['text'],
            user_id = currentUser.id,
            conversation_id = id
        )

        new_message.add()

        return make_response(jsonify({'operation': 'success'}), 200)
        