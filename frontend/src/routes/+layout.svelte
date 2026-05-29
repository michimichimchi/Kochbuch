<script lang="ts">
    import { onMount } from "svelte";
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
            } catch (error){
                const status = (error as any).status;
                if (status === 401 || status === 404) {   // Token ungültig oder Profil nicht gefunden, daher Logout
                    logout();
                loggedIn = false;
                }
            }
        }
    });
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
            <li><a href="/profil" class="nav-link">Mein Profil</a></li>
        {:else}
            <li><a href="/login" class="nav-link">Anmelden</a></li>
        {/if}
    </ul>
</nav>

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

</style>
