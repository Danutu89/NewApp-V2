<script context="module">
    import {user, get} from '../modules/Store'; 
    export async function preload(page){
        if (get(user).auth == false){
            this.redirect(302, '/');
        }
    }
</script>

<script>
    import New from '../Pages/Post/New.svelte';
</script>

<New/>

<svelte:head>
<title>New Post - NewApp</title>
<meta name="robots" content="noindex">
</svelte:head>