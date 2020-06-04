import { writable } from 'svelte/store';
const deviceType = writable("desktop");

export default deviceType;