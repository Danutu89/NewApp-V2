import localStorage from './localStorage.js';
const currentChat = localStorage('chat',{
    id: null,
    last_message: {on: "", seen: true, text: ""},
    on: "",
    seen: true,
    text: "",
    members: [],
    room: ""
});

export default currentChat;