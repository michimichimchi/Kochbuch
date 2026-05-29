<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { page } from '$app/state';
    import { isLoggedIn } from '$lib/api';

    let title = $state("");
    let category_id = $state(2);
    let time = $state<number | "">("");
    let difficulty = $state(1);
    let paragraph = $state("");
    let image = $state("");
    let errorMsg = $state("");
    let loading = $state(true);
    let is_public = $state(true);
    
    let ingredients = $state<{ name: string; amount: string | number; unit: string }[]>([]);

    const recipeId = page.params.id;

    onMount(async () => {
        if (!isLoggedIn()) {
            goto('/login');
            return;
        }

        try {
            // Aktuelle Rezeptdaten laden
            const res = await fetch(`http://localhost:8000/recipes/${recipeId}`);
            if (!res.ok) throw new Error("Rezept konnte nicht geladen werden");
            
            const data = await res.json();
            title = data.title;
            category_id = data.category_id;
            time = data.time ?? "";
            difficulty = data.difficulty ?? 1;
            paragraph = data.paragraph ?? "";
            image = data.image ?? "";
            is_public = data.is_public ?? true;
            
            if (data.ingredients && data.ingredients.length > 0) {
                ingredients = data.ingredients.map((i: any) => ({
                    name: i.name,
                    amount: i.amount ?? "",
                    unit: i.unit ?? ""
                }));
            } else {
                ingredients = [{ name: "", amount: "", unit: "" }];
            }
        } catch (error) {
            errorMsg = (error as Error).message;
        } finally {
            loading = false;
        }
    });

    function addIngredient() {
        ingredients.push({ name: "", amount: "", unit: "" });
    }

    function removeIngredient(index: number) {
        ingredients.splice(index, 1);
    }

    async function handleSubmit(event: Event) {
        event.preventDefault();
        errorMsg = "";
        const token = localStorage.getItem('token');
        if (!token) {
            errorMsg = "Du bist nicht eingeloggt.";
            return;
        }

        const validIngredients = ingredients
            .filter(i => i.name.trim() !== "")
            .map(i => ({
                name: i.name.trim(),
                amount: i.amount ? Number(i.amount) : null,
                unit: i.unit.trim() || null
            }));

        const payload = {
            title,
            category_id,
            time: time ? Number(time) : null,
            difficulty: Number(difficulty),
            paragraph: paragraph.trim() || null,
            image: image.trim() || null,
            ingredients: validIngredients,
            is_public,
        };

        try {
            const res = await fetch(`http://localhost:8000/recipes/${recipeId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Fehler beim Aktualisieren des Rezepts");
            }

            // Zurück zur Detailansicht navigieren
            goto(`/rezepte/${recipeId}`);
        } catch (error) {
            errorMsg = (error as Error).message;
        }
    }
</script>

<main class="form-container">
    <h1>Rezept bearbeiten</h1>

    {#if loading}
        <p>Daten werden geladen...</p>
    {:else}
        {#if errorMsg}
            <p class="error">{errorMsg}</p>
        {/if}

        <form onsubmit={handleSubmit}>
            <div class="form-group">
                <label>Titel des Rezepts *</label>
                <input type="text" bind:value={title} required />
            </div>

        <div class="form-row">
            <div class="form-group">
                <label>Kategorie *</label>
                <select bind:value={category_id}>
                    <option value={1}>Vorspeise</option>
                    <option value={2}>Hauptgericht</option>
                    <option value={3}>Dessert</option>
                </select>
            </div>

            <div class="form-group">
                <label>Öffentlichkeit</label>
                <select bind:value={is_public}>
                    <option value={true}>Öffentlich</option>
                    <option value={false}>Privat</option>
                </select>
            </div>
        </div>

            <div class="form-row">
                <div class="form-group">
                    <label>Dauer (Minuten)</label>
                    <input type="number" bind:value={time} min="1" />
                </div>
                <div class="form-group">
                    <label>Schwierigkeit (1-5)</label>
                    <input type="number" bind:value={difficulty} min="1" max="5" />
                </div>
            </div>

            <div class="form-group">
                <label>Bild URL</label>
                <input type="url" bind:value={image} />
            </div>

            <div class="form-group">
                <label>Zutaten</label>
                {#each ingredients as ingredient, index}
                    <div class="ingredient-row">
                        <input type="text" bind:value={ingredient.name} placeholder="Name" required />
                        <input type="number" bind:value={ingredient.amount} placeholder="Menge" class="small-input" />
                        <input type="text" bind:value={ingredient.unit} placeholder="Einheit" class="small-input" />
                        {#if ingredients.length > 1}
                            <button type="button" class="remove-btn" onclick={() => removeIngredient(index)}>✖</button>
                        {/if}
                    </div>
                {/each}
                <button type="button" class="add-btn" onclick={addIngredient}>+ Zutat hinzufügen</button>
            </div>

            <div class="form-group">
                <label>Zubereitungsschritte</label>
                <textarea bind:value={paragraph}></textarea>
            </div>

            <button type="submit" class="submit-btn">Änderungen speichern</button>
        </form>
    {/if}
</main>

<style>
    .form-container {
        max-width: 600px;
        margin: 2rem auto;
        background: #fff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        color: #845b2f;
    }
    .form-group { margin-bottom: 1.2rem; }
    .form-row { display: flex; gap: 1rem; }
    .form-row .form-group { flex: 1; }
    label { display: block; font-weight: 600; margin-bottom: 0.4rem; }
    input, select, textarea {
        width: 100%;
        padding: 0.6rem;
        border: 1px solid #e0d6c3;
        border-radius: 6px;
        box-sizing: border-box;
        font-family: inherit;
    }
    textarea { min-height: 120px; resize: vertical; }
    .ingredient-row { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
    .small-input { width: 80px; }
    button { cursor: pointer; border: none; border-radius: 6px; padding: 0.6rem 1rem; font-weight: 600; }
    .add-btn { background: #f3e7d7; color: #845b2f; margin-top: 0.5rem; }
    .remove-btn { background: #ffcccc; color: #b00020; }
    .submit-btn { width: 100%; background: #845b2f; color: #fff; padding: 0.8rem; font-size: 1.1rem; margin-top: 1rem; transition: background 0.2s; }
    .submit-btn:hover { background: #a97c50; }
    .error { color: #b00020; background: #ffe6e6; padding: 0.8rem; border-radius: 6px; margin-bottom: 1rem; }
</style>