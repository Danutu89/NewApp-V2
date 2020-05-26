<script>
import { onMount, beforeUpdate } from 'svelte';
import { lPage } from '../../modules/Preloads.js';

let swipeDir = "none";
let elementSwiped = "none";
let touchStart, touchCurrent, touchEnd;
let touchStartFixed;
let touchLive = [];
let touchPosStart;
let swipeThreshold = 4;
let touchThreshold = 10;
let touchDistance = 5;
let change, changeFixed;
let elementOpened = "none";

let overflow;

//wrapper req
let sidebar, navbar, sidebarOpened = false;
let wrapperDragAmount;

//reaload req
let reload, reloadHeight;

function getTranslate3d (el) {
    var values = el.split(/\w+\(|\);?/);
    if (!values[1] || !values[1].length) {
        return [];
    }
    return values[1].split(/,\s?/g);
}


function swipeStart(e){
    if(typeof(e.targetTouches[0]) == "undefined"){
        touchStart = {x: e.clientX, y: e.clientY};
        touchPosStart = {x: e.clientX, y: e.clientY};
    }
    else{
        touchStart = {x: e.targetTouches[0].clientX, y: e.targetTouches[0].clientY};
        touchPosStart = {x: e.targetTouches[0].clientX, y: e.targetTouches[0].clientY};
    }
    touchStartFixed = touchStart;

    if(sidebar != null){
        sidebar.style.transition = "none";
    }
    if(reload != null){
        reload.style.transition = "none";
    }

    wrapperDragAmount = elementOpened == "wrapper" ? -20 : -290;

    touchLive.push(touchStart);
}

function swipeMove(e){
    if(typeof(e.targetTouches[0]) == "undefined")
        touchCurrent = {x: e.clientX, y: e.clientY};
    else
        touchCurrent = {x: e.targetTouches[0].clientX, y: e.targetTouches[0].clientY};

    change = {x: (touchStart.x - touchCurrent.x)*-1, y: (touchStart.y - touchCurrent.y)*-1};
    changeFixed = {x: (touchStartFixed.x - touchCurrent.x)*-1, y: (touchStartFixed.y - touchCurrent.y)*-1};

    if(touchLive.length < 5){
        //swipeDir = "none";
        touchLive.push({x: touchCurrent.x, y: touchCurrent.y, swipeDir: swipeDir});
        return;
    }

    var touchIndex = touchLive.length - touchDistance;

    if (Math.abs(touchCurrent.x - touchLive[touchIndex].x) > swipeThreshold && Math.abs(touchCurrent.y - touchLive[touchIndex].y) < swipeThreshold){
        if(touchCurrent.x - touchLive[touchIndex].x < 0){
            swipeDir = "left";
        }else{
            swipeDir = "right";
        }
    }else if(Math.abs(touchCurrent.y - touchLive[touchIndex].y) > swipeThreshold && Math.abs(touchCurrent.x - touchLive[touchIndex].x) < swipeThreshold){
        if(touchCurrent.y - touchLive[touchIndex].y < 0){
            swipeDir = "up";
        }else{
            swipeDir = "down";
        }
    }else{
        swipeDir = "none";
        
    }

    if(touchLive[touchLive.length - 1].swipeDir != swipeDir || touchLive[touchLive.length - 1].swipeDir == "none"){
        touchLive = [];
        touchStart = touchCurrent;
    }else{
        touchLive.push({x: touchCurrent.x, y: touchCurrent.y, swipeDir: swipeDir});
    }

    if(swipeDir == "right" && touchPosStart.x < window.innerWidth/4 || swipeDir == "left" && elementOpened == "wrapper"){
        if(sidebar != null && (elementSwiped == "wrapper" || elementSwiped == "none") && (elementOpened == "wrapper" || elementOpened == "none")){
            elementSwiped = "wrapper";
            elementOpened = "wrapper";
            dragWrapper(e);
        }
    }else if(swipeDir == "left"){
        
    }else if(touchPosStart.y < window.innerHeight/5 && document.body.scrollTop == 0 && window.scrollY == 0 && (swipeDir == "down" || swipeDir == "up")){
        if(reload != null && (elementOpened == "none" || elementOpened == "reload") && (elementSwiped == "none" || elementSwiped == "reload")){
            document.body.style.overflow = 'hidden';
            elementSwiped = "reload";
            dragReload(e);
        }
    }else{
        elementSwiped = "none";
    }
    
    //console.log(touchStart);
    //console.log(swipeDir, touchLive);
    
}

