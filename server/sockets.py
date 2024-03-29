from app import socket, make_response, jsonify, jwt, time, config, db
from models import User, Conversation, Conversations
import time as time_
import datetime as dt
from flask_socketio import join_room, leave_room

@socket.on('access')
def access(token):
    if not token:
        return make_response(jsonify({'operation': 'failed'}), 401)

    try:
        token = token['data']
        user_t = jwt.decode(token, config.get('JWT_KEY'))
    except:
        return make_response(jsonify({'operation': 'failed'}), 401)

    join_room('notification-{}'.format(user_t['id']))
    user = UserModel.query.filter_by(id=user_t['id']).first()
    user.status = 'Online'
    user.status_color = '#00c413'
    db.session.commit()

@socket.on('logout')
def logout(token):
    if not token:
        return make_response(jsonify({'operation': 'failed'}), 401)

    try:
        token = token['data']
        user_t = jwt.decode(token, config.get('JWT_KEY'))
    except:
        return make_response(jsonify({'operation': 'failed'}), 401)

    leave_room('notification-{}'.format(user_t['id']))
    user = UserModel.query.filter_by(id=user_t['id']).first()
    user.status = 'Offline'
    user.status_color = '#cc1616'
    db.session.commit()

@socket.on('join')
def join(data):
    join_room(data['room'])
    socket.send("joined", room=data['room'])

@socket.on('send_message')
def message(data):
    try:
        last_date = time.datetime.strptime(data['last_date'], '%a, %d %b %Y %H:%M:%S %Z')
    except:
        last_date = time.datetime.now()

    if (time.datetime.now() - last_date).days >= 1:
        new_day_from_last = True
    else:
        new_day_from_last = False

    if time.datetime.now().date() == last_date.date():
        new_day = False
    else:
        new_day = True

    message = {
        'text': data['text'],
        'author': data['author'],
        'room': data['room'],
        'id': data['id'],
        'at': time.datetime.now().strftime("%H:%M"),
        'on': time.datetime.now().strftime("%A %d %b"),
        'datetime': str(time.datetime.now()),
        'new_day_from_last': new_day_from_last,
        'new_day': new_day
    }

    user = UserModel.query.filter_by(name=data['author']['name']).first()
    new_message = ConversationsModel(
        id = None,
        message = data['text'],
        user = user.id,
        created_on = None,
        conversation_id = data['id']
    )
    new_message.add()
    socket.emit("get_message", message, room=data['room'])

@socket.on('connect')
def on_connect():
    print('my response', {'data': 'Connected'})


@socket.on('disconnect')
def on_disconnect():
    print('my response', {'data': 'Disconnected'})