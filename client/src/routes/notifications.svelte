<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR } from '../modules/Preloads.js';
    import {get, api as Api, user as User, currentApi} from '../modules/Store';
    export async function preload(page){
        if (get(User).auth == false){
            this.redirect(302, '/');
        }
        currentApi.set({data: instance.get(get(Api)['notifications.index']+'?ex=true'), json: null});
        isSSR.subscribe(value => {
            isSSRPage = value;
        })();

        if(!isSSRPage) {
            return;
        }

        const json = await get(currentApi).data.then(function (response) {
            return response.data;
        });

        currentApi.set({data: get(currentApi).data, json: json});

        return;
    }
</script>
<script>
import Notifications from '../components/Notifications.svelte';

export let notifications;

</script>

<Notifications not={notifications}/>

<svelte:head>
<title>Notifications - NewApp</title>
<meta name="robots" content="noindex">
</svelte:head>