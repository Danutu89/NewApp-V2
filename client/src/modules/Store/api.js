import { writable } from 'svelte/store'
import axios from 'axios'

const api = writable({
	'auth.check_email': '/api/v2/users/auth/register/check/email/',
	'auth.check_username': '/api/v2/users/auth/register/check/username/',
	'auth.confirm': '/api/v2/users/auth/register/confirm',
	'auth.login': '/api/v2/users/auth/login',
	'auth.register': '/api/v2/users/auth/register',
	'direct.chat': '/api/v2/users/direct/',
	'direct.index': '/api/v2/users/direct/',
	'follow.tag': '/api/v2/follow/tag/',
	'follow.user': '/api/v2/follow/user/',
	getApi: '/api/v2',
	'home.index': '/api/v2/home/',
	'notifications.check': '/api/v2/users/notifications/check/',
	'notifications.index': '/api/v2/users/notifications/',
	'notifications.subscribe': '/api/v2/users/notifications/subscribe',
	'post.close': '/api/v2/post/close/',
	'post.delete': '/api/v2/post/delete/',
	'post.edit': '/api/v2/post/edit/',
	'post.index': '/api/v2/post/',
	'post.like': '/api/v2/post/like/',
	'post.new': '/api/v2/post/new',
	'post.save': '/api/v2/post/save/',
	'replies.delete': '/api/v2/replies/delete/',
	'replies.edit': '/api/v2/replies/edit',
	'replies.new': '/api/v2/replies/new',
	static: '/static/',
	'users.images': '/static/users/',
	'users.settings': '/api/v2/users/settings/',
	'users.user': '/api/v2/users/',
	'users.users_list': '/api/v2/users/',
	'analytics.view': '/api/v2/analytics/view',
})

async function setApiUrls() {
	var apiUrls = await axios.get('/api/v2').then((res) => {
		return res.data
	})
	//api.set(apiUrls);
	return
}

const currentApi = writable(null)

export { api, setApiUrls, currentApi }

export default {
	api,
	setApiUrls,
	currentApi,
}
