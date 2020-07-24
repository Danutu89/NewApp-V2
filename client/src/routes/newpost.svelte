<script context="module">
	import { get, user as User } from '../modules/Store'
	export async function preload(page) {
		if (get(User).auth == false) {
			this.redirect(302, '/')
		}
	}
</script>

<script>
	import New from '../Pages/Post/New.svelte'
</script>

<New />

<svelte:head>
	<title>New Post - NewApp</title>
	<meta name="robots" content="noindex" />
</svelte:head>
