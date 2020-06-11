<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR } from '../modules/Preloads.js';
    import {get, api as Api, user as User, currentApi} from '../modules/Store';
    export async function preload(page){
        let isSSRPage;
        if (get(User).auth == false){
            this.redirect(302, '/');
        }
        const res = instance.get(get(Api)['notifications.index']+'?ex=true');
        isSSR.subscribe(value => {
            isSSRPage = value;
        })();

        if(!isSSRPage) {
            return { data: res };
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
import Notifications from '../components/Notifications.svelte';

currentApi.set({data: instance.get(get(Api)['notifications.index']+'?ex=true')});

export let data;

</script>

<Notifications not={data}/>

<svelte:head>
<title>Notifications - NewApp</title>
<meta name="robots" content="noindex">
</svelte:head>