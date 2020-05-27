from app import socket, make_response, jsonify, join_room, leave_room, jwt, time, key_c, db
from models import UserModel, ConversationModel, ConversationsModel

@socket.on('access')
def access(token):
    if not token:
        return make_response(jsonify({'operation': 'failed'}), 401)

    try:
        token = token['data']
        user_t = jwt.decode(token, key_c)
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
        user_t = jwt.decode(token, key_c)
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
    message = {
        'text': data['text'],
        'author': data['author'],
        'room': data['room'],
        'id': data['id'],
        'created_on': str(time.datetime.now())
    }
    new_message = ConversationsModel(
        id = None,
        message = data['text'],
        user = data['author']['id'],
        created_on = None,
        conversation_id = data['id']
    )
    db.session.add(new_message)
    db.session.commit()
    socket.emit("get_message", message, room=data['room'])

@socket.on('connect')
def on_connect():
    print('my response', {'data': 'Connected'})


@socket.on('disconnect')
def on_disconnect():
    print('my response', {'data': 'Disconnected'})