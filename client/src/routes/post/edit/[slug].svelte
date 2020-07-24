<script context="module">
	import { instance } from '../../../modules/Requests.js'
	import {
		get,
		api as Api,
		user as User,
		currentApi,
	} from '../../../modules/Store'
	export async function preload(page) {
		let args = ''
		if (get(User).auth === false) {
			this.redirect(302, '/')
		}
		let temp = page.params.slug.toString().split('-')
		let id = temp[temp.length - 1]
		const res = instance.get(get(Api)['post.edit'] + id)
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
	import Edit from '../../../Pages/Post/Edit.svelte'

	export let data
</script>

<Edit {data} />

<svelte:head>
	<title>Edit Profile - NewApp</title>
	<meta name="robots" content="noindex" />
</svelte:head>
