<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR, lPage } from '../modules/Preloads.js';
    import {user, get} from '../modules/Store';
    lPage.set({data: '/api/home?mode=saved', refresh: false});
    export async function preload(page){
        let isSSRPage;
        if(get(user).auth === false){
            this.redirect(302,'/');
        }

        const res = instance.get('/api/direct');
        lPage.set({data: '/api/direct', refresh: false});
        isSSR.subscribe(value => {
            isSSRPage = value;
        })();

        if(!isSSRPage) {
            return { data: res };
        }

        const json = await res.then(function (response) {
            return response.data;
        });
        
        return {data: json};
    }
</script>
<script>
import Direct from '../Pages/Direct/Direct.svelte';

export let data;
</script>

<Direct data={data}/>