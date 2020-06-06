import {instance} from '../../../modules/Requests.js';
import {get, currentChat, user as User, api as Api} from '../../../modules/Store';
import {socket} from '../../../modules/SocketIO.js';

async function loadChat(){
    const res = await instance.get(get(Api)['direct.chat']+get(currentChat).id);
    const json = await res.data;
    socket.emit("join", {
        room: get(currentChat).room
    });
    return json;
    
}

async function SendMessage(messages, text){

    socket.emit("send_message", {
        token: get(User).token,
        text: text,
        author: {
            avatar: get(User).avatar,
            name: get(User).name,
            realname: get(User).real_name
        },
        room: get(currentChat).room,
        id: get(currentChat).id,
        last_date: messages.length > 0 ? messages[messages.length -1].datetime : null
    })
}

export default {
    loadChat,
    SendMessage
}

export {
    loadChat,
    SendMessage
}