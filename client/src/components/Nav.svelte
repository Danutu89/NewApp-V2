<script>
	import Login from './Login.svelte'
	import Register from './Register.svelte'
	import Auth from '../modules/Auth'
	import {
		user as User,
		api as Api,
		deviceType as DeviceType,
	} from '../modules/Store'
	import { onMount } from 'svelte'
	import { stores, goto } from '@sapper/app'
	import { host } from '../modules/Options.js'
	import Cookie from 'cookie-universal'
	import Join from '../components/Join.svelte'
	import { instance } from '../modules/Requests.js'
	import { activateAlert } from '../modules/Alert.js'
	import { socket } from '../modules/SocketIO.js'

	const { page } = stores()
	var jwt_decode = require('jwt-decode')

	let notificationListener

	let l_modal,
		r_modal,
		j_modal,
		l_modal_in,
		r_modal_in,
		j_modal_in,
		user = null,
		user_center = null,
		user_image = null,
		overflow = null,
		search = '',
		settings_button = null,
		guest_center = null,
		guest = null
	var menu_open = false
	let notifications, notifications_c, notifications_center_c, notification_list
	let toggle
	let p_image, l_image

	$: if($User.auth == false){
		if(typeof(document) != 'undefined'){
			l_modal = document.getElementById('login-modal')
			r_modal = document.getElementById('register-modal')
			j_modal = document.getElementById('join-modal')
			l_modal_in = document.getElementById('login-modal-inner')
			r_modal_in = document.getElementById('register-modal-inner')
			j_modal_in = document.getElementById('join-modal-inner')
		}
	}

	socket.on('notification', () => {
		fetchNotifications()
	})

	function onClickDocument(e) {
		if ($User.auth && (!user || !user_center || !user_image || !overflow )) return
		if (!$User.auth && (!guest || !guest_center || !settings_button || !overflow)) return

		if ($User.auth) {
			if (!user_image.contains(e.target) && !user_center.contains(e.target)) {
				if (notifications_c && notifications_center_c)
					if ($DeviceType != 'mobile')
						if (notifications_c.contains(e.target)) {
							user.style['display'] = 'none'
						}
				if (user.style['display'] == 'block') {
					user.style['display'] = 'none'
					overflow.classList.remove('show')
				}
			} else if (user_image.contains(e.target)) {
				if (user.style['display'] == 'none') {
					user.style['display'] = 'block'
					overflow.classList.add('show')
				} else if (user.style['display'] == 'block') {
					user.style['display'] = 'none'
					overflow.classList.remove('show')
				}
			}
			if ($DeviceType != 'mobile') {
				if (notifications_c && notifications_center_c)
					if (
						!notifications_c.contains(e.target) &&
						!notifications_center_c.contains(e.target)
					) {
						if (user_image.contains(e.target)) {
							notifications_center_c.style['display'] = 'none'
						} else if (notifications_center_c.style['display'] == 'block') {
							notifications_center_c.style['display'] = 'none'
							overflow.classList.remove('show')
						}
					} else if (notifications_c.contains(e.target)) {
						if (notifications_center_c.style['display'] == 'none') {
							notifications_center_c.style['display'] = 'block'
							overflow.classList.add('show')
						} else if (notifications_center_c.style['display'] == 'block') {
							notifications_center_c.style['display'] = 'none'
							overflow.classList.remove('show')
						}
					}
			}
		} else {
			if (settings_button.contains(e.target)) {
				if (guest.style['display'] == 'none') {
					guest.style['display'] = 'block'
					overflow.classList.add('show')
				} else if (guest.style['display'] == 'block') {
					guest.style['display'] = 'none'
					overflow.classList.remove('show')
				}
			}else if(!guest.contains(e.target)){
				guest.style['display'] = 'none'
				overflow.classList.remove('show')
			}

			if (!l_modal_in.contains(e.target)) {
				l_modal.style['visibility'] = 'hidden'
				l_modal.style['opacity'] = 0
				l_modal.style['pointer-events'] = 'none'
			}
			if (!r_modal_in.contains(e.target)) {
				r_modal.style['visibility'] = 'hidden'
				r_modal.style['opacity'] = 0
				r_modal.style['pointer-events'] = 'none'
			}
			if (!j_modal_in.contains(e.target)) {
				j_modal.style['visibility'] = 'hidden'
				j_modal.style['opacity'] = 0
				j_modal.style['pointer-events'] = 'none'
			}
		}
		if (menu_open === true) {
			return false
		}
	}

	async function fetchNotifications() {
		var not = await instance
			.get($Api['notifications.index'] + '?ex=false', { pregress: false })
			.then((response) => {
				return response.data
			})
		notifications = await not
	}

	function fetchNotificationsInterval() {
		return window.setInterval(async () => {
			fetchNotifications()
		}, 3000)
	}

	function checkDevice() {
		if ($DeviceType == 'mobile') {
			p_image = '35px'
			l_image = '30'
		} else {
			p_image = '30px'
			l_image = '25'
		}
	}

	onMount(async function () {
		l_modal = document.getElementById('login-modal')
		r_modal = document.getElementById('register-modal')
		j_modal = document.getElementById('join-modal')
		l_modal_in = document.getElementById('login-modal-inner')
		r_modal_in = document.getElementById('register-modal-inner')
		j_modal_in = document.getElementById('join-modal-inner')
		overflow = document.querySelector('overflow')
		document.addEventListener('changedDeviceType', checkDevice)
		checkDevice()
		document.addEventListener('click', onClickDocument, {
			capture: true,
		})
		//if ($User.auth)
		//fetchNotifications();

		var n_id = null
		/*if($User.auth){
    n_id = fetchNotificationsInterval();
  }else{
    if(n_id)
      window.clearInterval(n_id);
  }*/
		if ($User.theme == 'Light') {
			toggle.classList.remove('active')
		}
	})

	function OpenModalLogin() {
		if (!l_modal)
			l_modal = document.getElementById('login-modal')

		if (l_modal.style['opacity'] < 1) {
			l_modal.style['visibility'] = 'visible'
			l_modal.style['opacity'] = 1
			l_modal.style['pointer-events'] = 'auto'
		} else {
			l_modal.style['visibility'] = 'hidden'
			l_modal.style['opacity'] = 0
			l_modal.style['pointer-events'] = 'none'
		}
	}

	function Search() {
		goto('/search?q=' + search)
	}

	function handleKeydown(event) {
		if (event.keyCode == 13) {
			Search()
		}
	}

	function CloseMenu() {
		user.style['display'] = 'none'
		overflow.classList.remove('show')
		menu_open = false
	}

	function ToggleTheme() {
		var decoded
		var token_d = $User
		if (toggle.classList.contains('active') === true) {
			User.setItem('theme', 'Light')
			toggle.classList.remove('active')
		} else {
			User.setItem('theme', 'Dark')
			toggle.classList.add('active')
		}
	}

	function scrollToTop() {
		const c = document.documentElement.scrollTop || document.body.scrollTop
		if (c > 0) {
			window.requestAnimationFrame(scrollToTop)
			window.scrollTo(0, c - c / 8)
		}
	}

	function goHome() {
		if (window.scrollY == 0) {
			if (window.location.pathname == '/')
				document.dispatchEvent(new CustomEvent('reloadingAnim'));
			goto('/')
		} else {
			if(window.location.pathname != '/')
				goto('/')
			scrollToTop()
		}
	}

	function gotoPage(path){
		if (window.scrollY == 0) {
			if (window.location.pathname == path)
				document.dispatchEvent(new CustomEvent('reloadingAnim'));
			goto(path)
		} else {
			if(window.location.pathname != path)
				goto('/')
			scrollToTop()
		}
	}
