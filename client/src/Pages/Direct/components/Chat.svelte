<script>
import {onMount, onDestroy} from 'svelte';
import {instance} from '../../../modules/Requests.js';
import {socket} from '../../../modules/SocketIO.js';
import {user as User, currentChat, deviceType as DeviceType} from '../../../modules/Store';
import {loadChat, SendMessage} from '../actions/actions.js';
let messages;
let text;
let _document;

function goBack(){
    var directElement = document.querySelector("direct");
    if(directElement.style.transform)
        directElement.style.transform = "";

    if($currentChat)
        socket.emit("leave_room", {
            room: $currentChat.room
        });

    currentChat.reset();
    
}

onMount(async ()=>{
    socket.on("connect", function() {
        socket.on("get_message", function(data){
            var mine;

            if(data.author.name == $User.name){
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
    _document = document;
    document.addEventListener('changedChat', async()=>{messages= await loadChat()});

    loadChat();
    if ($currentChat.id){
        
    }

});

onDestroy(async()=>{
    if($currentChat)
        socket.emit("leave_room", {
            room: $currentChat.room
        });
        //currentChat.reset();
    if(_document){
        _document.removeEventListener('changedChat', async()=>{messages = await loadChat()});
    }
});
 
</script>
<div class="conversation">
    {#if $currentChat.id != null}
        <div class="header">
            <div class="user">
                <i class="na-chevron-left" on:click={goBack} style="margin-right: 1rem;font-size: 1.5rem;top: 0;bottom: 0;margin: auto 0.5rem;color: var(--color);"></i>
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
                {#if message.new_day == true || message.new_day_from_last == true}
                    <div class="date-splitter" style="display: flex">
                        <hr>
                        <span style="width: calc({message.on.length} * 0.8rem)">{message.on}</span>
                        <hr>
                    </div>
                {/if}
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
            <button on:click={()=>{SendMessage(messages, text)}}>Send</button>
        </div>
    {/if}
</div>