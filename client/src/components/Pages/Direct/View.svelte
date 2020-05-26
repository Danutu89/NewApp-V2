<script>
import Chats from './components/Chats.svelte';
import Chat from './components/Chat.svelte';
import {lPage} from '../../../modules/Preloads.js';

export let data, async;

</script>

<direct>
    {#if async}
        {#await async}
        <Chat/>
        {:then data}
        <Chats chats={data['conversations']}/>
        <Chat/>
        {:catch error}
        <p style="color: red">{error.message}</p>
        {/await}
    {/if}
    {#if (data instanceof Promise) == false && $lPage.refresh == false}
        <Chats chats={data['conversations']}/>
        <Chat/>
    {/if}
</direct>