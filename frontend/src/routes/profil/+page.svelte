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

<main>
    <h1>Mein Profil</h1>

    <!-- Profil-Daten werden erst angezeigt, wenn die Antwort vom Backend angekommen ist -->
    <!-- Solange zeigt {:else} den Ladehinweis an -->
    {#if profile}
        <p><strong>Benutzername:</strong> {profile.username}</p>
        <p><strong>Email:</strong> {profile.email}</p>
        <!-- onclick ruft handleLogout direkt als Referenz auf (kein () nötig, da keine Argumente übergeben werden) -->
        <button class="logout-btn" onclick={handleLogout}>Logout</button>
    {:else}
        <p>Lade Profil...</p>
    {/if}
</main>

<style>
    main {
        max-width: 400px;
        margin: 2rem auto;
        font-family: sans-serif;
        color: rgb(132, 91, 47);
    }
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