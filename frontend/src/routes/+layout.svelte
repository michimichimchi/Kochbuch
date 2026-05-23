<script lang="ts">
    import { onMount } from "svelte";
    import { logout, isLoggedIn, fetchProtected } from '$lib/api';
    import { page } from '$app/stores';

    // Svelte 5 Runes: $state() macht eine Variable reaktiv – Svelte aktualisiert das DOM automatisch, wenn sich der Wert ändert.
    let loggedIn = $state(false);
    let sidebarOpen = $state(false);
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
        // logout() entfernt den JWT aus dem localStorage, damit der Nutzer ausgeloggt wird
        // es werden die Variablen neu gesetzt, damit der Profil-Button und die Sidebar sofort verschwinden, 
        // ohne dass die Seite neu geladen werden muss
        logout();
        loggedIn = false;
        profile = null;
        sidebarOpen = false;
        window.location.href = "/"; // Vollständige Seiten-Navigation zur Startseite, damit der Login-Zustand korrekt aktualisiert wird (siehe Kommentare in handleLogin und handleRegister)
    }
</script>

{#if loggedIn}
    <!-- Profilbild-Button oben rechts -->
    <!-- onclick toggelt die sidebarOpen-Variable, damit die Sidebar angezeigt oder versteckt wird, wenn der Button geklickt wird -->
    <button class="profile-btn" onclick={() => sidebarOpen = !sidebarOpen}>
        Profil
    </button>

    <!-- Sidebar -->
    {#if sidebarOpen}
        <aside class="sidebar">
            <h3>Mein Profil</h3>
            <p><strong>Benutzername:</strong> {profile?.username}</p>
            <p><strong>Email:</strong> {profile?.email}</p>
            <button class="logout-btn" onclick={handleLogout}>Logout</button>
        </aside>
    {/if}
{:else}
    <a href={$page.url.pathname === '/login' ? '/' : '/login'} class="anmelden-btn">
        {$page.url.pathname === '/login' ? 'Zurück' : 'Anmelden'}
    </a>
{/if}

<!-- Hier wird die eigentliche Seite eingebettet -->
<slot />

<style>
    /* Aussehen des Profil-Buttons oben rechts */
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
        z-index: 100;       /* Damit der Button über der Sidebar liegt */
    }


    /* Aussehen der Sidebar */
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
        color: rgb(132, 91, 47);
    }

    /* Aussehen des Logout-Buttons in der Sidebar */
    .logout-btn {
        margin-top: 1rem;
        padding: 0.4rem 1rem;
        background-color: #e53935;
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
    }

    /* Aussehen des Anmelden-Buttons, wenn nicht eingeloggt */
    .anmelden-btn {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background-color: transparent;
        color: rgb(132, 91, 47);
        border: 2px solid rgb(132, 91, 47);
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-size: 1rem;
        text-decoration: none;
    }
</style>
