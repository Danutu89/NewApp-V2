<script context="module">
    import {instance} from '../../modules/Requests.js';
    import {user as User, get, api as Api} from '../../modules/Store';
    export async function preload(page){
        if (get(User).auth == false){
            this.redirect(302, '/');
        }
        const res = await instance.get('/api/admin/dashboard').then(function (response) {
                return response.data;
            });
        const response = await res;
        return { json: response };
    }
</script>

<script>
import Dashboard from '../../components/admin/Dashboard.svelte';
export let json;
</script>

<svelte:head>
<title>NewApp - Admin</title>
<meta name="robots" content="noindex">
</svelte:head>

<Dashboard json={json}/>