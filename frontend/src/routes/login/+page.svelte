<script lang="ts">
    // login: sendet POST /token (OAuth2-Formular) und speichert den JWT im localStorage
    // register: sendet POST /auth/register und legt den Benutzer in der Datenbank an
    import { login, register } from '$lib/api';

    // Svelte 5 Runes: $state() macht eine Variable reaktiv –
    // Svelte aktualisiert das DOM automatisch, wenn sich der Wert ändert

    // Registrierungsfelder – gebunden an die drei Eingabefelder im Registrierungsformular
    let regUsername = $state("");
    let regEmail = $state("");
    let regPassword = $state("");

    // Loginfelder – gebunden an die zwei Eingabefelder im Loginformular
    let loginUsername = $state("");
    let loginPassword = $state("");

    // Fehlermeldung – wird angezeigt, wenn Registrierung oder Login fehlschlägt
    let errorMsg = $state("");

    // Wird aufgerufen, wenn der Nutzer auf "Registrieren" klickt
    async function handleRegister() {
        errorMsg = "";  // Vorherige Fehlermeldung zurücksetzen
        try {
            await register(regUsername, regEmail, regPassword);  // POST /auth/register → Benutzer wird in der DB angelegt
            await handleLogin(regUsername, regPassword);          // Direkt nach Registrierung einloggen –
                                                                  // regUsername/regPassword werden explizit übergeben,
                                                                  // damit nicht die leeren loginUsername/loginPassword-Felder verwendet werden
            window.location.href = "/";  // Vollständige Seiten-Navigation zur Startseite,
                                         // damit +layout.svelte neu ausgeführt wird und der Login-Zustand korrekt aktualisiert wird
        } catch (error) {
            // Fehlermeldung aus dem Error-Objekt auslesen (z.B. "Username bereits vergeben" vom Backend)
            errorMsg = (error as Error).message;
        }
    }

    // Wird aufgerufen, wenn der Nutzer auf "Anmelden" klickt – oder intern nach der Registrierung
    // Standardparameter: ohne Argumente → loginUsername/loginPassword aus den Feldern
    //                    mit Argumenten (Aufruf aus handleRegister) → übergebene Werte
    async function handleLogin(username: string = loginUsername, password: string = loginPassword) {
        errorMsg = "";  // Vorherige Fehlermeldung zurücksetzen
        try {
            await login(username, password);  // POST /token → JWT wird zurückgegeben und im localStorage gespeichert
            window.location.href = "/";       // Vollständige Seiten-Navigation zur Startseite (siehe Kommentar in handleRegister)
        } catch (error) {
            // Fehlermeldung aus dem Error-Objekt auslesen (z.B. "Benutzername oder Passwort falsch" vom Backend)
            errorMsg = (error as Error).message;
        }
    }
</script>

<section class="auth-section">
    <h2>Registrieren</h2>
    <!-- bind:value verknüpft den Eingabewert bidirektional mit der $state-Variable -->
    <input bind:value={regUsername} placeholder="Benutzername" />
    <input bind:value={regEmail} placeholder="Email" />
    <input bind:value={regPassword} type="password" placeholder="Passwort" />
    <!-- onclick als direkte Referenz: kein () nötig, da keine Argumente übergeben werden -->
    <button onclick={handleRegister}>Registrieren</button>

    <h2>Login</h2>
    <input bind:value={loginUsername} placeholder="Benutzername" />
    <input bind:value={loginPassword} type="password" placeholder="Passwort" />
    <!-- Pfeilfunktion nötig: onclick={handleLogin} würde das Browser-Event-Objekt
         als erstes Argument übergeben und damit den username-Parameter überschreiben -->
    <button onclick={() => handleLogin()}>Anmelden</button>

    <!-- Fehlermeldung wird nur angezeigt, wenn errorMsg einen Wert hat -->
    {#if errorMsg}
        <p style="color: red">{errorMsg}</p>
    {/if}
</section>

<style>

    .auth-section {
        max-width: 400px;
        width: 90%;
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        padding: 2rem 2.5rem;
        margin: 4rem auto;
    }
    .auth-section input {
        display: block;
        margin: 0.5rem 0;
        padding: 0.4rem 0.6rem;
        width: 100%;
        border-radius: 6px;
        border: 1px solid #e0d6c3;
    }
    .auth-section button {
        margin: 0.5rem 0.25rem 0.5rem 0;
        padding: 0.4rem 1rem;
        cursor: pointer;
        background: #845b2f;
        color: #fff;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: background 0.2s;
    }
    .auth-section button:hover {
        background: #a97c50;
    }

</style>