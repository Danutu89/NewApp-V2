export let host = 'http://localhost:5000'
export let sockets = 'https://new-app.dev'

if (process.env.NODE_ENV == 'prod') {
	host = 'https://new-app.dev'
	sockets = 'https://new-app.dev'
}
