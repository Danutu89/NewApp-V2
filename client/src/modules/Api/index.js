import axios from 'axios';
import {api} from '../Store';

async function setApiUrls(){
    var apiUrls = await axios.get("/api/v2").then((res)=>{return res.data;});
    api.set(apiUrls);
    return;
}

export{
    setApiUrls
}