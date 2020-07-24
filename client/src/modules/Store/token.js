import { writable } from 'svelte/store'

const token = writable(null)

const setToken = (value) => {
	token.set(value)
}

export { token, setToken }

export default {
	token,
	setToken,
}
