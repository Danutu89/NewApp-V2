<script>
	export let user
</script>

<div class="sidebar-right">
	{#if user.follow_check}
		<div class="widgets">
			<div class="user-follows">
				<div class="header">{user.real_name} Follows</div>
				<hr />
				<div class="users">
					{#each user.follows as userf}
						<div class="user-followed" id="user-1">
							<div class="user-img">
								<img
									loading="lazy"
									data={userf.avatar}
									onerror="this.style.display='none'"
									alt="" />
							</div>
							<a href="/user/{userf.name}">
								<div class="user-info">
									<span>{userf.real_name}</span>
									<br />
									<span style="font-size: 0.7rem;">@{userf.name}</span>
								</div>
							</a>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>
