<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { fetchProtected, isLoggedIn } from '$lib/api';

    type Recipe = {
        id: number;
        title: string;
        time?: number | null;
        image?: string | null;
        difficulty?: number | null;
        is_public?: boolean | null;
    };

    let recipes = $state<Recipe[]>([]);
    let loading = $state(true);
    let errorMsg = $state("");

    onMount(async () => {
        if (!isLoggedIn()) {
            goto('/login');
            return;
        }

        try {
            // Holt die Rezepte des aktuell eingeloggten Nutzers
            recipes = await fetchProtected<Recipe[]>('/recipes/me');
        } catch (error) {
            errorMsg = (error as Error).message;
        } finally {
            loading = false;
        }
    });

    async function handleDelete(id: number, event: Event) {
        event.preventDefault(); // Verhindert, dass der Link zur Detailseite ausgelöst wird
        
        if (!confirm("Möchtest du dieses Rezept wirklich löschen?")) return;

        const token = localStorage.getItem("token");
        try {
            const res = await fetch(`http://localhost:8000/recipes/${id}`, {
                method: "DELETE",
                headers: { "Authorization": `Bearer ${token}` }
            });

            if (!res.ok) throw new Error("Fehler beim Löschen");
            
            // Rezept aus dem Frontend-Array entfernen (UI aktualisiert sich automatisch)
            recipes = recipes.filter(r => r.id !== id);
        } catch (error) {
            alert((error as Error).message);
        }
    }

    function handleEdit(recipeId: number, event: Event) {
        event.preventDefault();
        event.stopPropagation(); // Verhindert, dass die Rezept-Karte angeklickt wird
        goto(`/rezepte/${recipeId}/bearbeiten`);
    }
</script>

<main class="container">
    <h1>Meine Rezepte</h1>
    <p class="subtitle">Hier findest du alle von dir erstellten Kochrezepte.</p>

    {#if loading}
        <p class="info">Rezepte werden geladen...</p>
    {:else if errorMsg}
        <p class="error">Fehler beim Laden: {errorMsg}</p>
    {:else if recipes.length === 0}
        <div class="empty-state">
            <p>Du hast bisher noch keine eigenen Rezepte hinzugefügt.</p>
            <a href="/rezept-neu" class="btn">Erstes Rezept erstellen ✚</a>
        </div>
    {:else}
        <div class="recipe-list">
            {#each recipes as recipe}
                <a class="recipe-card" href={`/rezepte/${recipe.id}`}>
                    {#if recipe.image && recipe.image.startsWith('http')}
                        <img src={recipe.image} alt={recipe.title} />
                    {:else}
                        <div class="image-placeholder">🍲</div>
                    {/if}
                    <div class="recipe-content">
                        <div class="recipe-title">{recipe.title}</div>
                        <div class="recipe-meta">
                            {#if recipe.time}<span>⏱ {recipe.time} Min.</span>{/if}
                            {#if recipe.difficulty}<span>💪 {recipe.difficulty}/5</span>{/if}
                            {#if recipe.is_public != null}<span>{recipe.is_public ? '🌍 Öffentlich' : '🔒 Privat'}</span>{/if}
                        </div>
                        <button class="edit-btn" onclick={(e) => handleEdit(recipe.id, e)}>
                            ✏️ Bearbeiten
                        </button>
                        <button class="delete-btn" onclick={(e) => handleDelete(recipe.id, e)}>
                            🗑️ Löschen
                        </button>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</main>

<style>
    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 3rem 1rem;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 { color: #845b2f; margin-bottom: 0.5rem; }
    .subtitle { color: #a97c50; margin-bottom: 2rem; }
    .recipe-list { display: flex; gap: 1.5rem; flex-wrap: wrap; }
    .recipe-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        overflow: hidden;
        width: 260px;
        text-decoration: none;
        color: inherit;
        transition: box-shadow 0.2s;
        display: flex;
        flex-direction: column;
    }
    .recipe-card:hover {
        box-shadow: 0 4px 16px rgba(132,91,47,0.12);
    }
    img, .image-placeholder { width: 100%; height: 140px; object-fit: cover; }
    .image-placeholder {
        background: #f3e7d7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
    }
    .recipe-content { padding: 1rem; display: flex; flex-direction: column; flex-grow: 1; }
    .recipe-title { color: #845b2f; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .recipe-meta { display: flex; gap: 0.8rem; color: #a97c50; font-size: 0.9rem; margin-bottom: 1rem; }
    
    .delete-btn {
        margin-top: auto;
        background: #ffe6e6;
        color: #b00020;
        border: none;
        border-radius: 6px;
        padding: 0.5rem;
        cursor: pointer;
        font-weight: 600;
        transition: background 0.2s;
        width: 100%;
    }
    .delete-btn:hover { background: #ffcccc; }

    .info { color: #845b2f; }
    .error { color: #b00020; background: #ffe6e6; padding: 1rem; border-radius: 8px; }
    .empty-state { text-align: center; padding: 3rem; background: #fff; border-radius: 16px; color: #845b2f; }
    .btn {
        display: inline-block;
        margin-top: 1rem;
        background: #845b2f;
        color: #fff;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
    }
    .btn:hover { background: #a97c50; }

    .edit-btn {
        margin-top: auto; /* Schiebt die Buttons an das untere Kartenende */
        margin-bottom: 0.5rem; /* Erzeugt Abstand zum darunterliegenden Löschen-Button */
        background: #f3e7d7;
        color: #845b2f;
        border: none;
        border-radius: 6px;
        padding: 0.5rem;
        cursor: pointer;
        font-weight: 600;
        transition: background 0.2s;
        width: 100%;
        text-align: center;
    }
    .edit-btn:hover { 
        background: #e0d6c3; 
    }
</style>