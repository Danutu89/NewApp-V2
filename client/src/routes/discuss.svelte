<script context="module">
	import { instance } from '../modules/Requests.js'
	import { isSSR } from '../modules/Preloads.js'
	import { get, api as Api, currentApi } from '../modules/Store'
	export async function preload(page) {
		let isSSRPage
		const res = instance.get(get(Api)['home.index'] + '?mode=discuss')
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
	import Home from '../Pages/Home/Home.svelte'

	currentApi.set({
		data: get(Api)['home.index'] + '?mode=discuss',
	})

	export let data
</script>

<svelte:head>
	<title>Discuss - NewApp</title>
	<meta
		name="description"
		content="NewApp the newest community for developers to learn, share​ ​their
		programming ​knowledge, and build their careers." />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://new-app.dev/" />
	<meta property="og:site_name" content="NewApp" />
	<meta
		property="og:image"
		itemprop="image primaryImageOfPage"
		content="https://new-app.dev/static/logo.jpg" />
	<meta
		property="og:description"
		content="The newest community for developers to learn, share​ ​their
		programming ​knowledge, and build their careers." />
	<meta name="twitter:title" content="NewApp" />
	<meta
		name="twitter:description"
		content="The newest community for developers to learn, share​ ​their
		programming ​knowledge, and build their careers." />
	<meta
		name="twitter:image:src"
		content="https://new-app.dev/static/logo.jpg" />
</svelte:head>

<Home {data} mode={'saved'} />
