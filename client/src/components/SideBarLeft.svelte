<script>
	import { instance } from '../modules/Requests.js'
	import { onMount, onDestroy } from 'svelte'
	import OpenJoin from '../modules/OpenJoin.js'
	import { host } from '../modules/Options.js'
	import {
		user as User,
		api as Api,
		deviceType as DeviceType,
	} from '../modules/Store'
	import { swipeDirection } from '../modules/Swipe.js'

	export let user
	export let utilities
	let tag_button = []

	let top, height, winHeight

	let document_
	let window_

	function Follow_Tag(tag_) {
		if ($User.auth == false) {
			OpenJoin()
			return
		}
		instance
			.get($Api['follow.tag'] + tag_, { progress: false })
			.then(function (response) {
				var x = tag_button[tag_]
				tag_button[tag_] = x

				if (response.staus != 200) {
					//alert
					return
				}

				if (response.data['operation'] == 'followed') {
					x.innerHTML = 'Unfollow'
					utilities.tags.splice(utilities.tags.indexOf(tag_), 1)
					utilities.tags = [...utilities.tags]
					user.flw_tags = [...user.flw_tags, tag_]
				} else if (response.data['operation'] == 'unfollowed') {
					x.innerHTML = 'Follow'
					user.flw_tags.splice(user.flw_tags.indexOf(tag_), 1)
					user.flw_tags = [...user.flw_tags]
					utilities.tags = [...utilities.tags, tag_]
				}
			})
	}

	function updateView() {
		if ($DeviceType == 'tablet' || $DeviceType == 'mobile') {
			document.getElementById('sidebar-left').classList.add('wrapper-left')
			document.getElementById('sidebar-left').classList.remove('sidebar')
		} else {
			document.getElementById('sidebar-left').classList.remove('wrapper-left')
			document.getElementById('sidebar-left').classList.add('sidebar')
			document.getElementById('sidebar-left').style['transform'] = ''
		}
	}

	onMount(async function () {
		window_ = window
		document.addEventListener('changedDeviceType', updateView)
		top = document.getElementById('sidebar-left').offsetTop
		height = document.getElementById('sidebar-left').offsetHeight
		winHeight = window.innerHeight
		document_ = document
	})

	onDestroy(function () {
		if (document_ && window_) {
			document_.removeEventListener('changedDeviceType', updateView)
		}
	})
</script>

<div
	class={$DeviceType != 'desktop' ? 'wrapper-left' : 'sidebar'}
	id="sidebar-left">
	<div class="widget" id="pwa">
		<div class="widget-list">
			<div class="widget-item" style="display: flex;">
				<div class="text" style="line-height: 1.5;">Install our WebApp</div>
				<button
					class="widget-button"
					id="install_pwa"
					style="margin-inline-start: auto;">
					Install
				</button>
			</div>
		</div>
	</div>
	{#if $User.auth}
		<div class="user-card">
			<a href="/user/{$User.name}" style="display: flex;">
				<div class="user-image">
					<img
						class="profile_image"
						alt=""
						data="{$Api['users.images']}{$User.avatar}"
						onerror="this.style.display='none'"
						height="50px"
						width="50px"
						title="profile image" />
				</div>
				<div class="user-info" style="margin-top: -0.2rem;">
					<div style="font-size:1.1rem;">{$User.real_name}</div>
					<div class="user-tag" style="font-size: 0.7rem;">@{$User.name}</div>
				</div>
			</a>
		</div>
	{/if}
	<!--
<div class="widget" id="navigation">
    <div class="widget-header">
        <div class="widget-title">Navigation</div>
    </div>
    <div class="widget-list">
        <div class="widget-item" id='posts-show'>
            <div class="text"><a href="/"><span class="section"><i class="na-pen-square"></i> Posts</span></a></div>
        </div>
        <div class="widget-item" id='podcasts-show'>
            <div class="text"><a href="/podcasts"><span class="section"><i class="na-headphones"></i> Podcasts</span></a></div>
        </div>
    </div>
</div>
-->
	{#if utilities}
		<div class="widget">
			<div class="widget-header">
				<div class="widget-title">Customize your experience</div>
			</div>
			<div class="widget-list" style="max-height: 400px;overflow: auto;">
				{#if user && 'flw_tags' in user}
					{#if $User.auth && user.flw_tags}
						{#each user.flw_tags as tag}
							<div
								class="widget-item"
								id="widget-tags"
								style="border-top: none;display: flex;">
								<div class="text">
									<a style="text-decoration: underline;" href="/tag/{tag.name}">
										#{tag.name}
									</a>
								</div>
								<button
									class="widget-button"
									bind:this={tag_button[tag]}
									on:click|preventDefault={() => Follow_Tag(tag.name)}
									id="follow-tag-{tag}"
									style="margin-inline-start: auto;">
									Unfollow
								</button>
							</div>
						{/each}
						<div
							class="widget-item"
							style="border-top: none;display: flex;background-color:
							var(--background-1);">
							<div class="text">Other Popular Tags</div>
						</div>
					{/if}
				{/if}
				{#each utilities.tags as tag}
					<div
						class="widget-item"
						id="widget-tags"
						style="border-top: none;display: flex;">
						<div class="text">
							<a style="text-decoration: underline;" href="/tag/{tag.name}">
								#{tag.name}
							</a>
						</div>
						<button
							class="widget-button"
							bind:this={tag_button[tag.name]}
							on:click|preventDefault={() => Follow_Tag(tag.name)}
							id="follow-tag-{tag.name}"
							style="margin-inline-start: auto;">
							Follow
						</button>
					</div>
				{/each}
			</div>
		</div>
	{/if}
	<div class="widget" style="display: block;padding: 1rem;">
		<a href="https://new-app.dev">
			<img
				style="vertical-align: middle;margin-left: -1px;"
				onerror="this.style.display='none'"
				data="https://newappcdn.b-cdn.net/images/logo.svg"
				width="25"
				height="30"
				alt="" />
		</a>
		<a href="https://www.facebook.com/newapp.nl">
			<i
				class="na-facebook-square"
				style="font-size: 2rem; color: var(--theme-color); vertical-align:
				middle; margin-left: 0.5rem;" />
		</a>
		<a href="https://twitter.com/_NewApp_">
			<i
				class="na-twitter"
				style="font-size: 2rem; color: var(--theme-color); vertical-align:
				middle; margin-left: 0.5rem;" />
		</a>
		<a href="/about" style="display: block;margin-top: 0.5rem;">About</a>
		<a href="/contact" style="display: block;margin-top: 0.5rem;">Contact</a>
		<a href="/privacy" style="display: block;margin-top: 0.5rem;">Privacy</a>
	</div>

</div>
