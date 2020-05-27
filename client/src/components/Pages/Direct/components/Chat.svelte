<script>
import {onMount} from 'svelte';
import {currentChat} from '../modules/currentChat.js';
import {instance} from '../../../../modules/Requests.js';
import {socket} from '../../../../modules/SocketIO.js';
import { stores } from '@sapper/app';
const { session } = stores();
let messages;
let text;

$: if ($currentChat){
    loadChat();
}

async function loadChat(){
    const res = await instance.get("/api/direct/mess/"+$currentChat.id);
    const json = await res.data;
    messages = json;
    socket.emit("join", {
        room: $currentChat.room
    })
    
}

async function SendMessage(){

    socket.emit("send_message", {
        token: $session.token,
        text: text,
        author: {
            avatar: $session.avatar,
            name: $session.name,
            realname: $session.real_name
        },
        room: $currentChat.room,
        id: $currentChat.id
    })
}

onMount(async ()=>{
    socket.on("connect", function() {
        socket.on("get_message", function(data){
            console.log(1);
            
            var mine;

            if(data.author.name == $session.name){
                mine = true;
            }else{
                mine = false;
            }

            var message = {
                mine: mine,
                created_on: data.created_on,
                author: data.author,
                text: data.text
            }

            messages = [...messages, message];
        })
    });
});
 
</script>
<div class="conversation">
    {#if $currentChat}
        <div class="header">
            <div class="user">
                <div class="img"><img data="{$currentChat.members[0].avatar}" alt="profile image" height="40px" width="40px"></div>
                <div class="info">
                    <span style="font-size: 1.1rem;font-weight: 500;">{$currentChat.members[0].real_name}</span>
                    <span>@{$currentChat.members[0].name}</span>
                </div>
            </div>
        </div>
        <div class="chat">
        {#if messages}
            {#each messages as message}
                {#if message.mine == true}
                    <div class="mine-message">
                        <div class="user-img">
                            <img class="profile_image" data="{message.author.avatar}" height="40px" width="40px" alt="profile image">
                        </div>
                        <div class="user-msg">
                            <span>{message.text}</span>
                        </div>
                    </div>
                {:else}
                    <div class="not-mine-message">
                        <div class="user-img">
                            <img class="profile_image" data="{message.author.avatar}" height="40px" width="40px" alt="profile image">
                        </div>
                        <div class="user-msg">
                            <span>{message.text}</span>
                        </div>
                    </div>
                {/if}
            {/each}
        {/if}
        </div>
        <div class="message">
            <div class="textarea">
                <textarea bind:value={text} type="text" name="message" id="message" style="margin-bottom: 0;min-height: 1.2rem;" contenteditable></textarea>
            </div>
            <button on:click={SendMessage}>Send</button>
        </div>
    {/if}
</div>