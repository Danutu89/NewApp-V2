<script context="module">
    import { instance } from '../../modules/Requests.js';
    import { isSSR } from '../../modules/Preloads.js';
    import {get, api as Api, currentApi} from '../../modules/Store';
    export async function preload(page){
        let temp = (page.params.slug).toString().split("-");
        let id = temp[temp.length-1];
        let isSSRPage;
        currentApi.set({data: instance.get(get(Api)['post.index']+id), json: null});
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
import Post from '../../Pages/Post/Post.svelte';

</script>


<Post/>



