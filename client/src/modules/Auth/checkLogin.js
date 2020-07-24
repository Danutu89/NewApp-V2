import jwtdecode from 'jwt-decode'
import { user, setToken } from '../Store'

export default (req, res) => {
	let userDecoded = {}

	const cookies = require('cookie-universal')(req, res)

	try {
		userDecoded = jwtdecode(req.token)
		user.set(userDecoded)
		setToken(req.token)
		cookies.set('token', req.token, {
			maxAge: 60 * 60 * 24,
			path: '/',
		})
	} catch {
		user.reset()
		cookies.remove('token')
		setToken(null)
		return
	}

	if (userDecoded.exp < (new Date().getTime() + 1) / 1000) {
		user.reset()
		cookies.remove('token')
		setToken(null)
	}
}
