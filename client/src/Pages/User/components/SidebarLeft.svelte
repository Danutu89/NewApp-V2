<script>
import {instance} from '../../../modules/Requests.js';
import OpenJoin from '../../../modules/OpenJoin.js';
import {user as User, api as Api, currentChat} from '../../../modules/Store';
import {currentPage} from '../modules';
import {goto} from '@sapper/app';

export let user;

let follow_button;

function Follow_User() {
  if ($User.auth) {
    if ($User.id != user.id) {
      instance.get($Api['follow.user'] + user.id)
        .then(response => {
          if (response.data['operation'] == 'unfollowed') {
            follow_button.innerHTML = 'Follow';
          } else if (response.data['operation'] == 'followed') {
            follow_button.innerHTML = '&#x2713 Following';
          }

        })
    }
  } else {
    OpenJoin();
  }
}

async function goToDirect(){
  var chat = await instance.post($Api['direct.index'], {users: user.name, ids: user.id}).then(res =>{
    return res.data
  })

  currentChat.set(chat['current']);

  goto('/direct');
}
</script>


<div class="sidebar-info">
  <div class="profile-image">
    <div>
      <div class="profile-photo" style="background-image: url({user.avatar});background-position: center center;
            background-size: cover;
            border: var(--border);
            height: 200px;
            width: 200px;
            border-radius: 100px;
            border: 3px solid var(--background);
                left: 0;
            right: 0;
            margin: auto;">
      </div>
    </div>

    <div class="user-name" style="line-height: 1.7rem;">
      <h1 style="font-weight: 400;">{user.real_name}</h1>
      <h4 style="font-weight: 400;">@{user.name}</h4>
    </div>
  </div>
  <div class="profile-actions">
    {#if $User.auth}
    {#if $User.id == user.id}
    {#if $currentPage == "settings"}
    <button class="follow-user" id="settings-user-{user.id}" on:click={()=>{currentPage.set("main")}}>Profile</button>
    {:else}
    <button class="follow-user" id="settings-user-{user.id}" on:click={()=>{currentPage.set("settings")}}>Settings</button>
    {/if}
    {:else}
    <button class="follow-user" bind:this={follow_button} on:click={Follow_User} id="follow-user-{user.id}">{#if user.info['following']}&#x2713 Following{:else}Follow{/if}</button>
    <button class="follow-user" style="margin-top: 0.5rem;" on:click={goToDirect}>Messages</button>
    {/if}
    {:else}
    <button class="follow-user" bind:this={follow_button} on:click={Follow_User} id="follow-user-{user.id}">Follow</button>
    {/if}
    
  </div>
  <div class="widgets">
    <div class="profile-presentation">
      <div class="header"><i class="na-globe"></i> Presentation</div>
      <div class="bio">{user.bio}</div>
      <div class="info">
        {#if user.profession != 'None' && user.profession }
        <p><i class="na-briefcase"></i> Profession {user.profession}</p>
        {/if}
        <p><i class="na-home"></i> From {user.country_name} <span class="flag-icon flag-icon-{user.country_flag}"></span></p>
        <p><i class="na-clock"></i> Joined on {user.join_date}</p>
        <p><i class="na-rss"></i> Followed by {user.followed_count} people</p>
      </div>
    </div>
    {#if user.tags_check}
    <div class="interesed-tags">
      <div class="header"><i class="na-hashtag"></i> Interesed Tags</div>
      <div class="tags">
        {#each user.tags as tag}
              <a style="text-decoration: none;" title="{tag}" href="/tag/{tag}"><span
                  style="font-size: 12px;">{tag}</span></a>
                  <br>
              {/each}
      </div>
    </div>
    {/if}
    {#if user.social }
    <div class="social">
      <div class="header"><i class="na-users"></i> Social</div>
      <div class="links">
        {#if user.facebook }
        <div style="margin-bottom: 0.3rem">
        <a style="text-decoration: none;"  href="https://facebook.com/{user.facebook}"><span
          style="font-size: 0.85rem;"><i class="na-facebook-square" style="font-size: 1rem;"></i> @{user.facebook}</span></a>
        </div>
        {/if}
        {#if user.instagram }
        <div style="margin-bottom: 0.3rem">
        <a style="text-decoration: none;" href="https://instagram.com/{user.instagram}"><span
          style="font-size: 0.85rem;"><i class="na-instagram" style="font-size: 1rem;"></i> @{user.instagram}</span></a>
        </div>
        {/if}
        {#if user.twitter }
        <div style="margin-bottom: 0.3rem">
        <a style="text-decoration: none;" href="https://twitter.com/{user.twitter}"><span
          style="font-size: 0.85rem;"><i class="na-twitter" style="font-size: 1rem;"></i> @{user.twitter}</span></a>
        </div>
        {/if}
        {#if user.github }
        <div style="margin-bottom: 0.3rem">
        <a style="text-decoration: none;" href="https://github.com/{user.github}"><span
          style="font-size: 0.85rem;"><i class="na-github" style="font-size: 1rem;"></i> @{user.github}</span></a>
        </div>
        {/if}
        {#if user.website }
        <div style="margin-bottom: 0.3rem">
            <a style="text-decoration: none;" href="{user.website}"><span
              style="font-size: 0.85rem;"><i class="na-globe" style="font-size: 1rem;"></i> {user.website}</span></a>
              
        </div>
        {/if}
      </div>
    </div>
    {/if}
  </div>
</div>