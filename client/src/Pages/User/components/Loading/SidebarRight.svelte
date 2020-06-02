<div class="sidebar-right">
    <div class="widgets">
        <div class="user-follows">
        <div class="header"><div class="loading" style="width: 40%"></div> Follows</div>
        <hr>
        <div class="users">
            {#each Array(3) as x}
            <div class="user-followed" id="user-1">
                <div class="user-img"><div class="loading" style="width:40px, height: 40px; border-radius: 40px;"></div></div>
                <div class="user-info">
                <span><div class="loading" style="width: 50%"></div></span>
                <br>
                <span style="font-size: 0.7rem;"><div class="loading" style="width: 30%"></div></span>
                </div>
            </div>
            {/each}
        </div>
        </div>
    </div>
</div>