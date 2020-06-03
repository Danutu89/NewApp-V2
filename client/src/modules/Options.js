export let host = 'https://192.168.1.183';
export let sockets = 'http://192.168.1.183';

if(process.env.NODE_ENV == "prod"){
    host = 'https://new-app.dev';
    sockets = 'https://new-app.dev';
}