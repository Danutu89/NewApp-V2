<script>
	import Chats from './components/Chats.svelte'
	import Chat from './components/Chat.svelte'

	export let data, async
</script>

<direct>
	{#if async}
		{#await async}
			<Chat />
		{:then data}
			<Chats chats={data['conversations']} />
			<Chat />
		{:catch error}
			<p style="color: red">{error.message}</p>
		{/await}
	{/if}
	{#if data instanceof Promise == false}
		<Chats chats={data['conversations']} />
		<Chat />
	{/if}
</direct>
