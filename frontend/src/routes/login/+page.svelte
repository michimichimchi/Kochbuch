<script lang="ts">
    // login() sendet POST /token (OAuth2-Formular) und speichert den JWT im localStorage
    // register() sendet POST /auth/register und legt den Benutzer in der Datenbank an
    import {login, register } from '$lib/api';

    // Svelte 5 Runes: $state() macht eine Variable reaktiv –
    // Svelte aktualisiert das DOM automatisch, wenn sich der Wert ändert.

    // Registrierungsfelder, werden an die drei Eingabefelder im Registrierungsformular gebunden
    let regUsername = $state("");
    let regEmail = $state("");
    let regPassword = $state("");

    // Loginfelder, werden an die zwei Eingabefelder im Loginformular gebunden
    let loginUsername = $state("");
    let loginPassword = $state("");

    // Fehlermeldung – wird unter den Formularen angezeigt, wenn ein Fehler auftritt
    let errorMsg = $state("");

    // Wird aufgerufen, wenn der Nutzer auf "Registrieren" klickt
    async function handleRegister() {
        errorMsg = "";  // Vorherige Fehlermeldung zurücksetzen
        try {
            await register(regUsername, regEmail, regPassword);  // POST /auth/register → Benutzer wird in der DB angelegt
            await handleLogin(regUsername, regPassword); // Direkt nach der Registrierung einloggen – Benutzername und Passwort werden explizit übergeben,
                                                         // damit nicht die leeren loginUsername/loginPassword-Felder verwendet werden
            window.location.href = "/"; // Vollständige Seiten-Navigation zur Startseite – dadurch wird +layout.svelte neu ausgeführt
                                        // und der Login-Zustand (Profil-Button) korrekt aktualisiert
        } catch (error) {
            // Fehlermeldung aus dem geworfenen Error-Objekt auslesen und anzeigen
            // (z.B. "Username bereits vergeben" vom Backend)
            errorMsg = (error as Error).message;
        }
    }

    // Wird aufgerufen, wenn der Nutzer auf "Anmelden" klickt – oder intern nach der Registrierung
    // Standardparameter: Falls keine Argumente übergeben werden (normaler Login-Klick),
    // werden die Werte aus den Loginfeldern verwendet.
    // Falls Argumente übergeben werden (Aufruf aus handleRegister), werden diese stattdessen genutzt.
    async function handleLogin(username: string = loginUsername, password: string = loginPassword) {
        errorMsg = "";  // Vorherige Fehlermeldung zurücksetzen
        try {
            await login(username, password);  // POST /token → JWT wird vom Backend zurückgegeben und im localStorage gespeichert
            window.location.href = "/";       // Vollständige Seiten-Navigation zur Startseite (siehe Kommentar in handleRegister)
        } catch (error) {
            // Fehlermeldung aus dem geworfenen Error-Objekt auslesen und anzeigen
            // (z.B. "Ungültige Anmeldedaten" vom Backend)
            errorMsg = (error as Error).message;
        }
    }
</script>



<main>
    <!-- Registrierungsformular -->
    <h2>Registrieren</h2>
    <!-- bind:value verknüpft den Eingabewert bidirektional mit der $state-Variable:
         Tippt der Nutzer, aktualisiert sich die Variable – ändert sich die Variable, aktualisiert sich das Feld. -->
    <input bind:value={regUsername} placeholder="Benutzername" />
    <input bind:value={regEmail} placeholder="Email" />
    <input bind:value={regPassword} type="password" placeholder="Passwort" />
    <!-- onclick ruft handleRegister direkt als Referenz auf (kein () nötig, da keine Argumente übergeben werden) -->
    <button onclick={handleRegister}>Registrieren</button>

    <!-- Loginformular -->
    <h2>Login</h2>
    <input bind:value={loginUsername} placeholder="Benutzername" />
    <input bind:value={loginPassword} type="password" placeholder="Passwort" />
    <!-- onclick verwendet eine Pfeilfunktion, damit handleLogin ohne Argumente aufgerufen wird
         und die Standardparameter (loginUsername, loginPassword) greifen.
         Würde man onclick={handleLogin} schreiben, würde Svelte das Browser-Event-Objekt
         als erstes Argument übergeben – das würde den username-Parameter überschreiben. -->
    <button onclick={() => handleLogin()}>Anmelden</button>

    <!-- Fehlermeldung: wird nur angezeigt, wenn errorMsg einen Wert hat -->
    {#if errorMsg}
        <p style="color: red">{errorMsg}</p>
    {/if}

</main>

<style>

    main {
        max-width: 400px;
        margin: 2rem auto;
        font-family: sans-serif;
    }
    input {
        display: block;
        margin: 0.5rem 0;
        padding: 0.4rem 0.6rem;
        width: 100%;
    }
    button {
        margin: 0.5rem 0.25rem 0.5rem 0;
        padding: 0.4rem 1rem;
        cursor: pointer;
    }

</style>

