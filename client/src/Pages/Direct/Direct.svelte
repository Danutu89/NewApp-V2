<script>
	import View from './View.svelte'
	import { onMount, beforeUpdate } from 'svelte'
	import { isSSR } from '../../modules/Preloads.js'
	import { instance } from '../../modules/Requests.js'
	import { stores, goto } from '@sapper/app'
	import { currentApi } from '../../modules/Store'
	import ReloadApi from '../../modules/ReloadApi'
	const { page } = stores()

	export let data
	let async = undefined,
		posts = undefined

	function LoadData() {
		if ($isSSR) {
			isSSR.set(false)
		} else if (data instanceof Promise) {
			posts = async () => {
				const response = await data
				if (response.status == 200) {
					const responseJson = await response
					return responseJson.data
				} else {
					throw new Error('Something went wrong')
				}
			}
			async = posts()
		}
	}

	onMount(async () => {
		LoadData()

		document.addEventListener('urlPathUpdated', PageUpdated)
		document.addEventListener('reloading', Reload)
	})

	function PageUpdated(e) {
		LoadData()
	}

	function Reload(e) {
		async = ReloadApi()
		data = async
	}
</script>

<View {data} {async} />
