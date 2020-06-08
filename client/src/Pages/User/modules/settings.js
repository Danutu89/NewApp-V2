import {instance} from '../../../modules/Requests.js';
import {user as User, api as Api, get} from '../../../modules/Store';


async function getSettings(){
    return await instance.get(get(Api)['users.settings']+get(User).name).then(res =>{
        return res.data;
    })
}

function getJsonDiff(data1, data2){
    var diff = (isArray(data1) ? [] : {});
    recursiveDiff(data1, data2, diff);
    return diff;
}

function recursiveDiff(a, b, node){
    var checked = [];

    for(var prop in a){
        if(typeof b[prop] == 'undefined'){
            addNode(prop, '[[removed]]', node);
        }
        else if(JSON.stringify(a[prop]) != JSON.stringify(b[prop])){
            // if value
            if(typeof b[prop] != 'object' || b[prop] == null){
                addNode(prop, b[prop], node);
            }
            else {
                // if array
                if(isArray(b[prop])){
                   addNode(prop, [], node);
                   recursiveDiff(a[prop], b[prop], node[prop]);
                }
                // if object
                else {
                    addNode(prop, {}, node);
                    recursiveDiff(a[prop], b[prop], node[prop]);
                }
            }
        }
    }
}

function addNode(prop, value, parent){
        parent[prop] = value;
}

function isArray(obj){
    return (Object.prototype.toString.call(obj) === '[object Array]');
}


export default {
    getSettings,
    getJsonDiff
}


export {
    getSettings,
    getJsonDiff
}