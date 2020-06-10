<script>
import View from './View.svelte';
import {onMount, beforeUpdate} from 'svelte';
import {isSSR, lPage} from '../../modules/Preloads.js';
import { instance } from '../../modules/Requests.js';
import {user} from '../../modules/Store';
import { stores, goto } from '@sapper/app';
import {currentApi} from '../../modules/Store';
const { page } = stores();

export let mode;
let data = $currentApi.data;
let async = undefined, posts = undefined;

function LoadData(){
    if($isSSR) {
        isSSR.set(false);
        data = $currentApi.json;
    } else{
        posts = async () => {
            data = $currentApi.data;
            const response = await data;
            if(response.status == 200) {
                const responseJson = await response;
                return responseJson.data;
            } else {
                throw new Error("Something went wrong");
            }
        }
        async = posts();
    }
}

onMount(async ()=>{
    LoadData();

    document.addEventListener("urlPathUpdated", PageUpdated);
})

function PageUpdated(e){
    LoadData();
}


</script>



<View mode={mode} data={data} async={async} logged={$user.auth}/>