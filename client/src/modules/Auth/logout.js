import { instance } from '../Requests.js'
import { socket } from '../SocketIO.js'
import { get, user } from '../Store'
import Cookie from 'cookie-universal'
const cookies = Cookie()

export default async () => {
	var userStore = get(user)
	if (userStore.auth) {
		socket.emit('logout', {
			data: userStore.token,
		})
		instance.defaults.headers.common['Token'] = ''
		user.reset()
		cookies.remove('token')
		await setTimeout(()=>{document.dispatchEvent(new CustomEvent('reloading'))}, 0)
		//location.reload()
	}
}
