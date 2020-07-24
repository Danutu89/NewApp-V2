<script>
	import SidebarLeft from './components/SidebarLeft.svelte'
	import SidebarRight from './components/SidebarRight.svelte'
	import Main from './components/Main.svelte'
	import Settings from './components/Settings.svelte'
	import LSidebarLeft from './components/Loading/SidebarLeft.svelte'
	import LSidebarRight from './components/Loading/SidebarRight.svelte'
	import LMain from './components/Loading/Main.svelte'
	import { currentPage } from './modules'
	import { api as Api } from '../../modules/Store'

	export let async, data
</script>

<svelte:head>
	{#if async}
		{#await async}
			<title>Loading...</title>
		{:then data}
			<title>{data.info.full_name} - NewApp</title>
			<meta name="keywords" content="newapp,{data.name}" />
			<meta name="description" content="{data.name} - {data.bio}" />
			<meta property="og:type" content="website" />
			<meta property="og:url" content="/user/{data.name}" />
			<meta property="og:site_name" content={data.name} />
			<meta
				property="og:image"
				itemprop="image primaryImageOfPage"
				content={data.avatar} />
			<meta property="og:description" content={data.bio} />
			<meta name="twitter:title" content={data.name} />
			<meta name="twitter:description" content={data.bio} />
			<meta name="twitter:image:src" content={data.avatar} />
		{/await}
	{/if}
	{#if data instanceof Promise == false}
		<title>{data.info.full_name} - NewApp</title>
		<meta name="keywords" content="newapp,{data.name}" />
		<meta name="description" content="{data.name} - {data.bio}" />
		<meta property="og:type" content="website" />
		<meta property="og:url" content="/user/{data.name}" />
		<meta property="og:site_name" content={data.name} />
		<meta
			property="og:image"
			itemprop="image primaryImageOfPage"
			content={data.avatar} />
		<meta property="og:description" content={data.bio} />
		<meta name="twitter:title" content={data.name} />
		<meta name="twitter:description" content={data.bio} />
		<meta name="twitter:image:src" content={data.avatar} />
	{/if}
</svelte:head>

<profile class="profile-page">
	{#if async}
		{#await async}
			<div
				class="profile-cover"
				style="background-color: #14947b;border: var(--border);height:350px;" />
			<div class="profile-main">
				<LSidebarLeft />
				<LMain />
				<LSidebarRight />
			</div>
		{:then data}
			{#if data.info.cover_img}
				<div
					class="profile-cover"
					style="background-image: url({$Api['users.images']}{data.info.cover_img});background-position:
					center;background-size: cover;border: var(--border);height:450px;" />
			{:else}
				<div
					class="profile-cover"
					style="background-color: #14947b;border: var(--border);height:350px;" />
			{/if}
			<div class="profile-main">
				<SidebarLeft user={data} />
				{#if $currentPage == 'settings'}
					<Settings user={data} />
				{:else}
					<Main user={data} />
				{/if}

				<SidebarRight user={data} />
			</div>
		{:catch error}
			<p style="color: red">{error.message}</p>
		{/await}
	{/if}
	{#if data instanceof Promise == false}
		{#if data.info.cover_img}
			<div
				class="profile-cover"
				style="background-image: url({$Api['users.images']}{data.info.cover_img});background-position:
				center;background-size: cover;border: var(--border);height:450px;" />
		{:else}
			<div
				class="profile-cover"
				style="background-color: #14947b;border: var(--border);height:350px;" />
		{/if}
		<div class="profile-main">
			<SidebarLeft user={data} />
			{#if $currentPage == 'settings'}
				<Settings user={data} />
			{:else}
				<Main user={data} />
			{/if}
			<SidebarRight user={data} />
		</div>
	{/if}
</profile>
