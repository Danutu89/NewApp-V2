<script>
	export let article
	import { onMount, beforeUpdate } from 'svelte'
	import OpenJoin from '../../../modules/OpenJoin.js'
	import { host } from '../../../modules/Options.js'
	import { instance } from '../../../modules/Requests.js'
	import { swipeDirection } from '../../../modules/Swipe.js'
	import {
		user as User,
		api as Api,
		deviceType as DeviceType,
	} from '../../../modules/Store'
	import TurndownService from 'turndown'
	import marked from 'marked'
	import { stores } from '@sapper/app'
	const { page } = stores()

	let like_button
	let reply_likes = []
	let like_counter
	let editor, editor_s
	let isMobile
	let turndown = TurndownService()
	let reply_id = -1
	let options_list, share_btn, optionsBtn, share_list

	let document_

	let editing = false
	let editing_id

	let webview = false

	let overflow

	let dark_theme

	let touchstartX = 0
	let touchstartY = 0
	let touchendX = 0
	let touchendY = 0
	let touchstartEl = null

	let saveButton, copyButton

	article.info.comments.forEach((reply) => {
		reply.mentions.forEach((mention) => {
			reply.text = String(reply.text).replace(
				'@' + mention,
				'<a href="/user/' + mention + '">@' + mention + '</a>'
			)
		})
	})

	function likePostAnim() {
		if (like_button.classList.contains('na-heart1')) {
			var likes = parseInt(like_counter.innerHTML)
			var total = likes + 1
			like_counter.innerHTML = total
			like_button.classList.remove('na-heart1')
			like_button.classList.add('na-heart')
			like_button.classList.add('heartscale')
		} else if (like_button.classList.contains('na-heart')) {
			var likes = parseInt(like_counter.innerHTML)
			var total = likes - 1
			like_counter.innerHTML = total
			like_button.classList.remove('na-heart')
			like_button.classList.add('na-heart1')
			like_button.classList.remove('heartscale')
		}
	}

	function Like_Post() {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		likePostAnim()
		instance
			.get($Api['post.like'] + article.id, { progress: false })
			.then((response) => {
				if (response.status != 200) {
					likePostAnim()
				}
				if (response.data['operation'] == 'failed') {
					likePostAnim()
				}
			})
	}

	function likeReplyAnim() {
		if (reply_likes[id].classList.contains('na-heart')) {
			reply_likes[id].classList.remove('na-heart')
			reply_likes[id].classList.add('na-heart1')
			reply_likes[id].classList.remove('heartscale')
		} else if (reply_likes[id].classList.contains('na-heart1')) {
			reply_likes[id].classList.remove('na-heart1')
			reply_likes[id].classList.add('na-heart')
			reply_likes[id].classList.add('heartscale')
		}
	}

	function Like_Reply(id) {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		likeReplyAnim()
		instance
			.get($Api['post.like'] + article.id, { progress: false })
			.then((response) => {
				if (response.status != 200) {
					likeReplyAnim()
				}
				if (response.data['operation'] == 'failed') {
					likeReplyAnim()
				}
			})
	}

	async function Reply(type) {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		if (editor.value().length < 2) {
			if (!editor_s) {
				editor_s = document.querySelectorAll('textarea')[1]
			}
			editor_s.setCustomValidity('Please fill out this field.')
			editor_s.classList.add('error')
			editor_s.reportValidity()
			return
		}
		let markdown = marked(editor.value())
		let reply
		let payload
		if (type == 'post') {
			payload = {
				content: markdown,
				token: $User.token,
				post_id: article.id,
				type: 'post',
			}
		} else {
			payload = {
				content: markdown,
				token: $User.token,
				post_id: article.id,
				type: 'reply',
				reply_id: reply_id,
			}
		}
		let json = await instance
			.post($Api['replies.new'], payload)
			.then((response) => {
				return response
			})

		let data = await json
		if (data.status != 200) {
			//alert
			return
		}

		if (data.data['operation'] != 'success') {
			//alert
			console.log(data.data['error'])
			return
		}

		reply = data.data.reply
		reply.text = markdown
		article.info.comments = [...article.info.comments, reply]
		PR.prettyPrint()
		editor.value('')
	}

	function Comment(_reply_id, reply_author) {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		let reply = document.querySelector('.post-reply')
		if (reply.style['display'] === 'none') {
			if ($DeviceType == 'mobile') {
				reply.style['display'] = 'block'
			}
			//editor.codemirror.focus()
		} else {
			if ($DeviceType == 'mobile') {
				reply.style['display'] = 'none'
			}
		}
		if (($DeviceType == 'mobile') === false) {
			//editor.codemirror.focus()
		}
		if (_reply_id != -1 && typeof _reply_id != 'undefined') {
			reply_id = _reply_id
			editor.value('@' + reply_author)
		}
	}

	async function Delete_Reply(id) {
		if ($User.auth == false) {
			return
		}
		const not = await instance
			.get($Api['replies.delete'] + id)
			.then((response) => {
				if (response.status != 200) {
					//alert
					return
				}

				if (response.data['operation'] != 'success') {
					//alert
					return
				}

				document.getElementById('reply_' + id).remove()

				return
			})
	}

	function Cancel_Reply() {
		if (editing) {
			editing = false
			editing_id = null
			editor.value('')
		}
	}

	function Edit_Reply(reply) {
		editing_id = reply
		editing = true
		if ($DeviceType == 'mobile') Comment()
		editor.value(turndown.turndown(reply.text_e))
		editor.codemirror.focus()
	}

	async function C_Edit_Reply() {
		if (
			($User.auth == false && $User.id != editing_id.author.id) ||
			$User.permissions.edit_reply_permission == false
		) {
			return
		}
		const resp = await instance
			.post($Api['replies.edit'], {
				content: marked(editor.value()),
				r_id: editing_id.id,
				token: $User.token,
			})
			.then((response) => {
				if (response.status != 200) {
					//alert
					return
				}

				if (response.data['operation'] != 'success') {
					//alert
					return
				}

				var data = response.data['reply']

				let replies = article.replies
				replies.forEach((reply) => {
					if (reply.id == editing_id.id) {
						reply.text_e = data['content']
						reply.text = data['content']
						data['mentions'].forEach((mention) => {
							reply.text = String(reply.text).replace(
								'@' + mention,
								'<a href="/user/' + mention + '">@' + mention + '</a>'
							)
						})
					}
				})
				article.replies = replies
				editing_id = null
				editing = false
				editor.value('')
				PR.prettyPrint()
				return
			})
	}

	function onClickDocument(e) {
		if (!copyButton || !share_btn || !options_list || !optionsBtn) return

		if (!copyButton.contains(e.target)) {
			copyButton.innerHTML = copyButton.childNodes[0].outerHTML + ' Copy Link'
			copyButton.childNodes[0].classList.remove('scale-anim')
		}
		if ($DeviceType == 'mobile') {
			if (share_btn.contains(e.target)) {
				if (options_list.classList.contains('toggled')) {
					if (options_list.classList.contains('share')) {
						options_list.classList.remove('toggled')
						options_list.classList.remove('share')
					} else {
						options_list.classList.add('share')
					}
				} else {
					options_list.classList.add('toggled')
					options_list.classList.add('share')
				}
			} else if (optionsBtn.contains(e.target)) {
				if (options_list.classList.contains('toggled')) {
					if (options_list.classList.contains('share')) {
						options_list.classList.remove('share')
					} else options_list.classList.remove('toggled')
				} else {
					options_list.classList.add('toggled')
				}
			} else if (
				!share_btn.contains(e.target) &&
				!options_list.contains(e.target)
			) {
				options_list.classList.remove('toggled')
				options_list.classList.remove('share')
			}
		} else {
			if (share_btn.contains(e.target)) {
				if (share_list.classList.contains('toggled')) {
					share_list.classList.remove('toggled')
				} else {
					share_list.classList.add('toggled')
				}
			} else if (
				!share_list.contains(e.target) &&
				!share_list.contains(e.target)
			) {
				share_list.classList.remove('toggled')
			}
		}
	}

	function savePost() {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		instance
			.get($Api['post.save'] + article.id, { progress: false })
			.then((response) => {
				if (response.data['operation'] == 'saved') {
					saveButton.innerHTML = saveButton.childNodes[0].outerHTML + ' Saved'
					saveButton.childNodes[0].classList.add('scale-anim')
				} else if (response.data['operation'] == 'deleted') {
					saveButton.innerHTML = saveButton.childNodes[0].outerHTML + ' Save'
					saveButton.childNodes[0].classList.remove('scale-anim')
				}
				document.activeElement = null
			})
	}

	async function copyLink() {
		if (!navigator.clipboard) return
		await navigator.clipboard.writeText(location.href)
		copyButton.innerHTML = copyButton.childNodes[0].outerHTML + ' Copied'
		copyButton.childNodes[0].classList.add('scale-anim')
		document.activeElement = null
	}

	function updatePage() {
		if (PR) PR.prettyPrint()
	}

	onMount(async function () {
		document_ = document
		var ua = navigator.userAgent
		if (ua.includes('wv') && $User.auth == false) {
			OpenJoin()
			webview = true
		} else {
			webview = false
		}

		if (article.info.closed == false) {
			let reply = document.querySelector('.post-reply')
			if (($DeviceType == 'mobile') === true) {
				if (reply.style['display'] == 'none') reply.style['display'] = 'none'
			} else {
				reply.style['display'] = 'block'
			}
			editor_s = document.querySelectorAll('textarea')[1]
			let SimpleMDE = require('simplemde')
			editor = new SimpleMDE({
				element: document.getElementById('editor'),
				toolbar: false,
				status: false,
			})
		}
		document.addEventListener('click', onClickDocument, {
			capture: true,
		})
		overflow = document.querySelector('overflow')
		document.addEventListener('urlPathUpdated', updatePage)
	})
