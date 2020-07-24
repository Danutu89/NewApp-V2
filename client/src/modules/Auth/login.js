import jwtdecode from 'jwt-decode'
import { instance } from '../Requests.js'
import { user as User, api as Api, get, setToken } from '../Store'
import Cookie from 'cookie-universal'
const cookies = Cookie()

export default async (username, pass) => {
	const res = await instance
		.post(get(Api)['auth.login'], {
			username: String(username).toLowerCase(),
			password: pass,
		})
		.then(function (response) {
			return response
		})
		.catch(function (error) {
			if (error.response) {
				return error.response
			}
		})
	const json = await res

	if (json.status != 200) return json

	var userDecoded = jwtdecode(json.data.login)

	if (typeof window != 'undefined')
		User.set({
			auth: true,
			id: userDecoded.id,
			name: userDecoded.name,
			real_name: userDecoded.realname,
			email: userDecoded.email,
			avatar: userDecoded.avatar,
			permissions: userDecoded.permissions,
			theme: get(User).theme,
		})

	cookies.set('token', json.data.login, {
		maxAge: 60 * 60 * 24 * 30,
		path: '/',
	})
	await setTimeout(()=>{document.dispatchEvent(new CustomEvent('reloading'))}, 0)
	setToken(json.data.login)

	return json
}
