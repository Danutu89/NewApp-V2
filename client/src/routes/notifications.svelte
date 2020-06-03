<script context="module">
    import { instance } from '../modules/Requests.js';
    import { host } from '../modules/Options.js';
    import {get, api as Api, user as User} from '../modules/Store';
    export async function preload(page){
        if (get(User).auth == false){
            this.redirect(302, '/');
        }
        const res = await instance.get(get(Api)['notifications.index']+'?ex=true').then(function (response) {
                return response.data;
            });
        const json = await res;
        return { notifications: json };
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