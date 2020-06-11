<script context="module">
    import { instance } from '../modules/Requests.js';
    import { isSSR, lPage } from '../modules/Preloads.js';
    import {get, api as Api, currentApi} from '../modules/Store';
    export async function preload(page,session){
        let isSSRPage;
        const res = instance.get(get(Api)['home.index']+'?search=' + page.query.q);
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
import Home from '../Pages/Home/Home.svelte'
import { stores } from '@sapper/app';
const { page, session } = stores();

currentApi.set({data: instance.get(get(Api)['home.index']+'?search=' + $page.query.q)});

export let data;
</script>
<svelte:head>
<title>Search - {$page.query.q}</title>
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


<Home data={data} mode={'search'}/>