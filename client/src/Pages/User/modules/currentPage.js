import {writable} from 'svelte/store';

const currentPage = writable("main");


export default currentPage;