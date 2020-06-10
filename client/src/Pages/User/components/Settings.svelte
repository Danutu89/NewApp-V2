<script>
import Select from 'svelte-select';
import {instance} from '../../../modules/Requests.js';
import {user as User, api as Api} from '../../../modules/Store';
import {getSettings, getJsonDiff} from '../modules';
import { onMount } from 'svelte';
import Cookie from 'cookie-universal';
const cookies = Cookie();
var jwt_decode = require('jwt-decode');

export let user;

let decoded=false;

let editInfo, editMisc;
let s_real_name=user.real_name,
    s_email=user.email,
    s_bio=user.bio,
    s_profession=user.profession,
    s_i=user.instagram,
    s_f=user.facebook,
    s_t=user.twitter,
    s_g=user.github,
    s_w=user.website;
let s_genre=user.genre,
    s_theme_mode=user.theme_mode,
    s_theme=user.theme;
let s_avatarimg, s_coverimg;
let c_coverimg,c_avatarimg;
let isMobile;
let settings, settings_base = {};

function SwitchPanel(panel){
    if (panel === 'misc'){
      if(isMobile){
        editInfo.style['display'] = 'none';
        editMisc.style['display'] = 'block';
      }else{
        editInfo.style['display'] = 'none';
        editMisc.style['display'] = 'flex';
      }
    }else if(panel === 'main'){
      if(isMobile){
        editInfo.style['display'] = 'block';
        editMisc.style['display'] = 'none';
      }else{
        editInfo.style['display'] = 'flex';
        editMisc.style['display'] = 'none';
      }
    }
}

async function SaveSettings(){
  var token = $User.token;
  let formdata = new FormData();

  try {
      formdata.append('avatarimg', s_avatarimg.files[0], s_avatarimg.files[0].name);
      c_avatarimg = true;
  } catch (error) {
      c_avatarimg = false;
  }

  try {
      formdata.append('coverimg', s_coverimg.files[0], s_coverimg.files[0].name);
      c_coverimg = true;
  } catch (error) {
      c_coverimg = false;
  }

  formdata.append('data', JSON.stringify(settings_base));

  const resp = await instance.post($Api['users.settings'], formdata, {headers: {'Content-Type': 'multipart/form-data'}}).then((response)=>{
    return response;
  })

  if (resp.status != 200){
    //alert
    return;
  }

  try {
    decoded = jwt_decode(resp.data['token']);
  } catch (error) {
    decoded = false;
  }

  if (decoded != false){
    cookies.set("token", resp.data['token'],{maxAge:60 * 60 * 24 * 30, path: '/'});
    User.set({
        name: decoded.name,
        email: decoded.email,
				avatar: decoded.avatar,
				real_name: decoded.real_name,
				permissions: decoded.permissions,
				theme: decoded.theme,
				theme_mode: decoded.theme_mode,
				auth: true
			})
  }else{
    //alert
    return;
  }

  goto('/user/'+user.name);
}

onMount(async function(){
  settings = await getSettings();
  
  isMobile = window.matchMedia("only screen and (max-width: 800px)").matches;
  s_coverimg = document.getElementById('coverimg');
  s_avatarimg = document.getElementById('avatarimg');
})

function showEdit(input){
  var _input = document.getElementById(input);
  var _text = document.getElementById(input+'_text');
  if (_input.style.display == 'none'){
    _input.style.display = 'inherit';
    _text.style.display = 'none';
  }else{
    _input.style.display = 'none';
    _text.style.display = 'block';
  }

}
function UpdateSttings(setting){
  if(typeof setting.value == 'object')
    settings_base[setting.key] = setting.value.value;
  else  
    settings_base[setting.key] = setting.value;
}

</script>
<div class="sidebar-main">
    <div class="edit-info" id="main" bind:this={editInfo} style="width: auto;">
          {#if settings}
            <div class="col-1" style="text-align:left;">
            {#each settings['text_input'] as setting}
              <div style="display: flex;margin-bottom:1rem;">
                <input id="{setting.key}" name="{setting.key}" on:change|preventDefault={()=>{UpdateSttings(setting)}} placeholder="{setting.name}" type="text"
                    style="display: none;margin-bottom:0;margin-right:0.5rem;" bind:value={setting.value}>
                <p style="font-weight: 500;margin: 0.1em 0;" id="{setting.key}_text">{setting.name}: {setting.value}</p>
                <span class="modify-button na-pencil-alt" on:click={()=>showEdit(setting.key)}></span>
              </div>
            {/each}
            {#each settings['custom_input'] as setting}
              <div style="display: flex;margin-bottom:1rem;">
                <div class="input-group" style="display: none;margin-bottom:0;margin-right:0.5rem;" id="{setting.key}">
                    <div class="input-group-icon" style="margin-bottom:0;">{setting.placeholder}</div>
                    <div class="input-group-area" style="display: flex;"><input id="{setting.key}" name="{setting.key}" on:change|preventDefault={()=>{UpdateSttings(setting)}}  placeholder="{setting.name}" type="text"
                            style="margin-bottom:0;" bind:value={setting.value}></div>
                </div>
                <p style="font-weight: 500;margin: 0.1em 0;" id="{setting.key}_text">{setting.name}: {setting.value}</p>
                <span class="modify-button na-pencil-alt" on:click={()=>showEdit(setting.key)}></span>
            </div>
            {/each}
            </div>
            <div class="col-2" style="text-align:left;">
              {#each settings['selectable'] as setting}
                <div style="display: flex;margin-bottom:1rem;">
                  <Select items={setting.values} on:select={(value)=>{UpdateSttings(setting)}} Id={setting.key} containerStyles={"width: calc(100% - 3.4rem);display: none"} bind:selectedValue={setting.value}></Select>
                  <p style="font-weight: 500;margin: 0.1em 0;" id="{setting.key}_text">{setting.name}: {setting.value.value}</p>
                  <span class="modify-button na-pencil-alt" on:click={()=>showEdit(setting.key)}></span>
                </div>
              {/each}
               Avatar:
              <br>
              <input type="file" name="avatarimg" id="avatarimg">
              <br>
              Cover:
              <br>
              <input type="file" name="coverimg" id="coverimg">
              </div>
              <button on:click={SaveSettings}>Save</button>
          {/if}
    </div>
    <div class="edit-misc" id="misc" bind:this={editMisc}>
        <div class="col-1" style="text-align:left;">

            <input id="theme_mode" name="theme_mode" type="checkbox" bind:value={s_theme_mode}> Get theme from the system
            <br>
            Theme:
            <br>
            <select id="theme" name="theme" bind:value={s_theme}>
                <option value="Light">Light</option>
                <option value="Dark">Dark</option>
            </select>
        </div>
        <div class="col-2" style="text-align:left;"></div>
    </div>
</div>