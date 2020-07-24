<script context="module">
	import { instance } from '../../modules/Requests.js'
	import { isSSR } from '../../modules/Preloads.js'
	import { get, api as Api, currentApi } from '../../modules/Store'
	export async function preload(page, session) {
		let isSSRPage
		const res = instance.get(get(Api)['users.user'] + page.params.slug)
		isSSR.subscribe((value) => {
			isSSRPage = value
		})()

		if (!isSSRPage) {
			return { data: res }
		}

		const response = await res
			.then(function (response) {
				return response
			})
			.catch((err) => {
				return err.response
			})

		if (response.status != 200) {
			return this.error(response.status, response.statusText)
		}

		const json = await response.data

		return { data: json }
	}
</script>

<script>
	import User from '../../Pages/User/User.svelte'
	import { stores } from '@sapper/app'
	const { page } = stores()

	currentApi.set({
		data: get(Api)['users.user'] + $page.params.slug,
	})

	export let data
</script>

<User {data} />