</script>

<style>
	.toggle-theme {
		display: flex;
		margin-inline-start: auto;
	}
	.toggle {
		width: 50px;
		height: 20px;
		position: relative;

		margin: -3px 0;
		border-radius: 25px;
		cursor: pointer;

		border: 2px solid var(--secondary-background);
		background-color: var(--secondary-background);
		transition: 300ms all cubic-bezier(0, 0, 1, 1);
	}
	.toggle::after {
		position: absolute;
		content: '\e900';
		top: 4px;
		left: 7px;
		transition: 300ms all cubic-bezier(0, 0, 1, 1);
		font-family: 'NewApp-Icons';
		font-size: 13px;
		color: var(--color);
	}
	.active.toggle::after {
		left: 30px;
		content: '\f186';
	}
</style>

<nav class="newapp-navbar" id="navbar">
	<div class="navbar-items">
		<div class="navbar-item" style="cursor: pointer;">
			<div href="/" class="navbar-logo" on:click={goHome}>
				<img
					style="vertical-align: middle;"
					loading="lazy"
					data="https://newappcdn.b-cdn.net/images/logo.svg"
					width={l_image}
					alt="" />
			</div>
		</div>
		<div class="navbar-item navbar-search">
			<input
				bind:value={search}
				type="text"
				name="q"
				placeholder="Search"
				id="search"
				on:keydown={handleKeydown} />
		</div>
		<div class="navbar-item navbar-center">
			<div class="navigation">
				<div
					class="nav-item"
					on:click={() => {
						gotoPage('/')
					}}>
					<span>Home</span>
				</div>
				<div
					class="nav-item"
					on:click={() => {
						gotoPage('/discuss')
					}}>
					<span>Discuss</span>
				</div>
				<div
					class="nav-item"
					on:click={() => {
						gotoPage('/questions')
					}}>
					<span>Questions</span>
				</div>
				<div
					class="nav-item"
					on:click={() => {
						gotoPage('/tutorials')
					}}>
					<span>Tutorials</span>
				</div>
			</div>
		</div>
		<div style="margin-inline-start: auto;display:flex;">
			{#if $User.auth == true}
				{#if $DeviceType != 'mobile'}
					<div bind:this={notifications_c} class="navbar-item">
						<div
							class="newapp-dropdown"
							id="notification-center"
							style="cursor: pointer;">
							<i class="na-bell" />
							{#if notifications}
								{#if notifications.count_new > 0}
									<span class="notifications-number">
										{notifications.count_new}
									</span>
								{/if}
								<div
									bind:this={notifications_center_c}
									class="newapp-dropdown-content"
									id="notifications"
									style="display: none;">
									<a href="/notifications" style="color: var(--color);">
										Notifications
									</a>
									<hr />
									<div
										style="max-height: 20rem;overflow: auto;margin: 0rem -0.5rem
										0rem -0.5rem;padding: 0.3rem;"
										bind:this={notification_list}>
										{#if notifications.count > 0}
											{#each notifications.notify as notification}
												<a
													href={notification.link}
													on:click={fetchNotifications}>
													<div class="dropdown-item" style="display:flex;">
														<img
															data="{$Api['users.images']}{notification.author.avatar}"
															height="40px"
															width="40px"
															style="border-radius: 30px;margin-top:
															0.2rem;min-width: 40px;min-height: 40px;"
															alt="" />
														<div
															style="display: block;margin-left:
															0.4rem;line-height: 1.2;">
															<span
																style="color:
																var(--navbar-color);font-size:1rem;line-height:
																1;">
																<span style="font-weight: 500;">
																	{notification.title}
																</span>
															</span>
															{#if notification.category != 'follow' || notification.category != 'unfollow'}
																<span style="color: var(--link)">
																	{notification.body}
																</span>
															{/if}
															<span
																style="color: #828282; width: max-content;
																display: flex; margin-inline-start: auto;
																font-size: 0.6rem;margin-top: 0.3rem;
																margin-right: 0.2rem;ssss">
																{notification.time_ago} ago
															</span>
														</div>
													</div>
												</a>
											{/each}
										{:else}No Notifications{/if}
									</div>
								</div>
							{/if}

						</div>
					</div>
					<div class="navbar-item">
						<a href="/newpost" rel="prefetch">
							<i
								class="na-plus-circle"
								style="color:var(--navbar-color);display:block;margin-top:
								calc((30px - 19px )/2);" />
						</a>
					</div>
				{/if}
				<div class="navbar-item">
					<a href="/direct" rel="prefetch">
						<i
							class="na-comment"
							style="color:var(--navbar-color);display:block;margin-top:
							calc((30px - 19px )/2);" />
					</a>
				</div>
				<div
					class="navbar-item"
					style="cursor: pointer;"
					id="navbar_profile_image">
					<div bind:this={user_center} class="newapp-dropdown" id="user-center">
						<img
							data="{$Api['users.images']}{$User.avatar}"
							bind:this={user_image}
							id="user-image"
							height={p_image}
							width={p_image}
							onerror="this.style.visibility='none'"
							on:
							style="border-radius: 30px;margin-top: 1px;"
							alt="" />
						<div
							bind:this={user}
							class="newapp-dropdown-content"
							id="user"
							style="display: none;">
							<div class="dropdown-user" style="display:flex;cursor: default;">
								<img
									data="{$Api['users.images']}{$User.avatar}"
									id="user-dropdown-image"
									height="40px"
									width="40px"
									onerror="this.style.visibility='none'"
									style="border-radius: 30px;margin-top: 1px;"
									alt="" />
								<div class="info" style="margin-left: 0.5rem;line-height: 1.3;">
									<span>{$User.real_name}</span>
									<br />
									<span style="font-size:0.7rem;">@{$User.name}</span>
								</div>
							</div>
							<hr />
							<a href="/user/{$User.name}" style="color: var(--navbar-color);">
								<div class="dropdown-item" on:click={CloseMenu}>
									<i class="na-user" />
									<span>Profile</span>
									<i class="na-chevron-right" />
								</div>
							</a>
							{#if $DeviceType == 'mobile'}
								<a href="/notifications" style="color: var(--navbar-color);">
									<div class="dropdown-item" on:click={CloseMenu}>
										<i class="na-bell" />
										<span>Notifications</span>
										<i class="na-chevron-right" />
									</div>
								</a>
								<a href="/newpost" style="color: var(--navbar-color);">
									<div class="dropdown-item" on:click={CloseMenu}>
										<i class="na-plus-circle" />
										<span>New Post</span>
										<i class="na-chevron-right" />
									</div>
								</a>
							{/if}
							{#if $User.permissions.admin == true}
								<a
									rel="preload"
									href="/admin"
									style="color: var(--navbar-color);">
									<div class="dropdown-item" on:click={CloseMenu}>
										<i class="na-user-shield" />
										<span>Admin</span>
										<i class="na-chevron-right" />
									</div>
								</a>
							{/if}
							<a
								rel="preload"
								href="/saved"
								style="color: var(--navbar-color);">
								<div class="dropdown-item" on:click={CloseMenu}>
									<i class="na-inbox-in" />
									<span>Saved</span>
									<i class="na-chevron-right" />
								</div>
							</a>
							<div class="dropdown-item">
								<i class="na-moon" />
								<span>Dark Theme</span>
								<div class="toggle-theme">
									<span
										class="toggle {$User.theme == "Dark" ? "active" : ""}"
										bind:this={toggle}
										on:click={() => {
											ToggleTheme()
										}} />
								</div>
							</div>
							<span style="color: var(--navbar-color);">
								<div
									class="dropdown-item"
									on:click={() => {
										CloseMenu(), Auth.logout()
									}}>
									<i class="na-sign-out-alt" />
									<span>Logout</span>
								</div>
							</span>
						</div>
					</div>
				</div>
			{:else}
				<div
					class="navbar-item"
					style="margin-inline-start: auto;display:flex;margin-right: 0.5rem;">
					<span
						style="color:
						var(--navbar-color);margin-block-start:auto;margin-block-end:
						auto;cursor: pointer;"
						on:click={OpenModalLogin}>
						<span style="vertical-align: inherit;">
							<i class="na-sign-in-alt" />
							Login
						</span>
					</span>
				</div>
				<div
					class="navbar-item"
					style="cursor: pointer;"
					id="navbar_profile_image">
					<div bind:this={guest_center} class="newapp-dropdown" id="guest-center">
						<i class="na-cog" bind:this={settings_button} />
						<div
							bind:this={guest}
							class="newapp-dropdown-content"
							id="user"
							style="display: none;margin-top: 1rem;">
							<div class="dropdown-item">
								<i class="na-moon" />
								<span>Dark Theme</span>
								<div class="toggle-theme">
									<span
										class="toggle {$User.theme == "Dark" ? "active" : ""}"
										bind:this={toggle}
										on:click={() => {
											ToggleTheme()
										}} />
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
</nav>

{#if $User.auth == false}
	<Login />
	<Register />
	<Join />
{/if}
