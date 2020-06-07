<script>
import {onMount, beforeUpdate} from 'svelte'
import Nav from '../components/Nav.svelte';
import { loadProgressBar } from 'axios-progress-bar';
import { stores } from '@sapper/app';
const { page } = stores();
import Analytics from '../modules/Analytics.js';
import SideBarAdmin from '../components/SideBarAdmin.svelte';
import Alert from '../components/Alert.svelte';
export let segment;
import {host, sockets} from '../modules/Options.js';
import {instance} from '../modules/Requests.js';
import { alert } from '../modules/Alert.js';
import { lPage } from '../modules/Preloads.js';
import { swipeDirection } from '../modules/Swipe.js';
import Swipe from '../components/Controllers/Swipe.svelte';
import Screen from '../components/Controllers/Screen.svelte';
import {socket} from '../modules/SocketIO.js';
import {user as User, api as Api} from '../modules/Store';
import {confirmUser} from '../modules/Auth';
import {setApiUrls} from '../modules/Api';
import Cookie from 'cookie-universal';
const cookies = Cookie();

let admin = false;
let analytics = new Analytics;

let tStart;
let tCurrent;

let reload;
let reloadHeight;
let changeY;

let loading = false;

var path = segment;
try {
	if(path.includes('/admin/')){
		admin = true;
	}else{
		admin = false;
	}
} catch (error) {
	admin = false;
}

$: if(cookies.get('token')){
	instance.defaults.headers.common['Token'] = cookies.get('token');
}

function lazyLoad(){
	var img = document.querySelectorAll("img");
	img.forEach(image => {
		var data = image.getAttribute("data");
		if(String(data).includes("newapp.nl"))
			var data_m = String(data).replace("https://newapp.nl", host);
		else
			data_m = data;
		image.setAttribute('src', data_m);
	});
}

async function CheckNotification(id){
    if($User.auth == false){
        return;
    }
    const not = await instance.get($Api['notifications.check'] + id).then(response =>{
        if(response.status != 200){
            //alert
            return;
        }

        if(response.data['operation'] != "success"){
            //alert
            return;
        }

        return;
    })
}


async function resetLoader(e){
	reload.style.transition = 'min-height 300ms linear, transform 300ms linear';
	reload.style["min-height"] = '';
	reload.style.transform = '';
	loading = false;
	await setTimeout(()=>{
		reload.style.transition = '';
		reload.children[0].style.display = 'none';
		reload.children[0].style.transform = '';
		reload.children[0].style["-webkit-animation"] = "";
		reload.children[0].style["animation"] = "";
		changeY = 0;
	},400)
	
}

function updatePage(){
	var path = location.pathname;
	if(path.includes('admin')){
		admin = true;
	}else{
		admin = false;
	}
	if($User.auth)
		document.querySelector("html").setAttribute("theme", $User.theme);
	else{
		if(window.matchMedia('(prefers-color-scheme: dark)').matches){
			document.querySelector("html").setAttribute("theme", "Dark");
		}else{
			document.querySelector("html").setAttribute("theme", "Light");
		}
	}
	if($page.query.notification_id){
        CheckNotification($page.query.notification_id);
	}
}

onMount(async function() {
	if($page.query.email && $page.query.token)
		confirmUser({email: $page.query.email, token:$page.query.token});
	setApiUrls();
	reloadHeight = getComputedStyle(reload).height;
	document.addEventListener('reloaded', resetLoader);
	loadProgressBar('', instance);
	if($User.auth){
		socket.on('connect', function () {
			socket.emit('access', {
				data: $User.token
			});												
		});
		socket.on('disconnect', function () {
			socket.emit('logout', {
				data: $User.token
			});												
		});
		
		document.querySelector("html").setAttribute("theme", $User.theme);			
		if (window.Notification && Notification.permission !== "granted") {
			Notification.requestPermission(function (status) {
			if (Notification.permission !== status) {
				Notification.permission = status;
			}
			if (Notification.permission === 'granted'){
				if ('serviceWorker' in navigator) {
					navigator.serviceWorker.controller.postMessage($User.token);
				}
			}
			});
		}
		else if (Notification.permission === 'granted'){
			if ('serviceWorker' in navigator) {
				navigator.serviceWorker.controller.postMessage($User.token);
			}
		}
	}else{
		if(window.matchMedia('(prefers-color-scheme: dark)').matches){
			document.querySelector("html").setAttribute("theme", "Dark");
		}else{
			document.querySelector("html").setAttribute("theme", "Light");
		}
	}
	lazyLoad();
	document.addEventListener('DOMSubtreeModified', lazyLoad);
	//analytics.init(true);
	let pageChangedEvent = new CustomEvent("urlPathUpdated");
	let url = location.href;
	document.body.addEventListener('click', ()=>{
	 	requestAnimationFrame(()=>{
			if(url!==location.href){
				document.dispatchEvent(pageChangedEvent);
		// 		analytics.validate();
		// 		analytics.init(false);
			};
			url = location.href;
	 	});
	}, true);
	document.addEventListener("urlPathUpdated", updatePage);
});

</script>

<Nav admin={admin}/>

{#if admin == false}
<reload bind:this={reload} style="display:flex"><div class="loader"></div></reload>
{:else}
<reload bind:this={reload} style="height: 2.7rem;display:flex"><div class="loader"></div></reload>
{/if}

<overflow></overflow>

{#if admin == false}

<content>
	<slot></slot>
</content>

{:else}

<a-content>
	<SideBarAdmin/>
	<slot></slot>
</a-content>
{/if}

{#if $alert.active == true}
<Alert/>
{/if}

<Swipe/>
<Screen/>