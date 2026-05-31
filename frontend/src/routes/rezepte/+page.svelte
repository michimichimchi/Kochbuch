<script lang="ts">
    import { page } from '$app/stores';

    type Recipe = {
        id: number;
        category_id: number;
        title: string;
        time?: number | null;
        paragraph?: string | null;
        image?: string | null;
        difficulty?: number | null;
    };

    // 1. NEU: Wir fangen jetzt BEIDES aus der URL ab (Suche und Kategorie)
    let searchQuery = $derived($page.url.searchParams.get('q') || "");
    let categoryQuery = $derived($page.url.searchParams.get('category') || "");

    let recipes = $state<Recipe[]>([]);
    let loading = $state(true);
    let errorMsg = $state("");

    // 2. NEU: $effect gibt jetzt Suche UND Kategorie an die Lade-Funktion weiter
    $effect(() => {
        ladeRezepte(searchQuery, categoryQuery);
    });

    async function ladeRezepte(query: string, category: string) {
        loading = true;
        errorMsg = "";
        try {
            // 3. NEU: URLSearchParams baut das ?search=...&category=... fehlerfrei zusammen
            const params = new URLSearchParams();
            if (query) params.append("search", query);
            if (category) params.append("category", category); 
            
            // Anfrage an das Backend schicken (jetzt mit den flexiblen Parametern!)
            const response = await fetch(`http://localhost:8000/recipes?${params.toString()}`);

            if (!response.ok) {
                throw new Error("Rezepte konnten nicht geladen werden");
            }

            recipes = await response.json();
        } catch (error) {
            errorMsg = (error as Error).message;
        } finally {
            loading = false;
        }
    }

    function hasValidImage(image?: string | null) {
        return image && image.startsWith("http");
    }
</script>

<main>
    <section class="recipes">
        <h1>Alle Rezepte</h1>

        {#if loading}
            <p class="info">Rezepte werden geladen...</p>
        {:else if errorMsg}
            <p class="error">{errorMsg}</p>
        {:else if recipes.length === 0}
            <p class="info">Noch keine Rezepte vorhanden.</p>
        {:else}
            <div class="recipe-list">
                {#each recipes as recipe}
                    <a class="recipe-card" href={`/rezepte/${recipe.id}`}>
                        {#if hasValidImage(recipe.image)}
                            <img src={recipe.image} alt={recipe.title} />
                        {:else}
                            <div class="image-placeholder">🍲</div>
                        {/if}

                        <div class="recipe-content">
                            <div class="recipe-title">{recipe.title}</div>

                            <div class="recipe-meta">
                                {#if recipe.time}
                                    <span>⏱ {recipe.time} Min.</span>
                                {/if}

                                {#if recipe.difficulty}
                                    <span>💪 {recipe.difficulty}/5</span>
                                {/if}
                            </div>
                        </div>
                    </a>
                {/each}
            </div>
        {/if}
    </section>
</main>

<style>
    main {
        font-family: 'Segoe UI', sans-serif;
        background: #f8f5f0;
        min-height: 100vh;
        padding: 3rem 1rem;
    }

    .recipes {
        max-width: 900px;
        margin: 0 auto;
    }

    h1 {
        color: #845b2f;
        margin-bottom: 1.5rem;
        font-size: 2rem;
    }

    .recipe-list {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        justify-content: flex-start;
    }

    .recipe-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        overflow: hidden;
        width: 260px;
        transition: box-shadow 0.2s;
    }

    .recipe-card:hover {
        box-shadow: 0 4px 16px rgba(132,91,47,0.12);
    }

    .recipe-card img,
    .image-placeholder {
        width: 100%;
        height: 140px;
    }

    .recipe-card img {
        object-fit: cover;
    }

    .image-placeholder {
        background: #f3e7d7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
    }

    .recipe-content {
        padding: 0.9rem;
    }

    .recipe-title {
        color: #845b2f;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .recipe-meta {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
        color: #a97c50;
        font-size: 0.9rem;
        margin-bottom: 0.6rem;
    }

    .recipe-content p {
        color: #4b4035;
        font-size: 0.95rem;
        line-height: 1.4;
        margin: 0;
    }

    .info,
    .error {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        padding: 1rem;
    }

    .error {
        color: #b00020;
    }

    .recipe-card {
    text-decoration: none;
    color: inherit;
    }
</style>