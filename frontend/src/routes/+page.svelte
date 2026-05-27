<script lang="ts">
    import { onMount } from "svelte";
    import { isLoggedIn } from '$lib/api';
    import { goto } from '$app/navigation';

    // Zustand, ob der Benutzer eingeloggt ist
    let loggedIn = $state(false);
    
    // Variablen für Top 5 Rezepte
    let topRecipes = $state<any[]>([]);
    let loadingTop = $state(true);
    
    // Überprüft beim Laden der Seite den Login UND holt die Top-Rezepte
    onMount(async () => {
        loggedIn = isLoggedIn();
        
        // NEU: Die besten Rezepte vom Backend holen
        try {
            const res = await fetch("http://localhost:8000/recipes/top");
            if (res.ok) {
                topRecipes = await res.json();
            }
        } catch (error) {
            console.error("Fehler beim Laden der Top-Rezepte:", error);
        } finally {
            loadingTop = false;
        }
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
        <h2>Beliebte Rezepte ⭐</h2>
        <div class="recipe-list">
            
            {#if loadingTop}
                <p style="color: #845b2f;">Die best bewerteten Rezepte 🍳</p>
            {:else if topRecipes.length === 0}
                <p style="color: #845b2f;">Es wurden noch keine Rezepte bewertet. Sei der Erste!</p>
            {:else}
                {#each topRecipes as recipe}
                    <a class="recipe-card" href={`/rezepte/${recipe.id}`} style="text-decoration: none;">
                        
                        {#if recipe.image && recipe.image.startsWith("http")}
                            <img src={recipe.image} alt={recipe.title} />
                        {:else}
                            <div style="width: 100%; height: 140px; background: #f3e7d7; display: flex; align-items: center; justify-content: center; font-size: 3rem;">🍲</div>
                        {/if}

                        <div class="recipe-title">{recipe.title}</div>
                        
                        <div style="font-size: 0.85rem; color: #a97c50; padding-bottom: 0.8rem; display: flex; justify-content: space-around;">
                            {#if recipe.time}<span>⏱ {recipe.time} Min.</span>{/if}
                            {#if recipe.difficulty}<span>💪 {recipe.difficulty}/5</span>{/if}
                        </div>
                    </a>
                {/each}
            {/if}
            
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
