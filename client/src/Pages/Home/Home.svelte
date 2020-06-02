<script>
import View from './View.svelte';
import {onMount, beforeUpdate} from 'svelte';
import {isSSR, lPage} from '../../modules/Preloads.js';
import { instance } from '../../modules/Requests.js';
import {user} from '../../modules/Store';
import { stores, goto } from '@sapper/app';
const { page } = stores();

export let data, mode;
let async = undefined, posts = undefined;

function LoadData(){
    let loadEvent = new CustomEvent('reloaded');
    if($isSSR && $lPage.refresh == false) {
        isSSR.set(false);
    } else if(data instanceof Promise || $lPage.refresh == true) {
        posts = async () => {
            let promise, response;
            if($lPage.refresh){
                if($page.path == '/search')
                    promise = $lPage.data+''+$page.query.q;
                else if($page.path == '/tag/'+$page.params.slug)
                   promise = $lPage.data+''+$page.params.slug;
                else
                    promise = $lPage.data;
                response = await instance.get(promise);
            }
            else
                response = await data;
            if(response.status == 200) {
                const responseJson = await response;
                if($lPage.refresh == true)
                    document.dispatchEvent(loadEvent);
                lPage.set({data: $lPage.data, refresh: false});
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