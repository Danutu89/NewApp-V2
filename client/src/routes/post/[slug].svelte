<script context="module">
    import { instance } from '../../modules/Requests.js';
    import { isSSR } from '../../modules/Preloads.js';
    import {get, api as Api, currentApi} from '../../modules/Store';
    export async function preload(page){
        let temp = (page.params.slug).toString().split("-");
        let id = temp[temp.length-1];
        let isSSRPage;
        var res = instance.get(get(Api)['post.index']+id);
        isSSR.subscribe(value => {
            isSSRPage = value;
        })();

        if(!isSSRPage) {
            return {data: res};
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
import Post from '../../Pages/Post/Post.svelte';
import { stores } from '@sapper/app';
const { page, session } = stores();

let temp = ($page.params.slug).toString().split("-");
let id = temp[temp.length-1];

currentApi.set({data: instance.get(get(Api)['post.index']+id)});

export let data;

</script>


<Post data={data}/>



