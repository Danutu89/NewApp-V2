<script>
import SideBarLeft from '../../SideBarLeft.svelte';
import SideBarRight from '../../SideBarRight.svelte';
import Posts from '../../Posts.svelte';
import LSideBarLeft from '../../Loading/SideBarLeft.svelte';
import LSideBarRight from '../../Loading/SideBarRight.svelte';
import LPosts from '../../Loading/Posts.svelte';
import {lPage} from '../../../modules/Preloads.js';

export let async, data, mode;
</script>

{#if async}
    {#await async}
    <LSideBarLeft/>
    <LPosts/>
    <LSideBarRight page={"index"}/>
    {:then data}
    <SideBarLeft user={data.user} utilities={data.utilities}/>
    <Posts data={data.posts} mode={mode}/>
    <SideBarRight trending={data.trending} page={"index"}/>
    {:catch error}
    <p style="color: red">{error.message}</p>
    {/await}
{/if}
{#if (data instanceof Promise) == false && $lPage.refresh == false}
    <SideBarLeft user={data.user} utilities={data.utilities}/>
    <Posts data={data.posts} mode={mode}/>
    <SideBarRight trending={data.trending} page={"index"}/>
{/if}