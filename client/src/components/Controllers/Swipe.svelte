<script>
	import { onMount, beforeUpdate } from 'svelte'

	let swipeDir = 'none'
	let elementSwiped = 'none'
	let touchStart, touchCurrent, touchEnd
	let touchStartFixed
	let touchLive = []
	let touchPosStart
	let swipeThreshold = 20
	let touchThreshold = 10
	let touchDistance = 10
	let change, changeFixed
	let elementOpened = 'none'

	let overflow

	//wrapper req
	let sidebar,
		navbar,
		sidebarOpened = false
	let wrapperDragAmount

	//reaload req
	let reload, reloadHeight

	function getTranslate3d(el) {
		var values = el.split(/\w+\(|\);?/)
		if (!values[1] || !values[1].length) {
			return []
		}
		return values[1].split(/,\s?/g)
	}

	function swipeStart(e) {
		updateElements()
		if (typeof e.targetTouches[0] == 'undefined') {
			touchStart = { x: e.clientX, y: e.clientY }
			touchPosStart = { x: e.clientX, y: e.clientY }
		} else {
			touchStart = {
				x: e.targetTouches[0].clientX,
				y: e.targetTouches[0].clientY,
			}
			touchPosStart = {
				x: e.targetTouches[0].clientX,
				y: e.targetTouches[0].clientY,
			}
		}
		touchStartFixed = touchStart

		if (sidebar != null) {
			sidebar.style.transition = 'none'
		}
		if (reload != null) {
			reload.style.transition = 'none'
		}

		wrapperDragAmount = elementOpened == 'wrapper' ? -20 : -290

		touchLive.push(touchStart)
	}

	function swipeMove(e) {
		if (typeof e.targetTouches[0] == 'undefined')
			touchCurrent = { x: e.clientX, y: e.clientY }
		else
			touchCurrent = {
				x: e.targetTouches[0].clientX,
				y: e.targetTouches[0].clientY,
			}

		change = {
			x: (touchStart.x - touchCurrent.x) * -1,
			y: (touchStart.y - touchCurrent.y) * -1,
		}
		changeFixed = {
			x: (touchStartFixed.x - touchCurrent.x) * -1,
			y: (touchStartFixed.y - touchCurrent.y) * -1,
		}

		if (touchLive.length < 8) {
			touchLive.unshift({
				x: touchCurrent.x,
				y: touchCurrent.y,
				swipeDir: swipeDir,
			})
			return
		} else if (touchLive.length > 25) touchLive.pop()

		touchLive.unshift({
			x: touchCurrent.x,
			y: touchCurrent.y,
			swipeDir: swipeDir,
		})

		var touchIndex = touchLive.length - touchDistance

		if (
			Math.abs(touchCurrent.x - touchStartFixed.x) > 20 &&
			Math.abs(touchCurrent.y - touchLive[touchLive.length - 5].y) <
				swipeThreshold
		) {
			if (touchCurrent.x - touchStartFixed.x < 0) {
				swipeDir = 'left'
			} else {
				swipeDir = 'right'
			}
		} else if (
			Math.abs(touchCurrent.y - touchStartFixed.y) > 20 &&
			Math.abs(touchCurrent.x - touchLive[touchLive.length - 2].x) <
				swipeThreshold
		) {
			if (touchCurrent.y - touchStartFixed.y < 0) {
				swipeDir = 'up'
			} else {
				swipeDir = 'down'
			}
		} else {
			swipeDir = 'none'
		}

		if (
			touchLive[touchLive.length - 1].swipeDir != swipeDir ||
			touchLive[touchLive.length - 1].swipeDir == 'none'
		) {
			touchLive = []
			touchStart = touchCurrent
		} else {
			touchLive.push({
				x: touchCurrent.x,
				y: touchCurrent.y,
				swipeDir: swipeDir,
			})
		}

		if (
			(swipeDir == 'right' && touchPosStart.x < window.innerWidth / 4) ||
			(swipeDir == 'left' && elementOpened == 'wrapper')
		) {
			if (
				sidebar != null &&
				(elementSwiped == 'wrapper' || elementSwiped == 'none') &&
				(elementOpened == 'wrapper' || elementOpened == 'none')
			) {
				elementSwiped = 'wrapper'
				elementOpened = 'wrapper'
				dragWrapper(e)
			}
		} else if (swipeDir == 'left') {
		} else if (
			touchPosStart.y < window.innerHeight / 5 &&
			document.body.scrollTop == 0 &&
			window.scrollY == 0 &&
			(swipeDir == 'down' || swipeDir == 'up')
		) {
			if (
				reload != null &&
				(elementOpened == 'none' || elementOpened == 'reload') &&
				(elementSwiped == 'none' || elementSwiped == 'reload')
			) {
				document.body.style.overflow = 'hidden'
				elementSwiped = 'reload'
				dragReload(e)
			}
		} else {
			elementSwiped = 'none'
		}
	}

	async function swipeEnd(e) {
		if (typeof e.targetTouches[0] == 'undefined')
			touchEnd = {
				x: e.changedTouches[0].clientX,
				y: e.changedTouches[0].clientY,
			}
		else
			touchEnd = {
				x: e.targetTouches[0].clientX,
				y: e.targetTouches[0].clientY,
			}

		var isTouch =
			Math.abs(touchEnd.y - touchStart.y) < touchThreshold &&
			Math.abs(touchEnd.x - touchStart.x) < touchThreshold
				? true
				: false

		if (isTouch) swipeDir = 'touch'

		if (
			(sidebar != null && !isTouch && elementSwiped == 'wrapper') ||
			elementOpened == 'wrapper'
		) {
			sidebar.style.transition = ''
			var tranX = sidebar.style.transform
			tranX = getTranslate3d(tranX)
			tranX = parseFloat(tranX[0])
			if (tranX != 20 && tranX != 290) {
				if (Math.abs(Math.abs(tranX) - 20) > Math.abs(Math.abs(tranX) - 290)) {
					sidebar.style.transform = 'translate3d(-290px, 0px, 0px)'
					elementOpened = 'none'
					overflow.classList.remove('show')
					document.body.style.overflow = 'visible'
				} else {
					sidebar.style.transform = 'translate3d(-20px, 0px, 0px)'
					elementOpened = 'wrapper'
					overflow.classList.add('show')
					document.body.style.overflow = 'hidden'
				}
			}
		}

		if (elementOpened != 'wrapper') document.body.style.overflow = 'visible'

		if (
			(reload != null && !isTouch && elementSwiped == 'reload') ||
			elementOpened == 'reload'
		) {
			reload.style.transition = ''

			if (changeFixed.y > 100) {
				reload.style['min-height'] = 'calc(' + reloadHeight + 'px + 60px)'
				reload.style.transform = 'translate3d(0px, 60px, 0px)'
				reload.children[0].style['-webkit-animation'] =
					'load8 1.1s infinite linear'
				reload.children[0].style['animation'] = 'load8 1.1s infinite linear'
				elementOpened = 'reload'
				await setTimeout(() => {
					document.dispatchEvent(new CustomEvent('reloading'))
				}, 400)
			} else {
				reload.style['min-height'] = ''
				reload.style.transform = ''
				reload.children[0].style.display = 'none'
				reload.children[0].style.transform = ''
				reload.children[0].style['-webkit-animation'] = ''
				reload.children[0].style['animation'] = ''
				elementOpened = 'none'
			}
		}

		touchLive = []
		swipeDir = 'none'
		elementSwiped = 'none'
		change = {}
	}

	function dragWrapper(e) {
		var multiplier = 1.4
		var dragAmount

		dragAmount = wrapperDragAmount + change.x * multiplier

		if (dragAmount > -290 && dragAmount < -20) {
			sidebar.style.transform = 'translate3d(' + dragAmount + 'px, 0px, 0px)'
		}
	}

	function dragReload(e) {
		var reloadHeightD = parseFloat(
			getComputedStyle(reload).minHeight.replace(/[^\d.]/g, '')
		)
		var rotation =
			changeFixed.y + 10 < 360 ? ((changeFixed.y + 10) * 30) / 10 : 30
		var height = reloadHeight + changeFixed.y + 30
		var spinnerHeight,
			containerHeight = 0
		var posY = changeFixed.y

		if (swipeDir == 'down') {
			containerHeight = reloadHeight + posY + 30
			spinnerHeight = changeFixed.y
		} else {
			posY -= Math.abs(change.y)
			containerHeight = reloadHeight + posY
			spinnerHeight = changeFixed.y
		}

		if (document.body.scrollTop == 0 && window.scrollY == 0) {
			document.body.style.overflow = 'hidden'

			reload.children[0].style.display = 'block'
			elementOpened = 'reload'

			if (changeFixed.y < 70) {
				reload.style.transform =
					'translate3d(0px, ' + spinnerHeight + 'px, 0px)'
			}
			if (changeFixed.y < 360) {
				reload.children[0].style.transform = 'rotate(' + rotation + 'deg)'
			}
			if (changeFixed.y < 100) {
				reload.style.transition = 'none'
				posY = changeFixed.y
			} else if (changeFixed.y > 100) {
				reload.style.transition = ''
				if (swipeDir == 'down') posY = 100
				reload.style.transform = 'translate3d(0px, ' + 70 + 'px, 0px)'
			} else if (changeFixed.y < 0) {
				reload.style.transition = ''
				if (swipeDir == 'up') posY = 0
				reload.style.transform = 'translate3d(0px, ' + 0 + 'px, 0px)'
			}
			reload.style['min-height'] = reloadHeight + posY + 'px'
		}
	}

	async function resetLoader() {
		await setTimeout(() => {
			reload.style['min-height'] = ''
			reload.style.transform = ''
			reload.children[0].style.display = 'none'
			reload.children[0].style.transform = ''
			reload.children[0].style['-webkit-animation'] = ''
			reload.children[0].style['animation'] = ''
			elementOpened = 'none'
		}, 400)
	}

	function updateElements() {
		overflow = document.querySelector('overflow')

		//wrapper req
		sidebar = document.getElementById('sidebar-left')
		navbar = document.querySelector('.newapp-navbar')

		//reload req
		reload = document.querySelector('reload')
	}

	async function launchLoader(){
		reload.children[0].style.display = 'block'
		reload.style['min-height'] = 'calc(' + reloadHeight + 'px + 40px)'
		//reload.style.transform = 'translate3d(0px, 60px, 0px)'
		reload.children[0].style['-webkit-animation'] =
			'load8 1.1s infinite linear'
		reload.children[0].style['animation'] = 'load8 1.1s infinite linear'
		await setTimeout(() => {document.dispatchEvent(new CustomEvent('reloading'))}, 400)
	}

	onMount(() => {
		document.addEventListener('touchstart', swipeStart)
		document.addEventListener('touchmove', swipeMove)
		document.addEventListener('touchend', swipeEnd)
		document.addEventListener('urlPathUpdated', updateElements)
		document.addEventListener('changedDeviceType', updateElements)

		document.addEventListener('reloaded', resetLoader)
		document.addEventListener('reloadingAnim', launchLoader)
		

		overflow = document.querySelector('overflow')

		//wrapper req
		sidebar = document.getElementById('sidebar-left')
		navbar = document.querySelector('.newapp-navbar')

		//reload req
		reload = document.querySelector('reload')
		reloadHeight = parseFloat(
			getComputedStyle(reload).minHeight.replace(/[^\d.]/g, '')
		)
	})
</script>
