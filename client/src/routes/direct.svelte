<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR } from '../modules/Preloads.js';
    import {get, api as Api, user as User, currentApi} from '../modules/Store';
    export async function preload(page){
        let isSSRPage;
        if(get(User).auth === false){
            this.redirect(302,'/');
        }
        let res = instance.get(get(Api)['direct.index']);
        isSSR.subscribe(value => {
            isSSRPage = value;
        })();

        if(!isSSRPage) {
            return {data: res};
        }

        const response = await res.then(function (response) {
            return response;
        }).catch(
            (err)=>{
                return err.response;
            }
        );

        if (response.status != 200){
            return this.error(response.status, response.statusText);
        }

        const json = await response.data;

        return {data: json};
    }
</script>
<script>
import Direct from '../Pages/Direct/Direct.svelte';

currentApi.set({data: instance.get(get(Api)['direct.index'])});

export let data;
</script>

<Direct data={data}/>