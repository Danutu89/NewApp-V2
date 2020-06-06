<script>
import {socket} from '../../../modules/SocketIO.js';
import {onMount} from 'svelte';
import {currentChat, deviceType as DeviceType} from '../../../modules/Store';

export let chats;

function gotoChat(chat){
    var directElement = document.querySelector("direct");
    if($DeviceType == "mobile")
        directElement.style.transform = "translate3d(-100vw, 0px, 0px)";
    currentChat.set(chat);
    document.dispatchEvent(new CustomEvent("changedChat"));
    
}

function checkScreen(){
    var directElement = document.querySelector("direct");
    if($DeviceType != "mobile")
        if(directElement.style.transform)
            directElement.style.transform = "";
    
    else if($currentChat.id){  
        if($DeviceType == "mobile")
            directElement.style.transform = "translate3d(-100vw, 0px, 0px)";
    }
}

onMount(()=>{
    document.addEventListener("changedDeviceType", checkScreen)
    checkScreen();
})

</script>
<div class="conversations">
    <div class="header">
        <span>Direct</span>
    </div>
    <div class="users">
        {#each chats as chat}
        <div class="user-conv" on:click={()=>{gotoChat(chat)}}>
            <div class="conv-img">
                <img class="profile_image" data="{chat.members[0].avatar}" height="40px" width="40px" alt="profile image">
            </div>
            <div class="conv-info">
                <span class="username" style="font-weight: 600;">{chat.members[0].real_name}</span>
                <span class="message">{chat.last_message.text}</span>
            </div>
        </div>
        {/each}
    </div>
</div>