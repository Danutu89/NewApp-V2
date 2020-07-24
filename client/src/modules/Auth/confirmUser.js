import { instance } from '../Requests.js'
import { activateAlert } from '../Alert.js'
import jwtdecode from 'jwt-decode'
import { user as User, api as Api, get } from '../Store'
import Cookie from 'cookie-universal'
const cookies = Cookie()

export default function confirmUser(data) {
	var user = instance.post(get(Api)['auth.confirm'], data).then((res) => {
		return res.data
	})

	if (user.confirm != 'success') {
		activateAlert({
			img: 'user-alt-slash',
			success: false,
			type: 'icon',
			text: 'Account activation failed.',
			link: ''
		})
		return
	}

	var userDecoded = jwtdecode(user.token)

	if (typeof window != 'undefined')
		User.set({
			auth: true,
			name: userDecoded.name,
			real_name: userDecoded.realname,
			email: userDecoded.email,
			avatar: userDecoded.avatar,
			id: userDecoded.id,
			permissions: userDecoded.permissions,
			theme: userDecoded.theme,
			theme_mode: userDecoded.theme_mode,
		})

	cookies.set('token', user.token, { maxAge: 60 * 60 * 24 * 30, path: '/' })
	activateAlert({
		img: 'user-check',
		type: 'icon',
		success: true,
		text: 'Account activated successfully.',
		link: ''
	})
	window.location.href = '/'
}
