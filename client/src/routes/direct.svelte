<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR, lPage } from '../modules/Preloads.js';
    import {get, api as Api, user as User} from '../modules/Store';
    lPage.set({data: get(Api)['direct.index'], refresh: false});
    export async function preload(page){
        let isSSRPage;
        if(get(User).auth === false){
            this.redirect(302,'/');
        }

        const res = instance.get(get(Api)['direct.index']);
        lPage.set({data: get(Api)['direct.index'], refresh: false});
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