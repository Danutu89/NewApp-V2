import localStorage from './localStorage.js'
import user from './user.js'
import { api, currentApi } from './api.js'
import { token, setToken } from './token.js'
import currentChat from './currentChat.js'
import deviceType from './deviceType.js'
import { get } from 'svelte/store'

export default {
	localStorage,
	user,
	api,
	currentApi,
	currentChat,
	deviceType,
	get,
	token,
	setToken,
}

export {
	localStorage,
	user,
	api,
	currentApi,
	currentChat,
	deviceType,
	get,
	token,
	setToken,
}
