import { currentApi, get } from './Store'
import { instance } from './Requests'

export default async function ReloadApi() {
	const query = instance.get(get(currentApi).data)

    const response = await query
    document.dispatchEvent(new CustomEvent('reloaded'))
	if (response.status == 200) {
		const responseJson = await response
		return responseJson.data
	} else {
		throw new Error('Something went wrong')
	}
}
