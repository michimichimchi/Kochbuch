<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/state";
    import { isLoggedIn, fetchProtected } from "$lib/api";

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
    };

    let recipe = $state<Recipe | null>(null);
    let loading = $state(true);
    let errorMsg = $state("");

    let loggedIn = $state(false);
    let rating = $state(5);
    let comment = $state("");
    let successMsg = $state("");

    const API_URL = "http://localhost:8000";

    onMount(async () => {
        loggedIn = isLoggedIn();

        try {
            const res = await fetch(`${API_URL}/recipes/${page.params.id}`);

            if (!res.ok) {
                throw new Error("Rezept konnte nicht geladen werden");
            }

            recipe = await res.json();
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

        try {
            await fetchProtected("/evaluations", {
                method: "POST",
                body: JSON.stringify({
                    recipe_id: recipe.id,
                    rating,
                    comment
                })
            });

            successMsg = "Bewertung gespeichert.";
            comment = "";
            rating = 5;
        } catch (error) {
            errorMsg = (error as Error).message;
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

                <div class="meta">
                    {#if recipe.time}
                        <span>⏱ {recipe.time} Min.</span>
                    {/if}

                    {#if recipe.difficulty}
                        <span>💪 Schwierigkeit {recipe.difficulty}/5</span>
                    {/if}

                    <ul>
                        {#each recipe.ingredients as ingredient}
                            <li>
                                <span class="amount">
                                    {#if ingredient.amount}{ingredient.amount}{/if} 
                                    {#if ingredient.unit}{ingredient.unit}{/if}
                                </span>
                                <span class="name">{ingredient.name}</span>
                            </li>
                        {/each}
                    </ul>

                </div>

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

                <button onclick={submitEvaluation}>Absenden</button>

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
    }

    h1,
    h2 {
        color: #845b2f;
        margin-top: 0;
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
    padding: 1;
    margin: 0.2rem 0;
    display: grid;
    grid-template-columns: max-content auto;
    gap: 0.2rem 1rem;
    }

    li {
    display: contents;
        }
</style>