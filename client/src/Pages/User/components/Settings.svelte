<script>
import Select from 'svelte-select';
import {instance} from '../../../modules/Requests.js';
import {user as User, api as Api, deviceType as DeviceType} from '../../../modules/Store';
import {getSettings, settings_modified} from '../modules';
import { onMount } from 'svelte';
let decoded=false;

let c_avatarimg, c_coverimg;
let editInfo, editMisc;
let settings, settings_base = {};

function SwitchPanel(panel){
    if (panel === 'misc'){
      if($DeviceType == 'mobile'){
        editInfo.style['display'] = 'none';
        editMisc.style['display'] = 'block';
      }else{
        editInfo.style['display'] = 'none';
        editMisc.style['display'] = 'flex';
      }
    }else if(panel === 'main'){
      if($DeviceType == 'mobile'){
        editInfo.style['display'] = 'block';
        editMisc.style['display'] = 'none';
      }else{
        editInfo.style['display'] = 'flex';
        editMisc.style['display'] = 'none';
      }
    }
}

onMount(async function(){
  settings = await getSettings();
  
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
  settings_modified.set(settings_base);
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
              <input type="file" on:change|preventDefault={()=>{UpdateSttings({'key': 'avatar', value: true})}} name="avatarimg" id="avatarimg">
              <br>
              Cover:
              <br>
              <input type="file" on:change|preventDefault={()=>{UpdateSttings({'key': 'cover', value: true})}} name="coverimg" id="coverimg">
              </div>
          {/if}
    </div>
</div>