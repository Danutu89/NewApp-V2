<script context="module">
    import { instance } from '../../../modules/Requests.js';
    import {get, api as Api, currentApi, user as User} from '../../../modules/Store';
    export async function preload(page, session){
        let args = '';
        if (get(User).auth===false){
            this.redirect(302, '/');
        }
        let temp = (page.params.slug).toString().split("-");
        let id = temp[temp.length-1];
        const res = await instance.get(get(Api)['post.edit']+id).then(function (response) {
                return response.data;
            });
        const json = await res;

        currentApi.set({data: null, josn: json})
        return;
    }   
</script>

<script>
import Edit from '../../../Pages/Post/Edit.svelte';
</script>

<Edit/>

<svelte:head>
<title>Edit Profile - NewApp</title>
<meta name="robots" content="noindex">
</svelte:head>