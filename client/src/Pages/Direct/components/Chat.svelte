<script>
import {onMount, onDestroy} from 'svelte';
import {currentChat} from '../modules/currentChat.js';
import {instance} from '../../../modules/Requests.js';
import {socket} from '../../../modules/SocketIO.js';
import {user as User} from '../../../modules/Store';
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
        token: $User.token,
        text: text,
        author: {
            avatar: $User.avatar,
            name: $User.name,
            realname: $User.real_name
        },
        room: $currentChat.room,
        id: $currentChat.id,
        last_date: messages[messages.length -1].datetime
    })
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
});

onDestroy(async()=>{
    if($currentChat)
        socket.emit("leave_room", {
            room: $currentChat.room
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
            <button on:click={SendMessage}>Send</button>
        </div>
    {/if}
</div>