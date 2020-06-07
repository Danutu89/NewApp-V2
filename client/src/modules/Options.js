export let host = 'https://new-app.dev';
export let sockets = 'http://192.168.1.183:5000';

if(process.env.NODE_ENV == "prod"){
    host = 'https://new-app.dev';
    sockets = 'https://new-app.dev';
}