<script>
	import { goto } from '@sapper/app'
	import { onMount } from 'svelte'
	import marked from 'marked'
	import { host } from '../../modules/Options.js'
	import TurndownService from 'turndown'
	import { instance } from '../../modules/Requests.js'
	import { activateAlert } from '../../modules/Alert.js'
	import { user as User, api as Api } from '../../modules/Store'

	export let data
	let title_c = data.title
	let title_s, editor_s
	let editor
	let turndown = TurndownService()
	let text_c = turndown.turndown(data.text)

	async function EditPost() {
		const res = await instance
			.post($Api['post.edit'] + data.id, {
				title: title_c,
				text: marked(editor.value()),
				id: data.id,
			})
			.then(function (response) {
				if (response.status != 200) {
					//alert
					return
				}
				if (response.data['operation'] == 'failed') {
					//alert
					return
				}
				activateAlert({
					img: 'na-check-circle',
					type: 'icon',
					success: true,
					text: 'Post edited successfully.',
					link: '/post/' + response.data['link']
				})
				goto(response.data['link'])
			})
		const json = await res
	}

	onMount(async function () {
		editor_s = document.querySelectorAll('textarea')[1]
		let SimpleMDE = require('simplemde')
		editor = new SimpleMDE({
			element: document.getElementById('editor'),
			toolbar: false,
			status: false,
		})
		editor.value(text_c)
	})
</script>

<editpost>
	<div class="newpost-form">
		<div class="header">
			<input
				id="title"
				bind:this={title_s}
				bind:value={title_c}
				name="title"
				placeholder="Title"
				required="true"
				style="background: transparent !important; font-size: 2rem;"
				type="text" />
		</div>
		<br />
		<div class="body">
			<textarea id="editor" />
		</div>
		<div class="footer">
			<button on:click={EditPost} class="newpost">Edit</button>
		</div>
	</div>
</editpost>

<svelte:head>
	<title>Edit - {title_c}</title>
</svelte:head>
