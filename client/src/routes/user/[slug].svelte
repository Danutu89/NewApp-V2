<script context="module">
    import { instance } from '../../modules/Requests.js';
    import { isSSR } from '../../modules/Preloads.js';
    import {get, api as Api, currentApi} from '../../modules/Store';
    export async function preload(page,session){
        let isSSRPage;
        currentApi.set({data: instance.get(get(Api)['users.user']+page.params.slug), json: null});
        isSSR.subscribe(value => {
            isSSRPage = value;
        })();

        if(!isSSRPage) {
            return;
        }

        const json = await get(currentApi).then(function (response) {
            return response.data;
        });

        currentApi.set({data: get(currentApi).data, json: json});

        return;
    }
</script>

<script>
import User from '../../Pages/User/User.svelte';
export let data;

</script>

<User data={data}/>

