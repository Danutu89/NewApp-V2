<script>
	import { user as User } from '../../modules/Store'
</script>

<div class="sidebar" id="sidebar-left">
	{#if $User.auth}
		<div class="user-card">
			<div style="display: flex;">
				<div class="user-image" style="margin-bottom:0;">
					<div
						class="loading"
						style="border-radius: 50px;width: 50px; height: 50px;" />
				</div>
				<div class="user-info" style="margin-top: -0.2rem;">
					<div
						class="loading"
						style="height: 0.8rem; width: 80%;margin-bottom: 0.5rem;" />
					<div class="loading" style="height: 0.8rem; width: 50%;" />
				</div>
			</div>
		</div>
	{/if}
	<div class="widget" id="navigation">
		<div class="widget-header">
			<div class="widget-title">Navigation</div>
		</div>
		<div class="widget-list">
			<div class="widget-item" id="posts-show">
				<div class="text">
					<a href="/">
						<span class="section">
							<i class="na-pen-square" />
							Posts
						</span>
					</a>
				</div>
			</div>
			<div class="widget-item" id="podcasts-show">
				<div class="text">
					<a href="/podcasts">
						<span class="section">
							<i class="na-headphones" />
							Podcasts
						</span>
					</a>
				</div>
			</div>
		</div>
	</div>
	<div class="widget">
		<div class="widget-header">
			<div class="widget-title">Customize your experience</div>
		</div>
		<div class="widget-list" style="max-height: 400px;overflow: auto;">
			{#each Array(5) as x}
				<div
					class="widget-item"
					id="widget-tags"
					style="border-top: none;display: flex;">
					<div class="text" style="width: 100%;">
						<div class="loading" style=" height: 0.8rem; width: 50%;" />
					</div>
				</div>
			{/each}
		</div>
	</div>
	<div class="widget" style="display: block;padding: 1rem;">
		<a href="https://newapp.nl">
			<img
				style="vertical-align: middle;margin-left: -1px;"
				onerror="this.style.display='none'"
				data="/static/logo.svg"
				width="25"
				height="30"
				alt="" />
		</a>
		<a href="https://www.facebook.com/newapp.nl">
			<i
				class="na-facebook-square"
				style="font-size: 2rem; color: var(--theme-color); vertical-align:
				middle; margin-left: 0.5rem;" />
		</a>
		<a href="https://twitter.com/_NewApp_">
			<i
				class="na-twitter"
				style="font-size: 2rem; color: var(--theme-color); vertical-align:
				middle; margin-left: 0.5rem;" />
		</a>
		<a href="/about" style="display: block;margin-top: 0.5rem;">About</a>
		<a href="/contact" style="display: block;margin-top: 0.5rem;">Contact</a>
		<a href="/privacy" style="display: block;margin-top: 0.5rem;">Privacy</a>
	</div>

</div>
