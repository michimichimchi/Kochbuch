<script lang="ts">
	import {onMount} from "svelte";
	import { login, isLoggedIn, register } from '$lib/api';

	// Zustand, ob der Benutzer eingeloggt ist
	let loggedIn = $state(false);

	// Registrierungsfelder
	let regUsername = $state("");
	let regEmail = $state("");
	let regPassword = $state("");

	// Login-Felder
	let loginUsername = $state("");
	let loginPassword = $state("");

	// Gemeinsame Fehlermeldung für Registrierung und Login
	let errorMsg = $state("");

	// Steuert die Sichtbarkeit des Auth-Formulars
	let showAuth = $state(false);

	// Überprüft beim Laden der Seite, ob der Benutzer bereits eingeloggt ist
	onMount(() => {
		loggedIn = isLoggedIn();
	})

	// Registrierungs-Handler, der nach erfolgreicher Registrierung direkt handleLogin() aufruft, damit Benutzer nach Registrierung auch eingeloggt wirdloggt wird
	async function handleRegister() {
		errorMsg = "";
		try {
			await register(regUsername, regEmail, regPassword); //Funktion register() aus api.ts aufrufen, um den Benutzer zu registrieren
			await handleLogin();                                // handle Login() aufrufen, um den Benutzer direkt nach der Registrierung einzuloggen                                       
		} catch (error) {
			errorMsg = (error as Error).message;
		}
	}

	// Login-Handler, der den Benutzer einloggt und bei Erfolg die Seite neu lädt, um den Zustand zurückzusetzen
	async function handleLogin() {
		try {
			await login(loginUsername, loginPassword); // Funktion login() aus api.ts aufrufen, um den Benutzer einzuloggen
			loggedIn = true;
			showAuth = false;         // Auth-Formular ausblenden
			window.location.reload(); // Seite neu laden, um den Zustand zurückzusetzen
		} catch (error) {
			errorMsg = (error as Error).message;
		}
	}

</script>

{#if !loggedIn}
    <button class="auth-btn" onclick={() => showAuth = !showAuth}>Anmelden</button>
{/if}

<main>
	<h1>Mein Projekt</h1>
	<p>Willkommen! Hier entsteht eure Anwendung.</p>

	<!-- Hier wird Auth-Formular Einblendung für Registrieren und Anmelden geregelt, Bedingung: Nutzer muss auf den Anmelde-Button klicken und darf nicht angemeldet sein -->
	{#if showAuth && !loggedIn}
		<!-- Registrierung -->
		<h2>Registrieren</h2>
		<input bind:value={regUsername} placeholder="Benutzername" />
		<input bind:value={regEmail} placeholder="Email" />
		<input bind:value={regPassword} type="password" placeholder="Passwort" />
		<button onclick={handleRegister}>Registrieren</button>      <!-- wenn man auf Registrieren-Butten klickt, werden Werte ans Backend gesendet	-->

		<!-- Login -->
		<h2>Login</h2>
		<input bind:value={loginUsername} placeholder="Benutzername" />
		<input bind:value={loginPassword} type="password" placeholder="Passwort" />
		<button onclick={handleLogin}>Anmelden</button> 		<!-- wenn man auf Anmelden-Butten klickt, werden Werte ans Backend gesendet	-->

		<!-- Fehlermeldung -->
		{#if errorMsg}
			<p style="color: red">{errorMsg}</p>
		{/if}
	{/if}

</main>

<style>
	main {
		max-width: 600px;
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

	/* Aussehen des Anmelde-Buttons oben rechts */
	.auth-btn {
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
	}
</style>
