<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from '$app/navigation';
    import { logout, isLoggedIn, fetchProtected } from '$lib/api';

    let loggedIn = $state(false);
    let sidebarOpen = $state(false); // Für Profil-Sidebar rechts
    let navOpen = $state(false);     // Für Haupt-Navigation links (mobil)
    let profile = $state<{ id: number; username: string; email: string } | null>(null);

    onMount(async () => {
        loggedIn = isLoggedIn();
        if (loggedIn) {
            try {
                profile = await fetchProtected("/my-profile");
            } catch {
                loggedIn = false;
            }
        }
    });

    function handleLogout() {
        logout();
        loggedIn = false;
        profile = null;
        sidebarOpen = false;
        window.location.reload();
    }
</script>


<!-- Haupt-Navigation Sidebar (links) -->
<nav class="main-nav">
    <div class="nav-title">🍲 Kochbuch</div>
    <ul>
        <li><a href="/" class="nav-link">Startseite</a></li>
        <li><a href="/rezepte" class="nav-link">Alle Rezepte</a></li>
        {#if loggedIn}
            <li><a href="/meine-rezepte" class="nav-link">Meine Rezepte</a></li>
            <li><a href="/rezept-neu" class="nav-link">Neues Rezept ✚</a></li>
            <li><a href="/meal-prep" class="nav-link">Meal Prep</a></li>
        {/if}
    </ul>
</nav>

<!-- Profil-Button oben rechts -->
{#if loggedIn}
    <button class="profile-btn" onclick={() => sidebarOpen = !sidebarOpen}>
        Profil
    </button>

    <!-- Profil-Sidebar (rechts) -->
    {#if sidebarOpen}
        <aside class="sidebar">
            <h3>Mein Profil</h3>
            <p><strong>Benutzername:</strong> {profile?.username}</p>
            <p><strong>Email:</strong> {profile?.email}</p>
            <button class="logout-btn" onclick={handleLogout}>Logout</button>
        </aside>
    {/if}
{/if}


<!-- Hauptinhalt, mit Abstand zur Sidebar -->
<div class="main-content">
    <slot />
</div>

<style>
    /* Haupt-Navigation Sidebar (links) */
    .main-nav {
        position: fixed;
        top: 0;
        left: 0;
        width: 220px;
        height: 100vh;
        background: #fff;
        box-shadow: 2px 0 8px rgba(0,0,0,0.07);
        padding: 2.5rem 1.2rem 1.2rem 1.2rem;
        z-index: 90;
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }
    .nav-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #845b2f;
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
        text-align: left;
    }
    .main-nav ul {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 1.1rem;
    }
    .nav-link {
        color: #845b2f;
        text-decoration: none;
        font-size: 1.08rem;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: background 0.18s, color 0.18s;
        display: block;
    }
    .nav-link:hover {
        background: #f3e7d7;
        color: #a97c50;
    }

    /* Hauptinhalt mit Abstand zur Sidebar */
    .main-content {
        margin-left: 220px;
        min-height: 100vh;
        background: #f8f5f0;
    }

    /* Profil-Button oben rechts */
    .profile-btn {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background-color: transparent;
        color: rgb(132, 91, 47);
        border: 2px solid rgb(132, 91, 47);
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-size: 1rem;
        cursor: pointer;
        z-index: 100;
    }

    /* Profil-Sidebar (rechts) */
    .sidebar {
        position: fixed;
        top: 0;
        right: 0;
        width: 260px;
        height: 100%;
        background: white;
        box-shadow: -2px 0 8px rgba(0,0,0,0.15);
        padding: 2rem 1.5rem;
        z-index: 99;
    }

    /* Logout-Button in der Sidebar */
    .logout-btn {
        margin-top: 1rem;
        padding: 0.4rem 1rem;
        background-color: #e53935;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
    }
</style>