async function swipeEnd(e){
    if(typeof(e.targetTouches[0]) == "undefined")
        touchEnd = {x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY};
    else
        touchEnd = {x: e.targetTouches[0].clientX, y: e.targetTouches[0].clientY};

    var isTouch = Math.abs(touchEnd.y - touchStart.y) < touchThreshold && Math.abs(touchEnd.x - touchStart.x) < touchThreshold ? true : false;

    if(isTouch)
        swipeDir = "touch";

    if(sidebar != null && !isTouch && elementSwiped == "wrapper" || elementOpened == "wrapper"){
        sidebar.style.transition = "";
        var tranX = sidebar.style.transform;
        tranX = getTranslate3d(tranX);
        tranX = parseFloat(tranX[0]);
        if(tranX != 20 && tranX != 290){
            if( Math.abs(Math.abs(tranX) - 20) > Math.abs(Math.abs(tranX) - 290)){
                sidebar.style.transform = "translate3d(-290px, 0px, 0px)";
                elementOpened = "none";
                overflow.classList.remove("show");
            }else{
                sidebar.style.transform = "translate3d(-20px, 0px, 0px)";
                elementOpened = "wrapper";
                overflow.classList.add("show");
            }
        }
    }

    if(elementOpened != "wrapper")
        document.body.style.overflow = 'visible';

    if(reload != null && !isTouch){
        reload.style.transition = "";

        if(changeFixed.y > 100){
            reload.style["min-height"] = 'calc('+reloadHeight+'px + 60px)';
            reload.style.transform = 'translate3d(0px, 60px, 0px)';
            reload.children[0].style["-webkit-animation"] = "load8 1.1s infinite linear";
            reload.children[0].style["animation"] = "load8 1.1s infinite linear";
            elementOpened = "reload";
            await setTimeout(()=>{
                lPage.set({data: $lPage.data, refresh: true});
            }, 400)
        }else{
            reload.style["min-height"] = '';
            reload.style.transform = '';
            reload.children[0].style.display = 'none';
			reload.children[0].style.transform = '';
			reload.children[0].style["-webkit-animation"] = "";
			reload.children[0].style["animation"] = "";
            elementOpened = "none";
        }
    }

    //console.log(change)
    //console.log(swipeDir, elementSwiped);
    //console.log(isTouch);
    touchLive = [];
    swipeDir = "none";
    elementSwiped = "none";
    change = {};
}

function dragWrapper(e){
    var multiplier = 1.4;
    var dragAmount;

    dragAmount = wrapperDragAmount + (change.x*multiplier);

    if(dragAmount > -290 && dragAmount < -20){
        sidebar.style.transform = "translate3d("+dragAmount+"px, 0px, 0px)";
    }

}

function dragReload(e){
    var reloadHeightD = parseFloat((getComputedStyle(reload).minHeight).replace(/[^\d.]/g, ''));
    var rotation = changeFixed.y+10 < 360 ? (changeFixed.y+10) * 30/10 : 30;
    var height = reloadHeight + changeFixed.y + 30;
    var spinnerHeight, containerHeight = 0;
    var posY = changeFixed.y;

    if(swipeDir == "down"){
        containerHeight = reloadHeight + posY + 30;
        spinnerHeight = changeFixed.y;
    }else{
        posY -= Math.abs(change.y);
        containerHeight = reloadHeight + posY;
        spinnerHeight = changeFixed.y;
    }

	if(document.body.scrollTop == 0 && window.scrollY == 0){
		document.body.style.overflow = 'hidden';
	
        reload.children[0].style.display = 'block';
        elementOpened = "reload";

		if(changeFixed.y < 70 ){
            reload.style.transform = 'translate3d(0px, '+spinnerHeight+'px, 0px)';
		}  
		if(changeFixed.y < 360){
			reload.children[0].style.transform = 'rotate('+rotation+'deg)';
        }
        if(changeFixed.y < 100){
            reload.style.transition = "none";
            posY = changeFixed.y;
		}else if(changeFixed.y > 100){
            reload.style.transition = "";
            if(swipeDir == "down")
                posY = 100;
            reload.style.transform = 'translate3d(0px, '+70+'px, 0px)';
        }else if(changeFixed.y < 0 ){
            reload.style.transition = "";
            if(swipeDir == "up")
                posY = 0;
            reload.style.transform = 'translate3d(0px, '+0+'px, 0px)';
        }
        reload.style["min-height"] = (reloadHeight+posY)+'px';
    }
    console.log(posY, change.y);
}

async function resetLoader(){
	await setTimeout(()=>{
        reload.style["min-height"] = '';
	    reload.style.transform = '';
		reload.children[0].style.display = 'none';
		reload.children[0].style.transform = '';
		reload.children[0].style["-webkit-animation"] = "";
        reload.children[0].style["animation"] = "";
        elementOpened = "none";
	},400)
}

beforeUpdate(()=>{
    overflow = document.querySelector("overflow");

    //wrapper req
    sidebar = document.getElementById("sidebar-left");
    navbar = document.querySelector(".newapp-navbar");

    //reload req
    reload = document.querySelector("reload");

})

onMount(()=>{
    document.addEventListener("touchstart", swipeStart);
    document.addEventListener("touchmove", swipeMove);
    document.addEventListener("touchend", swipeEnd);

    document.addEventListener('reloaded', resetLoader);

    overflow = document.querySelector("overflow");

    //wrapper req
    sidebar = document.getElementById("sidebar-left");
    navbar = document.querySelector(".newapp-navbar");

    //reload req
    reload = document.querySelector("reload");
    reloadHeight = parseFloat((getComputedStyle(reload).minHeight).replace(/[^\d.]/g, ''));


});
</script>