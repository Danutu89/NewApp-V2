<script>
	import SideBarLeft from '../../components/SideBarLeft.svelte'
	import SideBarRight from '../../components/SideBarRight.svelte'
	import Posts from '../../components/Posts.svelte'
	import LSideBarLeft from '../../components/Loading/SideBarLeft.svelte'
	import LSideBarRight from '../../components/Loading/SideBarRight.svelte'
	import LPosts from '../../components/Loading/Posts.svelte'

	export let async, data, mode, logged
</script>

{#if async}
	{#await async}
		<LSideBarLeft />
		<LPosts />
		<LSideBarRight page={'index'} />
	{:then data}
		{#if logged}
			<SideBarLeft user={data.user} utilities={data.utilities} />
		{:else}
			<SideBarLeft utilities={data.utilities} />
		{/if}
		<Posts data={data.posts} {mode} />
		<SideBarRight trending={data.trending} page={'index'} />
	{:catch error}
		<p style="color: red">{error.message}</p>
	{/await}
{/if}
{#if data instanceof Promise == false}
	{#if logged}
		<SideBarLeft user={data.user} utilities={data.utilities} />
	{:else}
		<SideBarLeft utilities={data.utilities} />
	{/if}
	<Posts data={data.posts} {mode} />
	<SideBarRight trending={data.trending} page={'index'} />
{/if}
