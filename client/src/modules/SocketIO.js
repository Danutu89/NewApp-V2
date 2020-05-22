import {sockets} from './Options.js';
const socketio = require('socket.io-client');

export const socket = socketio.connect(sockets,{transports: ['websocket','polling']});
