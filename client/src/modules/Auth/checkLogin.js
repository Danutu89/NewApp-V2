import jwtdecode from 'jwt-decode';
import { user } from '../Store';

export default (req, res)=>{
    let userDecoded = {};

    const cookies = require('cookie-universal')(req, res);
    
    try{
        userDecoded = jwtdecode(cookies.get('token'));
    }
    catch{
        user.reset();
        cookies.remove('token');
        return;
    }

    if(userDecoded.exp < (new Date().getTime() + 1) / 1000){
        user.reset();
        cookies.remove('token');
        
    }
    
};

