<script>
	import { instance } from '../../../modules/Requests.js'
	import OpenJoin from '../../../modules/OpenJoin.js'
	import { user as User, api as Api, currentChat } from '../../../modules/Store'
	import { currentPage, setSettings } from '../modules'
	import { goto } from '@sapper/app'

	export let user

	let follow_button

	function Follow_User() {
		if ($User.auth) {
			if ($User.id != user.id) {
				instance.get($Api['follow.user'] + user.id).then((response) => {
					if (response.data['operation'] == 'unfollowed') {
						follow_button.innerHTML = 'Follow'
					} else if (response.data['operation'] == 'followed') {
						follow_button.innerHTML = '&#x2713 Following'
					}
				})
			}
		} else {
			OpenJoin()
		}
	}

	async function goToDirect() {
		var chat = await instance
			.post($Api['direct.index'], { users: user.name, ids: user.id })
			.then((res) => {
				return res.data
			})

		currentChat.set(chat['current'])

		goto('/direct')
	}
</script>

<div class="sidebar-info">
	<div class="profile-image">
		<div>
			<div
				class="profile-photo"
				style="background-image: url({$Api['users.images']}{user.info.avatar_img});background-position:
				center center; background-size: cover; border: var(--border); height:
				200px; width: 200px; border-radius: 100px; border: 3px solid
				var(--background); left: 0; right: 0; margin: auto;" />
		</div>

		<div class="user-name" style="line-height: 1.7rem;">
			<h1 style="font-weight: 400;">{user.info.full_name}</h1>
			<h4 style="font-weight: 400;">@{user.name}</h4>
		</div>
	</div>
	<div class="profile-actions">
		{#if $User.auth}
			{#if !user.mine}
				{#if $currentPage == 'settings'}
					<button
						class="follow-user"
						id="settings-user-{user.name}"
						on:click={() => {
							currentPage.set('main')
						}}>
						Profile
					</button>
					<button
						class="follow-user"
						style="margin-top: 0.5rem;"
						id="save-settings-user-{user.name}"
						on:click={setSettings}>
						Save
					</button>
				{:else}
					<button
						class="follow-user"
						id="settings-user-{user.name}"
						on:click={() => {
							currentPage.set('settings')
						}}>
						Settings
					</button>
				{/if}
			{:else}
				<button
					class="follow-user"
					bind:this={follow_button}
					on:click={Follow_User}
					id="follow-user-{user.name}">
					{#if user.userInfo['following']}&#x2713 Following{:else}Follow{/if}
				</button>
				<button
					class="follow-user"
					style="margin-top: 0.5rem;"
					on:click={goToDirect}>
					Messages
				</button>
			{/if}
		{:else}
			<button
				class="follow-user"
				bind:this={follow_button}
				on:click={Follow_User}
				id="follow-user-{user.name}">
				Follow
			</button>
		{/if}

	</div>
	<div class="widgets">
		<div class="profile-presentation">
			<div class="header">
				<i class="na-globe" />
				Presentation
			</div>
			<div class="bio">{user.pers.bio}</div>
			<div class="info">
				{#if user.pers.profession != 'None' && user.pers.profession}
					<p>
						<i class="na-briefcase" />
						Profession {user.pers.profession}
					</p>
				{/if}
				<p>
					<i class="na-home" />
					From {user.location.location.country}
					<span class="flag-icon flag-icon-{user.location.location.flag}" />
				</p>
				<p>
					<i class="na-clock" />
					Joined on {user.info.joined_on}
				</p>
				<p>
					<i class="na-rss" />
					Followed by {user.followers_count} people
				</p>
			</div>
		</div>
		{#if user.tags}
			<div class="interesed-tags">
				<div class="header">
					<i class="na-hashtag" />
					Interesed Tags
				</div>
				<div class="tags">
					{#each user.tags as tag}
						<a
							style="text-decoration: none;"
							title={tag.name}
							href="/tag/{tag.name}">
							<span style="font-size: 12px;">{tag.name}</span>
						</a>
						<br />
					{/each}
				</div>
			</div>
		{/if}
		{#if user.social}
			<div class="social">
				<div class="header">
					<i class="na-users" />
					Social
				</div>
				<div class="links">
					{#each user.social as social}
						<div style="margin-bottom: 0.3rem">
							<a
								style="text-decoration: none;"
								href="https://{social.social.pre_link}/{social.link}">
								<span style="font-size: 0.85rem;">
									<i class="na-{social.social.icon}" style="font-size: 1rem;" />
									@{social.link}
								</span>
							</a>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</div>
</div>
