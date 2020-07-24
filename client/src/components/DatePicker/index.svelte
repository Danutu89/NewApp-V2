<script>
	import { createEventDispatcher } from 'svelte'
	import Calendar from './calendar.svelte'
	import { getMonthName } from './datetime.js'

	const dispatch = createEventDispatcher()

	// props
	export let isAllowed = () => true
	export let selected = new Date()
	export let id
	export let style

	// state
	let date, month, year, showDatePicker

	// so that these change with props
	$: {
		date = selected.getDate()
		month = selected.getMonth()
		year = selected.getFullYear()
	}

	// handlers
	const onFocus = () => {
		showDatePicker = true
	}

	const next = () => {
		if (month === 11) {
			month = 0
			year = year + 1
			return
		}
		month = month + 1
	}

	const prev = () => {
		if (month === 0) {
			month = 11
			year -= 1
			return
		}
		month -= 1
	}

	const onDateChange = (d) => {
		showDatePicker = false
		dispatch('datechange', d.detail)
	}
</script>

<style>
	.relative {
		position: relative;
	}
	.box {
		position: absolute;
		top: 40px;
		left: 0px;
		border: var(--border);
		background-color: var(--secondary-background);
		display: inline-block;
		border-radius: var(--border-radius);
		box-sizing: 5px 5px 11px 0px rgba(0, 0, 0, 0.2);
	}

	.month-name {
		display: flex;
		justify-content: space-around;
		align-items: center;
		margin: 6px 0;
	}

	.center {
		display: flex;
		justify-content: center;
		align-items: center;
		text-align: center;
	}

	button {
		width: 70%;
		border: 1px solid rgba(0, 0, 0, 0.125);
		background-color: var(--secondary-color);
		border-radius: var(--border-radius);
		color: white;
		font-weight: 600;
		padding: 0.2rem 1rem;
		cursor: pointer;
		transition: cubic-bezier(0, 0, 1, 1) 100ms;
	}
	button:focus {
		outline: none;
	}
</style>

<div class="relative" {id} {style}>
	<input
		type="text"
		style="width: 100%;margin-bottom: 0px"
		on:focus={onFocus}
		value={selected.toDateString()} />
	{#if showDatePicker}
		<div class="box">
			<div class="month-name">
				<div class="center">
					<button on:click={prev}>
						<i class="na-chevron-left" />
					</button>
				</div>
				<div class="center">{getMonthName(month)} {year}</div>
				<div class="center">
					<button on:click={next}>
						<i class="na-chevron-right" />
					</button>
				</div>
			</div>
			<Calendar
				{month}
				{year}
				date={selected}
				{isAllowed}
				on:datechange={onDateChange} />
		</div>
	{/if}
</div>
