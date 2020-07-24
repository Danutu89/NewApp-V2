import { writable } from 'svelte/store'
export const alert = writable({
	active: false,
	img: null,
	title: null,
	text: null,
	link: null,
})

export function activateAlert({img, title, text, link, type, success}) {
	alert.set({
		active: true,
		img,
		type,
		title,
		text,
		link,
		success
	})
}
