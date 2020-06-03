<script context="module">
    import { instance } from '../../modules/Requests.js';
    import {get, api as Api, user as User} from '../../modules/Store';
    export async function preload(page,session){
        if (get(User).auth===false){
            this.redirect(302, '/');
        }
        const res = await instance.get(get(Api)['users.setting']).then(function (response) {
                return response.data;
            });
        const json = await res;
        return { user: json.settings };
    }
</script>

<script>
    import Settings from '../../Pages/User/Settings.svelte';

    export let user;
</script>

<svelte:head>
<title>Settings - NewApp</title>
<meta name="robots" content="noindex">
</svelte:head>

<Settings user={user} />