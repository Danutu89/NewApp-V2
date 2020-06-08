export let host = 'https://new-app.dev';
export let sockets = 'https://new-app.dev';

if(process.env.NODE_ENV == "prod"){
    host = 'https://new-app.dev';
    sockets = 'https://new-app.dev';
}