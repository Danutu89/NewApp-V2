import {instance} from '../Requests.js';

export default async(payload)=>{
    const res = await instance.post('/api/register' ,payload).then(function (response) {
        return response.data;
    }).then(function (response){
        return response;
    }).catch(function (error) {
        if (error.response) {
        return error.response;
        }
    });
    const json = await res;
    return json;
}