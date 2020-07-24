<script>
	import { getDateRows, uuid, noop } from './datetime.js'
	import { createEventDispatcher } from 'svelte'

	const dispatch = createEventDispatcher()

	// props
	export let date
	export let month
	export let year
	export let isAllowed

	// local vars to help in render
	const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
	let cells

	// function helpers
	const onChange = (date) => {
		dispatch('datechange', new Date(year, month, date))
	}

	const allow = (year, month, date) => {
		if (!date) return true
		return isAllowed(new Date(year, month, date))
	}

	$: cells = getDateRows(month, year).map((c) => ({
		value: c,
		allowed: allow(year, month, c),
	}))
</script>

<style>
	.container {
		margin-top: 8px;
		padding: 6px;
		width: 310px;
	}
	.row {
		display: flex;
		margin: 2px 6px;
		flex-wrap: wrap;
	}

	.cell {
		display: inline-block;
		width: 32px;
		height: 20px;
		text-align: center;
		padding: 4px;
		margin: 1px;
	}

	.selected {
		background: var(--secondary-color);
	}

	.highlight {
		transition: transform 0.2s cubic-bezier(0.105, 0.14, 0.24, 1);
	}

	.disabled {
		background: #efefef;
		cursor: not-allowed;
		color: #bfbfbf;
	}

	.highlight:hover {
		background: var(--theme-color);
		color: #fff;
		cursor: pointer;
		transform: scale(1.3);
	}

	.selected.highlight:hover {
		background: var(--secondary-color);
	}
</style>

<div class="container">
	<div class="row">
		{#each weekdays as day}
			<div class="cell">{day}</div>
		{/each}
	</div>

	<div class="row">
		{#each cells as { allowed, value } (uuid())}
			<div
				on:click={allowed && value ? onChange.bind(this, value) : noop}
				class:cell={true}
				class:highlight={allowed && value}
				class:disabled={!allowed}
				class:selected={new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime() === new Date(year, month, value).getTime()}>
				{value || ''}
			</div>
		{/each}
	</div>
</div>
