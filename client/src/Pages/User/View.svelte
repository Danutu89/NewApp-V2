<script>
import SidebarLeft from './components/SidebarLeft.svelte';
import SidebarRight from './components/SidebarRight.svelte';
import Main from './components/Main.svelte';
import LSidebarLeft from './components/Loading/SidebarLeft.svelte';
import LSidebarRight from './components/Loading/SidebarRight.svelte';
import LMain from './components/Loading/Main.svelte';
import {lPage} from '../../modules/Preloads.js';

export let async, data;
</script>


<svelte:head>
{#if async}
        {#await async}
        <title>Loading...</title>
        {:then data}
        <title>{data.real_name} - NewApp</title>
        <meta name="keywords" content="newapp,{data.name}">
        <meta name="description" content="{data.name} - {data.bio}">
        <meta property="og:type" content="website">
        <meta property="og:url" content="/user/{data.name}">
        <meta property="og:site_name" content="{data.name}">
        <meta property="og:image" itemprop="image primaryImageOfPage" content="{data.avatar}">
        <meta property="og:description" content="{data.bio}">
        <meta name="twitter:title" content="{data.name}">
        <meta name="twitter:description" content="{data.bio}">
        <meta name="twitter:image:src" content="{data.avatar}">
        {/await}
{/if}
{#if (data instanceof Promise) == false && $lPage.refresh == false}
    <title>{data.real_name} - NewApp</title>
    <meta name="keywords" content="newapp,{data.name}">
    <meta name="description" content="{data.name} - {data.bio}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="/user/{data.name}">
    <meta property="og:site_name" content="{data.name}">
    <meta property="og:image" itemprop="image primaryImageOfPage" content="{data.avatar}">
    <meta property="og:description" content="{data.bio}">
    <meta name="twitter:title" content="{data.name}">
    <meta name="twitter:description" content="{data.bio}">
    <meta name="twitter:image:src" content="{data.avatar}">
{/if}
</svelte:head>

<profile class="profile-page">
    {#if async}
        {#await async}
        <div class="profile-cover" style="background-color: #14947b;border: var(--border);height:350px;"></div>
        <div class="profile-main">
            <LSidebarLeft/>
            <LMain/>
            <LSidebarRight/>
        </div>
        {:then data}
            {#if data.cover}
            <div class="profile-cover" style="background-image: url({data.cover});background-position: center;background-size: cover;border: var(--border);height:450px;"></div>
            {:else}
            <div class="profile-cover" style="background-color: #14947b;border: var(--border);height:350px;"></div>
            {/if}
            <div class="profile-main">
                <SidebarLeft user={data}/>
                <Main user={data}/>
                <SidebarRight user={data}/>
            </div>
        {:catch error}
        <p style="color: red">{error.message}</p>
        {/await}
    {/if}
    {#if (data instanceof Promise) == false && $lPage.refresh == false}
        {#if data.cover}
        <div class="profile-cover" style="background-image: url({data.cover});background-position: center;background-size: cover;border: var(--border);height:450px;"></div>
        {:else}
        <div class="profile-cover" style="background-color: #14947b;border: var(--border);height:350px;"></div>
        {/if}
        <div class="profile-main">
            <SidebarLeft user={data}/>
            <Main user={data}/>
            <SidebarRight user={data}/>
        </div>
    {/if}
</profile>