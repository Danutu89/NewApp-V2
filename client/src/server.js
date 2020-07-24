import sirv from 'sirv'
import polka from 'polka'
import compression from 'compression'
import * as sapper from '@sapper/server'
import Auth from './modules/Auth'

const { PORT, NODE_ENV } = process.env
const dev = NODE_ENV === 'development'

polka() // You can also use Express
	.use(
		compression({ threshold: 0 }),
		sirv('static', { dev }),
		async (req, res, next) => {
			const cookies = require('cookie-universal')(req, res)
			if (cookies.get('token')) req.token = cookies.get('token')
			else req.token = ''
			Auth.checkLogin(req, res)
			next()
		},
		sapper.middleware()
	)
	.listen(PORT, (err) => {
		if (err) console.log('error', err)
	})
