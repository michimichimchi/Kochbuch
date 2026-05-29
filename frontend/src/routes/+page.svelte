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

    // Gemeinsame Fehlermeldung
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
	<!-- Hero Section -->
	<section class="hero">
		<div class="hero-content">
			<h1>Kochbuch</h1>
			<p>Entdecke, teile und genieße die besten Rezepte!</p>
			<div class="search-bar">
				<input type="text" placeholder="Suche nach Rezepten, Zutaten..." />
				<button>Suchen</button>
			</div>
		</div>
	</section>

	<!-- Kategorien -->
	<section class="categories">
		<h2>Kategorien</h2>
		<div class="category-list">
			<div class="category-card">Vorspeisen</div>
			<div class="category-card">Hauptgerichte</div>
			<div class="category-card">Desserts</div>
			<div class="category-card">Vegetarisch</div>
			<div class="category-card">Snacks</div>
			<div class="category-card">Getränke</div>
			<div class="category-card">High Protein</div>
		</div>
	</section>

	<!-- Beliebte Rezepte -->
	<section class="popular">
        <h2>Beliebte Rezepte</h2>
        <div class="recipe-list">
            <div class="recipe-card">
                <img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=400&q=80" alt="Rezept 1" />
                <div class="recipe-title">Rezept 1</div>
            </div>
            <div class="recipe-card">
                <img src="https://images.unsplash.com/photo-1519864600265-abb23847ef2c?auto=format&fit=crop&w=400&q=80" alt="Rezept 2" />
                <div class="recipe-title">Rezept 2</div>
            </div>
            <div class="recipe-card">
                <img src="https://images.unsplash.com/photo-1464306076886-debca5e8a6b0?auto=format&fit=crop&w=400&q=80" alt="Rezept 3" />
                <div class="recipe-title">Rezept 3</div>
            </div>
            <div class="recipe-card">
                <img src="https://images.unsplash.com/photo-1525130413817-d9f869a4a0d0?auto=format&fit=crop&w=400&q=80" alt="Rezept 4" />
                <div class="recipe-title">Rezept 4</div>
            </div>
            <div class="recipe-card">
                <img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=400&q=80" alt="Rezept 5" />
                <div class="recipe-title">Rezept 5</div>
            </div>
        </div>
    </section>

	<!-- Auth-Formular bleibt erhalten, aber weiter unten -->
	{#if showAuth && !loggedIn}
		<section class="auth-section">
			<h2>Registrieren</h2>
			<input bind:value={regUsername} placeholder="Benutzername" />
			<input bind:value={regEmail} placeholder="Email" />
			<input bind:value={regPassword} type="password" placeholder="Passwort" />
			<button onclick={handleRegister}>Registrieren</button>
			<h2>Login</h2>
			<input bind:value={loginUsername} placeholder="Benutzername" />
			<input bind:value={loginPassword} type="password" placeholder="Passwort" />
			<button onclick={handleLogin}>Anmelden</button>
			{#if errorMsg}
				<p style="color: red">{errorMsg}</p>
			{/if}
		</section>
	{/if}
</main>

<style>
	main {
		font-family: 'Segoe UI', sans-serif;
		background: #f8f5f0;
		min-height: 100vh;
	}
	.hero {
		background: url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80') center/cover no-repeat;
		color: #fff;
		padding: 4rem 0 6rem 0;
		text-align: center;
		position: relative;
	}
	.hero::after {
		content: '';
		position: absolute;
		top: 0; left: 0; right: 0; bottom: 0;
		background: rgba(0,0,0,0.45);
		z-index: 1;
	}
	.hero-content {
		position: relative;
		z-index: 2;
		max-width: 600px;
		margin: 0 auto;
	}
	.hero h1 {
		font-size: 3rem;
		margin-bottom: 0.5rem;
		letter-spacing: 2px;
		font-weight: 700;
	}
	.hero p {
		font-size: 1.3rem;
		margin-bottom: 2rem;
	}
	.search-bar {
		display: flex;
		justify-content: center;
		gap: 0.5rem;
	}
	.search-bar input {
		padding: 0.7rem 1rem;
		border-radius: 8px 0 0 8px;
		border: none;
		width: 60%;
		font-size: 1rem;
	}
	.search-bar button {
		padding: 0.7rem 1.5rem;
		border-radius: 0 8px 8px 0;
		border: none;
		background: #845b2f;
		color: #fff;
		font-size: 1rem;
		cursor: pointer;
		font-weight: 600;
		transition: background 0.2s;
	}
	.search-bar button:hover {
		background: #a97c50;
	}
	.categories {
		max-width: 900px;
		margin: 2.5rem auto 1.5rem auto;
		padding: 0 1rem;
	}
	.categories h2 {
		color: #845b2f;
		margin-bottom: 1rem;
		font-size: 1.5rem;
	}
	.category-list {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		justify-content: center;
	}
	.category-card {
		background: #fff;
		border-radius: 16px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.07);
		padding: 1.2rem 2.2rem;
		font-size: 1.1rem;
		color: #845b2f;
		font-weight: 500;
		cursor: pointer;
		transition: box-shadow 0.2s, background 0.2s;
	}
	.category-card:hover {
		background: #f3e7d7;
		box-shadow: 0 4px 16px rgba(132,91,47,0.12);
	}
	.popular {
		max-width: 900px;
		margin: 2.5rem auto 1.5rem auto;
		padding: 0 1rem;
	}
	.popular h2 {
		color: #845b2f;
		margin-bottom: 1rem;
		font-size: 1.5rem;
	}
	.recipe-list {
		display: flex;
		gap: 1.5rem;
		flex-wrap: wrap;
		justify-content: center;
	}
	.recipe-card {
		background: #fff;
		border-radius: 16px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.07);
		overflow: hidden;
		width: 220px;
		text-align: center;
		transition: box-shadow 0.2s;
		cursor: pointer;
	}
	.recipe-card:hover {
		box-shadow: 0 4px 16px rgba(132,91,47,0.12);
	}
	.recipe-card img {
		width: 100%;
		height: 140px;
		object-fit: cover;
	}
	.recipe-title {
		padding: 0.8rem 0.5rem;
		color: #845b2f;
		font-weight: 600;
		font-size: 1.1rem;
	}
	.auth-section {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		z-index: 1000;
		
		/* Optische Anpassungen */
		max-width: 400px;
		width: 90%;
		background: #fff;
		border-radius: 12px;
		box-shadow: 0 8px 32px rgba(0,0,0,0.2);
		padding: 2rem 2.5rem;
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
		z-index: 10;
	}
</style>
