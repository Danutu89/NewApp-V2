<script>
	import Auth from '../modules/Auth'
	import { onMount } from 'svelte'
	import { stores } from '@sapper/app'
	var jwt_decode = require('jwt-decode')

	let l_modal
	let r_modal
	let username = '',
		password = ''
	let username_c, password_c
	let check
	let decoded

	onMount(async function () {
		r_modal = document.getElementById('register-modal')
	})

	function CloseModalLogin() {
		if(document && l_modal)
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

	function OpenRegister() {
		l_modal.style['visibility'] = 'hidden'
		l_modal.style['opacity'] = 0
		l_modal.style['pointer-events'] = 'none'
		r_modal.style['visibility'] = 'visible'
		r_modal.style['opacity'] = 1
		r_modal.style['pointer-events'] = 'auto'
	}

	async function Login() {
		if (!username) {
			username_c.setCustomValidity('Please fill out this field.')
			username_c.focus()
			username_c.classList.add('error')
			username_c.reportValidity()
			return
		}
		if (!password) {
			password_c.setCustomValidity('Please fill out this field.')
			password_c.focus()
			password_c.classList.add('error')
			password_c.reportValidity()
			return
		}

		var login_check = await Auth.login(username, password)
		check = login_check.data.login

		if (login_check.status != 200) {
			if (login_check.data.camp == 'user') {
				username_c.setCustomValidity(check)
				username_c.focus()
				username_c.classList.add('error')
				username_c.reportValidity()
				return
			} else if (login_check.data.camp == 'password') {
				password_c.setCustomValidity(check)
				password_c.focus()
				password_c.classList.add('error')
				password_c.reportValidity()
				return
			} else {
				username_c.focus()
				username_c.classList.add('error')

				password_c.focus()
				password_c.classList.add('error')

				return
			}
		}

		CloseModalLogin()
	}

	function handleKeydown(event) {
		if (event.keyCode == 13) {
			Login()
		}
	}
</script>

<modal id="login-modal" bind:this={l_modal}>
	<div class="modal" on:keydown={handleKeydown} id="login-modal-inner">
		<span
			on:click={CloseModalLogin}
			class="close-modal"
			style="font-size: 0.7rem;cursor:pointer;">
			Close
		</span>
		<div class="modal-header">
			<img
				style="vertical-align: middle;"
				onerror="this.style.display='none'"
				data="https://newappcdn.b-cdn.net/images/logo.svg"
				width="70"
				alt="" />
			<br />
			<span style="color:var(--color)">
				<span style="color:#18BC9C;">New</span>
				App - Login
			</span>
		</div>
		<div class="modal-content">
			<input
				id="username_login"
				name="username_login"
				placeholder="Username/Email"
				required="true"
				type="text"
				bind:value={username}
				bind:this={username_c} />
			<input
				id="password_login"
				name="password_login"
				placeholder="Password"
				required="true"
				type="password"
				bind:value={password}
				bind:this={password_c} />
			<span style="font-size: 0.6rem;color:var(--color)">
				Forgot password?
				<a href="#reset-password-modal">Click Here</a>
			</span>
		</div>
		<div class="modal-footer">
			<span style="font-size: 0.6rem;color:var(--color)">
				You don`t have an account?
				<span style="color:#18BC9C;cursor:pointer;" on:click={OpenRegister}>
					Register here
				</span>
			</span>
			<button type="submit" class="modal-button" on:click={Login}>Login</button>
		</div>
	</div>
</modal>
