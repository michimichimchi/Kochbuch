<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/state";
    import { isLoggedIn } from "$lib/api";

    type Ingredient = {
        name: string;
        amount?: number | null;
        unit?: string | null;
    };

    type Recipe = {
        id: number;
        category_id: number;
        title: string;
        time?: number | null;
        paragraph?: string | null;
        image?: string | null;
        difficulty?: number | null;
        ingredients: Ingredient[];
        avg_rating?: number | null;
    };

    type Evaluation = {
        id: number;
        rating?: number | null;
        comment?: string | null;
        username?: string;
        user_id?: number;
        recipe_id?: number;
    };

    let recipe = $state<Recipe | null>(null);
    let evaluations = $state<Evaluation[]>([]);
    let loading = $state(true);
    let errorMsg = $state("");

    let loggedIn = $state(false);
    let rating = $state(5);
    let comment = $state("");
    let successMsg = $state("");
    let isFavorite = $state(false);

    const API_URL = "http://localhost:8000";

    async function loadEvaluations(recipeId: number | string) {
        const evalRes = await fetch(`${API_URL}/recipes/${recipeId}/evaluations`);

        if (evalRes.ok) {
            evaluations = await evalRes.json();
        }
    }

    onMount(async () => {
        loggedIn = isLoggedIn();

        try {
            const res = await fetch(`${API_URL}/recipes/${page.params.id}`);

            if (!res.ok) {
                throw new Error("Rezept konnte nicht geladen werden");
            }

            recipe = await res.json();
            await loadEvaluations(page.params.id!);

            if (loggedIn) {
                const token = localStorage.getItem("token");
                const favRes = await fetch(`${API_URL}/favorites/${page.params.id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (favRes.ok) {
                    const favData = await favRes.json();
                    isFavorite = favData.is_favorite;
                }
            }

        } catch (error) {
            errorMsg = (error as Error).message;
        } finally {
            loading = false;
        }
    });

    async function submitEvaluation() {
        errorMsg = "";
        successMsg = "";

        if (!recipe) return;

        const token = localStorage.getItem("token");

        if (!token) {
            errorMsg = "Du bist nicht eingeloggt.";
            return;
        }

        try {
            const res = await fetch(`${API_URL}/evaluations`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    recipe_id: recipe.id,
                    rating,
                    comment
                })
            });

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                throw new Error(data?.detail ?? "Bewertung konnte nicht gespeichert werden");
            }

            successMsg = "Bewertung gespeichert.";
            comment = "";
            rating = 5;

            await loadEvaluations(recipe.id);
        } catch (error) {
            errorMsg = (error as Error).message;
        }
    }

    async function toggleFavorite() {
        const token = localStorage.getItem("token");
        if (!token || !recipe) return;

        if (isFavorite && !confirm("Möchtest du dieses Rezept wirklich aus deinen Favoriten entfernen?")) return;

        const method = isFavorite ? "DELETE" : "POST";
        const res = await fetch(`${API_URL}/favorites/${recipe.id}`, {
            method,
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.ok || res.status === 204) {
            isFavorite = !isFavorite;
        }
    }

    function hasValidImage(image?: string | null) {
        return image && image.startsWith("http");
    }

</script>

<main>
    {#if loading}
        <p class="box">Rezept wird geladen...</p>
    {:else if errorMsg && !recipe}
        <p class="box error">{errorMsg}</p>
    {:else if recipe}
        <section class="recipe-detail">
            {#if hasValidImage(recipe.image)}
                <img src={recipe.image} alt={recipe.title} />
            {:else}
                <div class="image-placeholder">🍲</div>
            {/if}

            <div class="content">
                <h1>{recipe.title}</h1>
                {#if loggedIn}
                    <button class="fav-btn" class:active={isFavorite} onclick={toggleFavorite}>
                        {isFavorite ? "In den Favoriten" : "Zu Favoriten hinzufügen"}
                    </button>
                {/if}

                <div class="meta">
                    {#if recipe.time}
                        <span>⏱ {recipe.time} Min.</span>
                    {/if}

                    {#if recipe.difficulty}
                        <span>💪 Schwierigkeit {recipe.difficulty}/5</span>
                    {/if}

                    {#if recipe.avg_rating}
                        <span>Bewertung: {recipe.avg_rating} ⭐</span>
                    {:else}
                        <span class="no-rating">(noch keine Bewertungen)</span>
                    {/if}
                </div>

                {#if recipe.ingredients?.length}
                    <ul>
                        {#each recipe.ingredients as ingredient}
                            <li>
                                <span class="amount">
                                    {#if ingredient.amount}{ingredient.amount}{/if}
                                    {#if ingredient.unit} {ingredient.unit}{/if}
                                </span>
                                <span class="name">{ingredient.name}</span>
                            </li>
                        {/each}
                    </ul>
                {/if}

                {#if recipe.paragraph}
                    <p>{recipe.paragraph}</p>
                {/if}
            </div>
        </section>

        <section class="evaluation">
            <h2>Bewerten & Kommentieren</h2>

            {#if loggedIn}
                <label>
                    Bewertung
                    <select bind:value={rating}>
                        <option value={1}>1 Stern</option>
                        <option value={2}>2 Sterne</option>
                        <option value={3}>3 Sterne</option>
                        <option value={4}>4 Sterne</option>
                        <option value={5}>5 Sterne</option>
                    </select>
                </label>

                <label>
                    Kommentar
                    <textarea bind:value={comment} placeholder="Dein Kommentar"></textarea>
                </label>

                <button type="button" onclick={submitEvaluation}>Absenden</button>

                {#if successMsg}
                    <p class="success">{successMsg}</p>
                {/if}

                {#if errorMsg}
                    <p class="error">{errorMsg}</p>
                {/if}
            {:else}
                <p>Du musst angemeldet sein, um eine Bewertung zu schreiben.</p>
            {/if}
        </section>

        <section class="evaluation">
            <h2>Kommentare</h2>

            {#if evaluations.length === 0}
                <p>Noch keine Kommentare vorhanden.</p>
            {:else}
                {#each evaluations as evaluation}
                    <div class="comment-card">
                        <strong>{evaluation.username ?? `User ${evaluation.user_id}`}</strong>

                        {#if evaluation.rating}
                            <div>{evaluation.rating} ⭐</div>
                        {/if}

                        {#if evaluation.comment}
                            <p>{evaluation.comment}</p>
                        {/if}
                    </div>
                {/each}
            {/if}
        </section>
    {/if}
</main>

<style>
    main {
        font-family: 'Segoe UI', sans-serif;
        background: #f8f5f0;
        min-height: 100vh;
        padding: 3rem 1rem;
    }

    .recipe-detail,
    .evaluation,
    .box {
        max-width: 850px;
        margin: 0 auto 2rem auto;
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        overflow: hidden;
    }

    .recipe-detail img,
    .image-placeholder {
        width: 100%;
        height: 320px;
    }

    .recipe-detail img {
        object-fit: cover;
    }

    .image-placeholder {
        background: #f3e7d7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 5rem;
    }

    .content,
    .evaluation,
    .box {
        padding: 1.5rem;
        position: relative
    }

    h1,
    h2 {
        color: #845b2f;
        margin-top: 0;
    }

    .title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    }

    .title-row h1 {
    margin: 0;
    }

    .meta {
        display: flex;
        gap: 1rem;
        color: #a97c50;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    p {
        color: #4b4035;
        line-height: 1.5;
    }

    label {
        display: block;
        color: #845b2f;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    select,
    textarea {
        display: block;
        width: 100%;
        margin-top: 0.4rem;
        border: 1px solid #e0d6c3;
        border-radius: 8px;
        padding: 0.7rem;
        font-family: inherit;
        box-sizing: border-box;
    }

    textarea {
        min-height: 110px;
        resize: vertical;
    }

    button {
        background: #845b2f;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.4rem;
        cursor: pointer;
        font-weight: 600;
    }

    button:hover {
        background: #a97c50;
    }

    .success {
        color: green;
    }

    .error {
        color: #b00020;
    }


    ul {
        list-style: none;
        padding: 0;
        margin: 0.2rem 0;
        display: grid;
        grid-template-columns: max-content auto;
        gap: 0.2rem 1rem;
    }

    li {
        display: contents;
    }

    .comment-card {
        padding: 1rem 0;
        border-bottom: 1px solid #eee;
    }

    .comment-card strong {
        display: block;
        margin-bottom: 0.25rem;
        color: #845b2f;
    }

    .fav-btn {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: #f3e7d7;
        color: #845b2f;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }

    .fav-btn:hover {
        background: #e0d6c3;
    }

    .fav-btn.active {
        background: #d4edda;
        color: #1a6b2f;
    }

    .fav-btn.active:hover {
        background: #b8dfc4;
    }

    .no-rating {
        font-size: 0.85rem;
        color: #b0a090;
        font-weight: 400;
    }

</style>