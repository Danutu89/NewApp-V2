import { instance } from './Requests.js'
import { api as Api, get } from './Store'

class Analytics {
	constructor() {
		this.agent = window.navigator.userAgent
		this.bot = /bot|google|baidu|bing|msn|duckduckbot|teoma|slurp|yandex/.test(
			this.agent
		)
	}

	async SendView(route) {
		let res = await instance
			.post(get(Api)['analytics.view'], {
				agent: this.agent,
				bot: this.bot,
				route: route,
			})
			.then((res) => res.data)

		if (res.operation != 'success') {
			console.log('Analytics: Error')
		}
	}
}

export { Analytics }
