import {instance} from '../../../modules/Requests.js';
import {user as User, api as Api, get} from '../../../modules/Store';
import currentPage from './currentPage.js';
import Cookie from 'cookie-universal';
const cookies = Cookie();
var jwt_decode = require('jwt-decode');
import {writable} from 'svelte/store';

const settings_modified = writable({});

async function getSettings(){
    return await instance.get(get(Api)['users.settings']+get(User).name).then(res =>{
        return res.data;
    })
}

async function setSettings(){
    var s_coverimg = document.getElementById('coverimg');
    var s_avatarimg = document.getElementById('avatarimg');
    var c_avatarimg, c_coverimg;
    let formdata = new FormData();

    try {
        formdata.append('avatarimg', s_avatarimg.files[0], s_avatarimg.files[0].name);
        c_avatarimg = true;
    } catch (error) {
        c_avatarimg = false;
    }

    try {
        formdata.append('coverimg', s_coverimg.files[0], s_coverimg.files[0].name);
        c_coverimg = true;
    } catch (error) {
        c_coverimg = false;
    }

    formdata.append('data', JSON.stringify(get(settings_modified)));

    const resp = await instance.post(get(Api)['users.settings']+get(User).name, formdata, {headers: {'Content-Type': 'multipart/form-data'}}).then((response)=>{
        return response;
    })

    if (resp.status != 200){
        //alert
        return;
    }

    var decoded;

    try {
        decoded = jwt_decode(resp.data['token']);
    } catch (error) {
        decoded = false;
    }

    if (decoded != false){
        cookies.set("token", resp.data['token'],{maxAge:60 * 60 * 24 * 30, path: '/'});
        User.set({
            name: decoded.name,
            id: decoded.id,
            email: decoded.email,
            avatar: decoded.avatar,
            real_name: decoded.realname,
            permissions: decoded.permissions,
            theme: decoded.theme,
            theme_mode: decoded.theme_mode,
            auth: true
        })
    }else{
        //alert
        return;
    }

    currentPage.set("main");
}

export default {
    getSettings,
    setSettings,
    settings_modified
}


export {
    getSettings,
    setSettings,
    settings_modified
}