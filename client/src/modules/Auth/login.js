import jwtdecode from 'jwt-decode';
import {instance} from '../Requests.js';
import {user} from '../Store';
import Cookie from 'cookie-universal';
const cookies = Cookie();

export default async(username,pass)=>{
    const res = await instance.get('/api/login',{
        auth: {
        username: String(username).toLowerCase(),
        password: pass
        }
    }).then(function (response){
        return response;
    }).catch(function (error) {
        if (error.response) {
        return error.response;
        }
    });
    const json = await res;

    if (json.status != 200)
        return json;

    var userDecoded = jwtdecode(json.data.login);
    
    if(typeof(window) != "undefined")
        user.set({
            auth: true,
            name: userDecoded.name,
            real_name: userDecoded.realname,
            email: userDecoded.email,
            avatar: userDecoded.avatar,
            id: userDecoded.id,
            permissions: userDecoded.permissions,
            theme: userDecoded.theme,
            theme_mode: userDecoded.theme_mode
        });

    cookies.set('token', json.data.login, {maxAge:60 * 60 * 24 * 30, path: '/'});
    instance.defaults.headers.common['Token'] = json.data.login;
    
    return json;
};