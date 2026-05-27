<script lang="ts">
    import {onMount} from "svelte";
    import { isLoggedIn,} from '$lib/api';
	import { goto } from '$app/navigation';

    // Zustand, ob der Benutzer eingeloggt ist
    let loggedIn = $state(false);
	
	// Überprüft beim Laden der Seite, ob der Benutzer bereits eingeloggt ist
	onMount(() => {
		loggedIn = isLoggedIn();
	})

	// Variable für das, was der Nutzer eintippt
    let searchQuery = $state("");
	// Die Funktion, die beim Klick/Enter ausgeführt wird
    function handleSearch(event: Event) {
        event.preventDefault(); // Blockiert den Standard-Seiten-Reload
        
        if (searchQuery.trim() !== "") {
            // Leitet weiter zu /rezepte?q=DeinSuchbegriff
            goto(`/rezepte?q=${encodeURIComponent(searchQuery.trim())}`);
        }
    }
</script>

{#if !loggedIn}
    <a href="/login" class="auth-btn">Anmelden</a>
{/if}


<main>
    <section class="hero">
        <div class="hero-content">
            <h1>Kochbuch</h1>
            <p>Entdecke, teile und genieße die besten Rezepte!</p>
            
            <form onsubmit={handleSearch} class="search-bar">
                <input 
                    type="text" 
                    placeholder="Suche nach Rezepten, Zutaten..." 
                    bind:value={searchQuery}
                />
                <button type="submit">Suchen</button>
            </form>
            
        </div>
    </section>
	
	<!-- Kategorien -->
	<section class="categories">
		<h2>Kategorien</h2>
		<div class="category-list">
			<div class="category-card">Vorspeisen</div>
			<div class="category-card">Hauptgerichte</div>
			<div class="category-card">Desserts</div>
			<div class="category-card">Snacks</div>
			<div class="category-card">Getränke</div>
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

	/* Aussehen des Anmelde-Buttons oben rechts */
	.auth-btn {
		position: fixed;
		top: 1rem;
		right: 1rem;
		background-color: #fff;
		color: rgb(132, 91, 47);
		border: 2px solid rgb(132, 91, 47);
		border-radius: 8px;
		padding: 0.5rem 1.2rem;
		font-size: 1rem;
		cursor: pointer;
		z-index: 10;
		text-decoration: none;
	}
</style>
