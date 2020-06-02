<script>
import Posts from '../../../components/Posts.svelte';

export let user;
</script>

<div class="sidebar-main">
    <div class="statistics">
        <div class="stat-item">
            <i class="na-pen-square" style="font-size: 1rem;"></i> {user.post_count} Posts
        </div>
        <div class="stat-item">
            <i class="na-tachometer" style="font-size: 1rem;"></i> {user.post_views} Posts Views
        </div>
        <div class="stat-item">
            <i class="na-comments" style="font-size: 1rem;"></i> {user.reply_count} Replies
        </div>
    </div>
    <div class="user-posts">
        <Posts data={user.posts} user={user.id} mode={"user"}/>
    </div>
</div>