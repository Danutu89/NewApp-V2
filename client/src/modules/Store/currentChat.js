import { writable } from 'svelte/store';
const currentChat = writable(null);

export default currentChat;