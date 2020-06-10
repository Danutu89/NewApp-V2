<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR } from '../modules/Preloads.js';
    import {get, api as Api, currentApi} from '../modules/Store';
    export async function preload(page,session){
        let isSSRPage;
        currentApi.set({data:instance.get(get(Api)['home.index']+'?mode=discuss'), json: null});
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
import Home from '../Pages/Home/Home.svelte'

</script>

<svelte:head>
<title>Discuss - NewApp</title>
<meta name="description" content="NewApp the newest community for developers to learn, share​ ​their programming ​knowledge, and build their careers.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://newapp.nl/">
<meta property="og:site_name" content="NewApp">
<meta property="og:image" itemprop="image primaryImageOfPage" content="https://newapp.nl/static/logo.jpg">
<meta property="og:description" content="The newest community for developers to learn, share​ ​their programming ​knowledge, and build their careers.">
<meta name="twitter:title" content="NewApp">
<meta name="twitter:description" content="The newest community for developers to learn, share​ ​their programming ​knowledge, and build their careers.">
<meta name="twitter:image:src" content="https://newapp.nl/static/logo.jpg">
</svelte:head>

<Home mode={'discuss'}/>