</script>

{#if article}
	<div class="article">
		<div class="post">
			{#if article.thumbnail}
				<div class="thumbnail">
					<img
						loading="lazy"
						data="/static/thumbnail_post/post_{article.id}.jpeg"
						onerror="this.style.display='none'"
						alt=""
						style="width: 100%;border-top-left-radius: var(--border-radius);
						border-top-right-radius: var(--border-radius);" />
				</div>
			{/if}
			<div class="content-post" style="padding:0.8rem;">
				<div class="info" style="display:flex;">
					<h1 style="margin-top: 0;font-weight: 400;font-size: 2rem;">
						{article.title}
					</h1>
				</div>
				<div class="post-author">
					<img
						style="border-radius:50px;margin-right: 5px;"
						height="40px"
						width="40px"
						onerror="this.style.display='none'"
						data="{$Api['users.images']}{article.author.info.avatar_img}"
						alt={article.author.name} />
					<div class="author-info">
						<a href="/user/{article.author.name}">
							<span class="author-name">{article.author.info.full_name}</span>
						</a>
						<div class="post-tags">
							{#each article.info.tags as tag}
								<a href="/tag/{tag.name}" style="font-size:13px;">
									<tag>{tag.name}</tag>
								</a>
							{/each}
						</div>
					</div>
				</div>
				<div class="post_content" style="margin-top: 1.5rem;">
					{@html article.info.text}
				</div>
				<br />

				<div class="user-actions">
					{#if $User.auth}
						{#if article.userInfo['liked']}
							<span
								style="cursor: pointer;margin-right:0.5rem;"
								on:click|preventDefault={Like_Post}>
								<i id="heart" class="na-heart" bind:this={like_button} />
								<span>Like</span>
							</span>
						{:else}
							<span
								style="cursor: pointer;margin-right:0.5rem;"
								on:click|preventDefault={Like_Post}>
								<i id="heart" class="na-heart1" bind:this={like_button} />
								<span>Like</span>
							</span>
						{/if}
					{:else}
						<span style="cursor: pointer;margin-right:0.5rem;">
							<i
								id="heart"
								class="na-heart1"
								on:click|preventDefault={Like_Post}
								bind:this={like_button} />
							<span>Like</span>
						</span>
					{/if}
					{#if article.info.closed == false}
						<span
							style="cursor: pointer;margin-right:0.5rem;"
							on:click|preventDefault={() => {
								Comment(-1)
							}}>
							<i id="comment" class="na-comment" />
							<span>Comment</span>
						</span>
					{/if}
					<span style="cursor: pointer;" bind:this={share_btn}>
						<i class="na-share" />
						<span>Share</span>
					</span>
					<div class="post-share" style="left:10.5rem;" bind:this={share_list}>
						<div class="list">
							<div class="title">Share</div>
							<hr />
							<div class="item">
								<i class="na-facebook-square" />
								Facebook
							</div>
							<div class="item">
								<i class="na-twitter" />
								Twitter
							</div>
							<div class="item">
								<i class="na-globe" />
								Hacker News
							</div>
						</div>
					</div>
					<div class="post-options" bind:this={options_list}>
						<div class="lists">
							<div class="list">
								<div class="title">Options</div>
								<hr />
								<div
									class="item"
									on:click|preventDefault={() => {
										options_list.classList.add('share')
									}}>
									<i class="na-share" />
									Share
								</div>
								<div
									class="item"
									on:click|preventDefault={savePost}
									bind:this={saveButton}>
									<i class="na-inbox-in" />
									Save
								</div>
								<div
									class="item"
									on:click|preventDefault={copyLink}
									bind:this={copyButton}>
									<i class="na-edit" />
									Copy Link
								</div>
							</div>
							<div class="list" style="margin-left:1rem">
								<div class="title">
									<i
										class="na-chevron-left"
										style="margin-right: 1rem;"
										on:click|preventDefault={() => {
											options_list.classList.remove('share')
										}} />
									Share
								</div>
								<hr />
								<div class="item">
									<i class="na-facebook-square" />
									Facebook
								</div>
								<div class="item">
									<i class="na-twitter" />
									Twitter
								</div>
								<div class="item">
									<i class="na-globe" />
									Hacker News
								</div>
							</div>
						</div>
					</div>
					<span
						style="cursor: pointer;margin-right:0.5rem;"
						class="mobile-post-options"
						bind:this={optionsBtn}>
						<i class="na-cog" />
						<span>Options</span>
					</span>
				</div>
				<div class="user-actions-info">
					<span>
						<span id="hearts" bind:this={like_counter}>
							{article.info.likes_count}
						</span>
						Likes
					</span>
				</div>
				{#if article.info.closed == false}
					<div class="post-reply" style="margin-top:3%;display:none;">
						<textarea
							class="editor"
							id="editor"
							style="margin-bottom:1%;"
							minlength="0"
							autocomplete="off"
							autocorrect="off"
							autocapitalize="off"
							spellcheck="false" />
						<div style="display:flex;">
							{#if editing == false}
								{#if reply_id != -1}
									<button
										class="reply-button"
										on:click={() => {
											;(reply_id = -1), editor.value('')
										}}>
										Cancel Reply
									</button>
									<button
										class="reply-button"
										on:click={() => {
											Reply('reply')
										}}
										style="margin-inline-start:auto;">
										Post Reply
									</button>
								{:else}
									<button
										class="reply-button"
										on:click={() => {
											Reply('post')
										}}
										style="margin-inline-start:auto;">
										Post Reply
									</button>
								{/if}
							{:else}
								<button class="reply-button" on:click={Cancel_Reply}>
									Cancel Edit
								</button>
								<button
									class="reply-button"
									on:click={C_Edit_Reply}
									style="margin-inline-start:auto;">
									Edit Reply
								</button>
							{/if}
						</div>
					</div>
				{:else}
					<div
						class="card"
						style="padding: 0.5rem; text-align: center; margin-top: 1rem;">
						<div class="card-body">
							<p>
								<i class="na-lock" />
								Post closed by {article.info.closed_by} on {article.info.closed_on}
							</p>
						</div>
					</div>
				{/if}
			</div>

		</div>
		{#each article.info.comments as reply}
			<div class="reply" id="reply_{reply.id}">
				<div
					id="reply_img_{reply.author.name}"
					class="author"
					style=" border-radius: 8px; padding: 0.5rem; display: flex;">
					<img
						style="border-radius:20px;margin-right: 5px;"
						onerror="this.style.display='none'"
						height="35px"
						width="35px"
						data="{$Api['users.images']}{reply.author.info.avatar_img}"
						alt={reply.author.name} />
					<div id="reply_name_{reply.author.name}" style="margin-top:-0.1rem;">

						<a
							id="reply_name"
							style="font-size: 0.8rem;"
							href="/user/{reply.author.name}">
							@{reply.author.name}
						</a>
						<p
							style="font-size: 60%;opacity: 0.6;margin-bottom: 0;margin-top: 0;">
							{reply.author.info.full_name}
						</p>
					</div>
				</div>

				{@html reply.text}

				<br />
				<div class="info" style="display: flex">
					<div class="user-actions">
						<span
							style="cursor: pointer;margin-right:0.5rem;vertical-align: sub;"
							on:click|preventDefault={() => {
								Like_Reply(reply.id)
							}}
							bind:this={reply_likes[reply.id]}>
							{#if reply.userInfo.liked}
								<i id="heart" class="na-heart" />
							{:else}
								<i id="heart" class="na-heart1" />
							{/if}
							<span>Like</span>
						</span>
						<span
							style="cursor: pointer;vertical-align: sub;"
							on:click|preventDefault={() => {
								Comment(reply.id, reply.author.name)
							}}>
							<i id="reply" class="na-comment" />
							<span>Reply</span>
						</span>
					</div>
					<div style="margin-inline-start: auto;display:flex;">
						{#if $User.auth}
							<div class="reply-actions">
								{#if reply.mine || $User.permissions.edit_reply == true}
									<button
										class="edit"
										on:click={() => {
											Edit_Reply(reply)
										}}>
										Edit
									</button>
								{/if}
								{#if reply.mine || $User.permissions.delete_reply == true}
									<button
										class="delete"
										on:click={() => {
											Delete_Reply(reply.id)
										}}>
										Delete
									</button>
								{/if}
							</div>
						{/if}
					</div>

				</div>
			</div>
			{#each reply.replies as reply}
				<div class="reply" id="reply_{reply.name}" style="margin-left: 2rem;">
					<div
						id="reply_img_{reply.author.name}"
						class="author"
						style=" border-radius: 8px; padding: 0.5rem; display: flex;">
						<img
							style="border-radius:20px;margin-right: 5px;"
							onerror="this.style.display='none'"
							height="35px"
							width="35px"
							data="{$Api['users.images']}{reply.author.info.avatar_img}"
							alt={reply.author.name} />
						<div
							id="reply_name_{reply.author.name}"
							style="margin-top:-0.1rem;">

							<a
								id="reply_name"
								style="font-size: 0.8rem;"
								href="/user/{reply.author.name}">
								@{reply.author.name}
							</a>
							<p
								style="font-size: 60%;opacity: 0.6;margin-bottom: 0;margin-top:
								0;">
								{reply.author.info.full_name}
							</p>
						</div>
					</div>

					{@html reply.text}

					<br />
					<div class="info" style="display: flex">
						<div class="user-actions">
							<span
								style="cursor: pointer;margin-right:0.5rem;vertical-align: sub;"
								on:click|preventDefault={() => {
									Like_Reply(reply.id)
								}}
								bind:this={reply_likes[reply.id]}>
								{#if reply.userInfo.liked}
									<i id="heart" class="na-heart" />
								{:else}
									<i id="heart" class="na-heart1" />
								{/if}
								<span>Like</span>
							</span>
							<span
								style="cursor: pointer;vertical-align: sub;"
								on:click|preventDefault={() => {
									Comment(reply.id, reply.author.name)
								}}>
								<i id="reply" class="na-comment" />
								<span>Reply</span>
							</span>
						</div>
						<div style="margin-inline-start: auto;display:flex;">
							{#if $User.auth}
								<div class="reply-actions">
									{#if reply.mine || $User.permissions.edit_reply == true}
										<button
											class="edit"
											on:click={() => {
												Edit_Reply(reply)
											}}>
											Edit
										</button>
									{/if}
									{#if reply.mine || $User.permissions.delete_reply == true}
										<button
											class="delete"
											on:click={() => {
												Delete_Reply(reply.id)
											}}>
											Delete
										</button>
									{/if}
								</div>
							{/if}
						</div>

					</div>
				</div>
			{/each}
		{/each}
		<br />
		<p style="margin-top: 1rem; font-size:initial;color:var(--color);">
			Not the answer you're looking for? Browse other questions tagged
			{#each article.info.tags as tag}
				<a href="/tag/{tag.name}" style="font-size:13px;margin-left:3px;">
					<tag>{tag.name}</tag>
				</a>
			{/each}
			{#if $User.auth}
				or
				<a href="/newpost" rel="prefetch" style="color:#18BC9C;">
					ask your own question
				</a>
			{/if}
			.
		</p>
	</div>
{/if}
