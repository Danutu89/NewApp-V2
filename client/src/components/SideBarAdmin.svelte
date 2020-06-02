<script>
import { user as User } from '../modules/Store';
</script>

<div class="sidebar-admin">
        <div class="user-card">
                <a href="/user/danutu" style="display: flex;">
                        <div class="user-image" style="margin-bottom:0;">
                                <img class="profile_image" alt="" src="{$User.avatar}" height="50px" width="50px" title="profile image">
                        </div>
                        <div class="user-info" style="margin-top: -0.2rem;"><span>{$User.real_name}</span> <br> <span
                        class="user-tag">@{$User.name}</span>
                        </div>
                </a>
        </div>
        <div class="navigation">
                <div class="header">
                        <span>Navigation</span>
                </div>
                <a href="/admin/"><div class="item">
                        <span>Dashboard</span>
                </div></a>
                <a href="/admin/posts"><div class="item">
                        <span>Posts</span>
                </div></a>
                <a href="/admin/Users"><div class="item">
                        <span>Users</span>
                </div></a>
                <a href="/admin/users"><div class="item">
                        <span>Users</span>
                </div></a>
        </div>
</div>