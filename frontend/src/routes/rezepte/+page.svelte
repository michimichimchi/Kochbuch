<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { fetchPublic } from '$lib/api';

    // Suchbegriff aus URL holen
    let searchQuery = $derived($page.url.searchParams.get('q') || "");
    let searchInput = $state(searchQuery);
    let recipes = $state<{ id: number; title: string; time: number; difficulty: number; image: string }[]>([]);
    let isLoading = $state(false);
    let error = $state("");

    // Rezepte laden, wenn sich der Suchbegriff ändert
    $effect(() => {
        ladeRezepte(searchQuery);
    });

    async function ladeRezepte(query: string) {
        isLoading = true;
        error = "";
        try {
            // API-Call: /rezepte?search=...
            const q = query ? `?search=${encodeURIComponent(query)}` : "";
            recipes = await fetchPublic(`/recipes${q}`);
        } catch (e) {
            error = (e as Error).message;
            recipes = [];
        } finally {
            isLoading = false;
        }
    }

    // Sucht beim Absenden des Formulars
    function handleSearch(e: Event) {
        e.preventDefault();
        // Navigiert mit neuem Suchbegriff in der URL
        goto(`/rezepte?q=${encodeURIComponent(searchInput)}`);
    }
</script>

<div class="results-container">
    <div class="header">
        <form onsubmit={handleSearch} class="search-form">
            <input type="text" bind:value={searchInput} placeholder="Nach was suchst du heute? 🍳" />
            <button type="submit">Suchen</button>
        </form>
        
        {#if searchQuery}
            <h1>Suchergebnisse für "{searchQuery}"</h1>
        {:else}
            <h1>Alle Rezepte</h1>
            <p>Entdecke unsere gesamte Sammlung.</p>
        {/if}
    </div>

{#if isLoading}
        <div class="loading">Suchen... 🍳</div>
    {:else if error}
        <div class="no-results">{error}</div>
    {:else if recipes.length === 0}
        <div class="no-results">Leider keine Rezepte gefunden. Versuch einen anderen Begriff!</div>
    {:else}
        <div class="recipe-grid">
            {#each recipes as recipe (recipe.id)}
                <div class="recipe-card">
                    <div class="no-image">🍲 Rezept</div>
                    <div class="card-info">
                        <h3>{recipe.title}</h3>
                        <div class="meta">
                            <span style="font-size: 0.85rem; line-height: 1.4;">
                                <strong>Zutaten:</strong><br/>
                                {#if recipe.ingredients}
                                    {recipe.ingredients.substring(0, 50)}...
                                {:else}
                                    Keine Angaben
                                {/if}
                            </span>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .results-container {
        max-width: 1100px;
        margin: 2rem auto 5rem auto;
        padding: 0 1.5rem;
    }
    .header {
        margin-bottom: 2rem;
        border-bottom: 2px solid #f3e7d7;
        padding-bottom: 1rem;
    }
    .header h1 {
        color: #845b2f;
        margin: 0 0 0.5rem 0;
    }
    .header p {
        color: #777;
        margin: 0;
    }
    .loading, .no-results {
        text-align: center;
        padding: 4rem 0;
        color: #888;
        font-size: 1.2rem;
    }
    .recipe-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 2rem;
    }
    .recipe-card {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        overflow: hidden;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(132,91,47,0.15);
    }
    .recipe-card img, .no-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .no-image {
        background: #eee;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #aaa;
    }
    .card-info {
        padding: 1.2rem;
    }
    .card-info h3 {
        margin: 0 0 1rem 0;
        color: #333;
        font-size: 1.2rem;
    }
    .meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        color: #666;
        background: #f8f5f0;
        padding: 0.5rem;
        border-radius: 6px;
        /* --- Suchleiste auf der Ergebnisseite --- */
    .search-form {
        display: flex;
        gap: 0.8rem;
        margin-bottom: 1.5rem;
        max-width: 600px;
    }
    
    .search-form input {
        flex: 1; /* Nimmt den restlichen Platz ein */
        padding: 0.8rem 1.2rem;
        border: 2px solid #eaddcf;
        border-radius: 8px;
        font-size: 1.05rem;
        font-family: inherit;
        outline: none;
        transition: border-color 0.2s, box-shadow 0.2s;
        background-color: #fff;
    }
    
    .search-form input:focus {
        border-color: #845b2f;
        box-shadow: 0 0 0 3px rgba(132,91,47,0.1);
    }
    
    .search-form button {
        padding: 0 1.8rem;
        background-color: #845b2f;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s, transform 0.1s;
    }
    
    .search-form button:hover {
        background-color: #6a4925;
    }
    
    .search-form button:active {
        transform: scale(0.98); /* Kleiner Klick-Effekt */
    }
    }
</style>