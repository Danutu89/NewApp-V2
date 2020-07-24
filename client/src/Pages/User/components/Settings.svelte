<script>
	import Select from 'svelte-select'
	import { instance } from '../../../modules/Requests.js'
	import {
		user as User,
		api as Api,
		deviceType as DeviceType,
	} from '../../../modules/Store'
	import { getSettings, settings_modified } from '../modules'
	import DatePicker from '../../../components/DatePicker'
	import { onMount } from 'svelte'
	let decoded = false

	let c_avatarimg, c_coverimg
	let editInfo, editMisc
	let social_choices = [],
		currentSocialToAdd
	let settings,
		settings_base = {
			social: [],
			pers: {},
			info: {},
		}

	function SwitchPanel(panel) {
		if (panel === 'misc') {
			if ($DeviceType == 'mobile') {
				editInfo.style['display'] = 'none'
				editMisc.style['display'] = 'block'
			} else {
				editInfo.style['display'] = 'none'
				editMisc.style['display'] = 'flex'
			}
		} else if (panel === 'main') {
			if ($DeviceType == 'mobile') {
				editInfo.style['display'] = 'block'
				editMisc.style['display'] = 'none'
			} else {
				editInfo.style['display'] = 'flex'
				editMisc.style['display'] = 'none'
			}
		}
	}

	onMount(async function () {
		settings = await getSettings()
		settings_base['social'] = settings.settings.social
		settings.utilities.socials.map((value, key) => {
			social_choices.push({
				value: key,
				label:
					'<span class=na-' +
					value.icon +
					' style=""> <span style=font-family:SANS-SERIF;margin-left:0.2rem;> ' +
					value.name +
					'</span></span>',
			})
		})
		social_choices = social_choices
		settings_modified.set(settings_base)
	})

	function showEdit(input) {
		var _input = document.getElementById(input)
		var _text = document.getElementById(input + '_text')
		if (_input.style.display == 'none') {
			_input.style.display = 'inherit'
			_text.style.display = 'none'
		} else {
			_input.style.display = 'none'
			_text.style.display = 'block'
		}
	}

	function onDateChange(key, category, d) {
		settings['settings']['date'][key].value = String(d.detail)
		settings_base['settings'][category][key] = String(d.detail)
	}

	function UpdateSttings(key, category, value) {
		if (category == 'social') settings_base[category][key] = value
		else {
			settings_base[category][key] = value
		}
		settings_modified.set(settings_base)
	}

	function ShowAddSocial() {
		if (document.querySelector('#addsocial').style.display == 'none')
			document.querySelector('#addsocial').style.display = 'flex'
		else document.querySelector('#addsocial').style.display = 'none'
	}

	function AddSocial() {
		var social = {
			link: '',
			id: 'new',
			social: settings['utilities']['socials'][currentSocialToAdd],
		}
		settings['settings']['social'] = [...settings['settings']['social'], social]
	}
</script>

<style>
	input[type='file'] {
		font-size: 100px;
		position: absolute;
		left: 0;
		top: 0;
		opacity: 0;
	}

	[type='file'] + label {
		border: var(--border);
		border-radius: var(--border-radius);
		background-color: var(--secondary-background);
		text-align: center;
		padding: 0.2rem;
		color: var(--color);
		position: relative;
		transition: all 0.3s;
		vertical-align: middle;
		cursor: pointer;
		padding: 0.5rem;
		line-height: 1;
		margin-inline-start: auto;
	}

	[type='file'] + label.btn-1 {
		background-color: var(--secondary-background);
		transition: none;
	}
	[type='file'] + label:hover {
		background-color: var(--hover);
	}
</style>

