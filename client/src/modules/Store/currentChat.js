import {writable} from 'svelte/store';
const currentChat = writable({
    id: null,
    last_message: {on: "", seen: true, text: ""},
    on: "",
    seen: true,
    text: "",
    members: [],
    room: ""
});

export default currentChat;