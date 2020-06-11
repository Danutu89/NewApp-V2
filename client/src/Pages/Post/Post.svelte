<script>
import View from './View.svelte';
import {onMount, onDestroy} from 'svelte';
import {isSSR} from '../../modules/Preloads.js';
import {currentApi} from '../../modules/Store';
import { stores } from '@sapper/app';
const { page } = stores();

export let data;
let async = undefined, posts = undefined;

function LoadData(){
    if($isSSR) {
        isSSR.set(false);
    } else if(data instanceof Promise) {
        posts = async () => {
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


<View data={data} async={async} page={$page}/>