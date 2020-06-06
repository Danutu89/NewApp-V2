<script>
import {onMount} from 'svelte';
import {deviceType} from '../../modules/Store';

let isMobile = false;

function checkDevice(e){
    var width = window.innerWidth;
    var temp = $deviceType;
    if (width < 940)
        deviceType.set("mobile");
    else if (width < 1260)
        deviceType.set("tablet");
    else
        deviceType.set("desktop");

    if(temp != $deviceType)
        document.dispatchEvent(new CustomEvent("changedDeviceType"));
}

onMount(()=>{
    window.addEventListener("resize", checkDevice);
    var width = window.innerWidth;
    if (width < 940)
        deviceType.set("mobile");
    else if (width < 1260)
        deviceType.set("tablet");
    else
        deviceType.set("desktop");
    document.dispatchEvent(new CustomEvent("changedDeviceType"));
})

</script>