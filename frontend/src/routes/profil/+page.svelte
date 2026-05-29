<script lang="ts">
    // onMount wird aufgerufen, sobald die Komponente im Browser geladen ist
    import { onMount } from "svelte";
    // fetchProtected: authentifizierter GET-Request (hängt JWT aus localStorage als Authorization-Header an)
    // logout: entfernt den JWT aus dem localStorage
    import { fetchProtected, logout } from "$lib/api";

    // Profil-Daten des eingeloggten Benutzers – null solange die Antwort vom Backend noch aussteht
    // $state() macht die Variable reaktiv: ändert sich profile, aktualisiert Svelte das DOM automatisch
    let profile = $state<{ id: number; username: string; email: string } | null>(null);

    // onMount: wird einmalig nach dem Laden der Seite ausgeführt
    // GET /my-profile → gibt Benutzername, E-Mail und ID des eingeloggten Nutzers zurück
    onMount(async () => {
        profile = await fetchProtected("/my-profile");
    });

    // Wird aufgerufen, wenn der Nutzer auf "Logout" klickt
    function handleLogout() {
        logout();                    // JWT aus localStorage entfernen → Nutzer ist damit ausgeloggt
        window.location.href = "/";  // Vollständige Seiten-Navigation zur Startseite,
                                     // damit +layout.svelte neu ausgeführt wird und der Login-Zustand korrekt aktualisiert wird
    }
</script>

<main class="container">
    <div class="profile-card">
        <div class="avatar">👤</div>
        <h1>Mein Profil</h1>

        {#if profile}
            <div class="info-group">
                <div class="info-row">
                    <span class="info-label">Benutzername</span>
                    <span class="info-value">{profile.username}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">E-Mail</span>
                    <span class="info-value">{profile.email}</span>
                </div>
            </div>

            <div class="actions">
                <a href="/meine-rezepte" class="btn-secondary">Meine Rezepte</a>
                <button class="btn-logout" onclick={handleLogout}>Logout</button>
            </div>
        {:else}
            <p class="loading">Profil wird geladen...</p>
        {/if}
    </div>
</main>

<style>

    .container {
        min-height: 100vh;
        background: #f8f5f0;
        display: flex;
        align-items: flex-start;
        justify-content: center;
        padding: 4rem 1rem;
        font-family: 'Segoe UI', sans-serif;
    }

    .profile-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 2.5rem 2rem;
        width: 100%;
        max-width: 420px;
        text-align: center;
    }

    .avatar {
        font-size: 4rem;
        background: #f3e7d7;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
    }

    h1 {
        color: #845b2f;
        margin: 0 0 1.5rem 0;
        font-size: 1.5rem;
    }

    .info-group {
        background: #f8f5f0;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin-bottom: 1.5rem;
        text-align: left;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e0d6c3;
    }

    .info-row:last-child {
        border-bottom: none;
    }

    .info-label {
        color: #a97c50;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .info-value {
        color: #4b4035;
        font-size: 0.9rem;
    }

    .actions {
        display: flex;
        gap: 0.75rem;
        justify-content: center;
    }

    .btn-secondary {
        background: #f3e7d7;
        color: #845b2f;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.2rem;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.95rem;
        cursor: pointer;
        transition: background 0.2s;
    }

    .btn-secondary:hover {
        background: #e0d6c3;
    }

    .btn-logout {
        background: #ffe6e6;
        color: #b00020;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.2rem;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: background 0.2s;
    }

    .btn-logout:hover {
        background: #ffcccc;
    }

    .loading {
        color: #a97c50;
    }
</style>