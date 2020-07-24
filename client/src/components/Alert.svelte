<script>
	import { onMount } from 'svelte'
	import { alert } from '../modules/Alert.js'
	import { goto } from '@sapper/app'

	let el

	onMount(() => {
		setTimeout(()=>{el.classList.add('active')}, 200)
		setTimeout(() => {
			//closeAlert()
		}, 4000)
	})

	function closeAlert(){
		el.classList.remove('active')
		setTimeout(() => {
			alert.set({
				active: false,
				img: null,
				type: 'icon',
				title: null,
				text: null,
				link: null,
			})
		}, 200)
	}
</script>

<style>
	alert {
		display: flex;
		padding: 0.5rem 0.8rem;
		background-color: var(--secondary-background);
		position: fixed;
		border-radius: 8px;
		bottom: 0;
		left: 0.5rem;
		-webkit-transform: translateY(60px);
		transform: translateY(60px);
		transition: transform 200ms linear;
		box-shadow: 5px 5px 11px 0px rgba(0, 0, 0, 0.2);
		color: var(--color);
		z-index: 5;
		cursor: pointer;
	}

	:global(alert.active) {
		-webkit-transform: translateY(-10px);
		transform: translateY(-10px);
	}

	alert .img {
		margin-right: 0.8rem;
		height: 40px;
		width: 30px;
		border-radius: 40px;
		display: flex;
	}

	alert .img img {
		top: 0;
		bottom: 0;
		left: 0;
		right: 0;
		margin: auto;
	}

	alert .img i {
		font-size: 1rem;
		margin: auto;
		background-color: var(--hover);
		padding: 0.5rem;
		border-radius: 30px;
	}

	alert .body {
		line-height: 1.35;
		font-family: sans-serif;
	}

	alert .close {
		line-height: 1;
		margin: auto;
		cursor: pointer;
		
		margin-left: 0.8rem;

	}
</style>

<alert bind:this={el}>
	<div
		class="img"
		on:click={() => {
			closeAlert()
			goto($alert.link)
		}}>
		{#if $alert.type == 'image'}
		<img data={$alert.img} alt="logo" height="35px" />
		{:else}
		<i class="{$alert.img}" style="{$alert.success ? "color:#00ff20;" : "color:#ff0000;"}"/>
		{/if}
	</div>
	<div
		class="body"
		style=" {$alert.title ? "" : "display:flex;"}"
		on:click={() => {
			closeAlert()
			goto($alert.link)
		}}>
		{#if $alert.title}
		<div class="title">{$alert.title}</div>
		{/if}
		<div class="text" style="{$alert.title ? "" : "margin: auto;"}">{$alert.text}</div>
	</div>
	<div
		class="close"
		on:click={() => {
			closeAlert()
		}}>
		<i class="na-times-circle" />
	</div>
</alert>
