<script>
	import { instance } from '../modules/Requests.js'
	import OpenJoin from '../modules/OpenJoin.js'
	import SPost from './Loading/SPost.svelte'
	import { user as User, api as Api } from '../modules/Store'
	import { host } from '../modules/Options.js'
	import { onMount, onDestroy } from 'svelte'
	import { activateAlert } from '../modules/Alert.js';

	export let data, mode, user
	let save_button = []
	let document_
	let page_ = 1
	let isLoadMore = true,
		CanLoad = false
	let loadPosts

	$: if (data) {
		isLoadMore = data['hasnext']
	}

	function SavePost(id) {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		instance
			.get($Api['post.save'] + id, { progress: false })
			.then((response) => {
				if (response.data['operation'] == 'saved') {
					save_button[id].innerHTML = 'Saved'
					activateAlert({
						img: 'na-check-circle',
						type: 'icon',
						success: true,
						text: 'Post saved successfully.',
						link: '/post/' + response.data['link']
					})
				} else if (response.data['operation'] == 'deleted') {
					save_button[id].innerHTML = 'Save'
				}
			})
	}

	onMount(() => {
		document_ = document
		document.addEventListener('scroll', onScroll)
	})

	onDestroy(function () {
		if (document_) document_.removeEventListener('scroll', onScroll)
	})

	function LoadMore() {
		page_++
		var args = '?'
		var added = false
		if (user) {
			args += 'user=' + user
			added = true
		} else if (mode) {
			args += '&mode=' + mode
			added = true
		}
		args += added ? '&page=' + page_ : 'page=' + page_
		loadPosts = instance
			.get($Api['home.index'] + args, { progress: false })
			.then(function (response) {
				data['list'] = [...data['list'], ...response.data['posts']['list']]
				data['hasnext'] = response.data['posts']['hasnext']
				data = data
			})
		isLoadMore = data['hasnext']
	}

	function onScroll(e) {
		const offset =
			document.documentElement.scrollHeight -
			document.documentElement.clientHeight -
			document.documentElement.scrollTop
		if (offset <= 400) {
			if (!CanLoad && isLoadMore) {
				LoadMore()
			}
			CanLoad = true
		} else {
			CanLoad = false
		}
	}
</script>

<div class="articles">
	{#if mode != 'user'}
		<div class="navigation-menu">
			<a href="/">
				<button>Home</button>
			</a>
			<a href="/questions">
				<button>Questions</button>
			</a>
			<a href="/discuss">
				<button>Discuss</button>
			</a>
			<a href="/tutorials">
				<button>Tutorials</button>
			</a>
		</div>
	{/if}
	{#each data.list as article}
		<div class="article-card" id="post_{article.id}">
			{#if article.thumbnail}
				<div
					class="article-thumbnail"
					style="max-height:300px;overflow: hidden;">
					<img
						loading="lazy"
						alt=""
						onerror="this.style.display='none'"
						data="/static/thumbnail_post/post_{article.id}.jpeg"
						style="border-top-left-radius: 8px; border-top-right-radius:
						8px;object-fit: cover;" />
				</div>
			{/if}
			<div class="article-main">
				<div class="article-author-image">
					<img
						class="profile_image"
						onerror="this.style.display='none'"
						loading="lazy"
						data="{$Api['users.images']}{article.author.info.avatar_img}"
						height="50px"
						width="50px"
						title="profile image"
						alt={article.author.name} />
				</div>
				<div class="article-info">
					<div class="article-title">
						<a rel="prefetch" href={article.link}>
							<h1 style="font-size: 1.5rem; font-weight: 400; margin: 0;">
								{article.title}
							</h1>
						</a>
					</div>
					<a rel="prefetch" href="/user/{article.author.name}">
						<div class="article-author">Author: {article.author.name}</div>
					</a>
					<div class="article-tags">
						<span>Tags:</span>
						{#each article.info.tags as tag}
							<a
								href="/tag/{tag.name}"
								rel="prefetch"
								style="margin-right: 0.1rem;">
								<tag class="article-tag">{tag.name}</tag>
							</a>
						{/each}
					</div>
				</div>
			</div>
			<div class="article-footbar">
				<div class="article-date">Published {article.info.posted_on}</div>
				<div class="article-misc">
					<span
						class="article-readtime"
						style="font-size: 0.8rem;color: grey;margin-right: 0.4rem;">
						{article.read_time}
					</span>
					<button
						class="article-save"
						id="save-{article.id}"
						bind:this={save_button[article.id]}
						on:click={() => SavePost(article.id)}>
						{#if $User.auth}
							{#if article.saved}Saved{:else}Save{/if}
						{:else}Save{/if}
					</button>
				</div>
			</div>
		</div>
	{/each}
	{#if loadPosts instanceof Promise == true}
		{#await loadPosts}
			<SPost />
		{/await}
	{/if}
</div>