<div class="sidebar-main">
	<div class="edit-info" id="main" bind:this={editInfo} style="width: auto;">
		{#if settings}
			<div class="col-1" style="text-align:left;">
				<div class="section" style="margin-bottom: 0.5rem;">
					<div class="title">Information</div>

				</div>

				{#each Object.entries(settings['settings']['string']) as [key, value]}
					<div style="display: flex;margin-bottom:1rem;">
						<input
							id={value.key}
							name={value.key}
							on:change|preventDefault={() => {
								UpdateSttings(key, value.category, value.value)
							}}
							placeholder={value.key}
							type="text"
							style="display: none;margin-bottom:0;margin-right:0.5rem;"
							bind:value={value.value} />
						<p style="font-weight: 500;margin: 0.1em 0;" id="{value.key}_text">
							{value.name}: {value.value}
						</p>
						<span
							class="modify-button na-pencil-alt"
							on:click={() => showEdit(key)} />
					</div>
				{/each}

				{#each Object.entries(settings['settings']['date']) as [key, value]}
					<div style="display: flex;margin-bottom:1rem;">
						<DatePicker
							id={value.key}
							style="display: none;margin-bottom:0;margin-right:0.5rem;width:
							100%"
							selected={new Date(value.value)}
							on:datechange={(d) => {
								onDateChange(key, value.category, d)
							}} />
						<p style="font-weight: 500;margin: 0.1em 0;" id="{value.key}_text">
							{value.name}: {String(value.value).slice(0, 15)}
						</p>
						<span
							class="modify-button na-pencil-alt"
							on:click={() => showEdit(key)} />
					</div>
				{/each}
				<div class="section" style="margin-bottom: 0.5rem;">
					<div class="title">Social</div>
					<span class="modify-button na-plus" on:click={ShowAddSocial} />
				</div>
				<div
					id="addsocial"
					class="addsocial"
					style="display: none;margin-bottom: 0.5rem;">
					<Select
						containerStyles={'width: 100%;margin-right: 0.4rem;'}
						items={social_choices}
						style="width: 100%;margin-right: 0.5rem;"
						on:select={(value) => {
							currentSocialToAdd = value.detail.value
						}} />
					<span
						class="modify-button na-plus"
						style="width: 2.5rem;text-align: center;padding: 0.5rem 0;"
						on:click={AddSocial} />
				</div>
				{#each settings['settings']['social'] as setting, key}
					<div style="display: flex;margin-bottom:1rem;">
						<div
							class="input-group"
							style="display: none;margin-bottom:0;margin-right:0.5rem;"
							id={setting.id}>
							<div class="input-group-icon" style="margin-bottom:0;">
								https://{setting.social.pre_link}
							</div>
							<div class="input-group-area" style="display: flex;">
								<input
									id={setting.id}
									name={setting.social.name}
									on:change|preventDefault={() => {
										UpdateSttings(key, 'social', setting)
									}}
									placeholder={setting.name}
									type="text"
									style="margin-bottom:0;"
									bind:value={setting.link} />
							</div>
						</div>
						<p style="font-weight: 500;margin: 0.1em 0;" id="{setting.id}_text">
							{setting.social.name}: {setting.link}
						</p>
						<span
							class="modify-button na-pencil-alt"
							on:click={() => showEdit(setting.id)} />
					</div>
				{/each}
			</div>
			<div class="col-2" style="text-align:left;">
				<div class="section" style="margin-bottom: 0.5rem;">
					<div class="title">Images</div>

				</div>
				<div style="display: flex;margin-bottom:1rem;">
					<span style="font-weight: 500;">Avatar:</span>

					<input
						type="file"
						on:change|preventDefault={() => {
							UpdateSttings('avatar_img', 'info', true)
						}}
						name="avatarimg"
						id="avatarimg" />
					<label for="avatarimg" class="btn-1">
						<i class="na-inbox-out" style="margin-right:0.5rem;" />
						Upload
					</label>
				</div>

				<div style="display: flex;margin-bottom:1rem;">
					<span style="font-weight: 500;">Cover:</span>

					<input
						type="file"
						on:change|preventDefault={() => {
							UpdateSttings('cover_img', 'info', true)
						}}
						name="coverimg"
						id="coverimg" />
					<label for="coverimg" class="btn-1">
						<i class="na-inbox-out" style="margin-right:0.5rem;" />
						Upload
					</label>
				</div>

			</div>
		{/if}
	</div>
</div>
