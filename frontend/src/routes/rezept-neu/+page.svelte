<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { isLoggedIn } from '$lib/api';

    // Svelte 5 Runes für die Formularfelder
    let title = $state("");
    let category_id = $state(2); // Standard: Hauptgericht
    let time = $state<number | "">("");
    let difficulty = $state(1);
    let paragraph = $state("");
    let image = $state("");
    let is_public = $state(true); // Neu: Öffentlichkeit des Rezepts
    let errorMsg = $state("");

    // Dynamische Liste für die Zutaten
    let ingredients = $state([{ name: "", amount: "", unit: "" }]);

    // Prüfen, ob der Nutzer eingeloggt ist
    onMount(() => {
        if (!isLoggedIn()) {
            goto('/login');
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

        // Leere Zutaten herausfiltern und Datentypen anpassen
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
            is_public,
            ingredients: validIngredients
        };

        try {
            const res = await fetch("http://localhost:8000/recipes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Fehler beim Anlegen des Rezepts");
            }

            const newRecipe = await res.json();
            // Nach erfolgreichem Speichern zur Detailseite des Rezepts weiterleiten
            goto(`/rezepte/${newRecipe.id}`);
        } catch (error) {
            errorMsg = (error as Error).message;
        }
    }
</script>

<main class="form-container">
    <h1>Neues Rezept anlegen</h1>

    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}

    <form onsubmit={handleSubmit}>
        <div class="form-group">
            <label>Titel des Rezepts *</label>
            <input type="text" bind:value={title} required placeholder="z. B. Spaghetti Bolognese" />
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
                <input type="number" bind:value={time} min="1" placeholder="z. B. 45" />
            </div>
            <div class="form-group">
                <label>Schwierigkeit (1-5)</label>
                <input type="number" bind:value={difficulty} min="1" max="5" />
            </div>
        </div>

        <div class="form-group">
            <label for="image">Bild URL</label>
            <input type="url" bind:value={image} placeholder="http://..." />
        </div>

        <div class="form-group">
            <label>Zutaten</label>
            {#each ingredients as ingredient, index}
                <div class="ingredient-row">
                    <input type="text" bind:value={ingredient.name} placeholder="Name (z.B. Mehl)" required />
                    <input type="number" bind:value={ingredient.amount} placeholder="Menge" class="small-input" min="1" />
                    <input type="text" bind:value={ingredient.unit} placeholder="Einheit (z.B. g)" class="small-input" />
                    {#if ingredients.length > 1}
                        <button type="button" class="remove-btn" onclick={() => removeIngredient(index)}>✖</button>
                    {/if}
                </div>
            {/each}
            <button type="button" class="add-btn" onclick={addIngredient}>+ Zutat hinzufügen</button>
        </div>

        <div class="form-group">
            <label>Zubereitungsschritte</label>
            <textarea bind:value={paragraph} placeholder="Wie wird es gekocht?"></textarea>
        </div>

        <button type="submit" class="submit-btn">Rezept speichern</button>
    </form>
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

    h1 {
        margin-top: 0;
        margin-bottom: 1.5rem;
    }

    .form-group {
        margin-bottom: 1.2rem;
    }

    .form-row {
        display: flex;
        gap: 1rem;
    }
    
    .form-row .form-group {
        flex: 1;
    }

    label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    input, select, textarea {
        width: 100%;
        padding: 0.6rem;
        border: 1px solid #e0d6c3;
        border-radius: 6px;
        box-sizing: border-box;
        font-family: inherit;
    }

    textarea {
        min-height: 120px;
        resize: vertical;
    }

    .ingredient-row {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .small-input {
        width: 80px;
    }

    button {
        cursor: pointer;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        font-weight: 600;
    }

    .add-btn {
        background: #f3e7d7;
        color: #845b2f;
        margin-top: 0.5rem;
    }

    .remove-btn {
        background: #ffcccc;
        color: #b00020;
    }

    .submit-btn {
        width: 100%;
        background: #845b2f;
        color: #fff;
        padding: 0.8rem;
        font-size: 1.1rem;
        margin-top: 1rem;
        transition: background 0.2s;
    }

    .submit-btn:hover {
        background: #a97c50;
    }

    .error {
        color: #b00020;
        background: #ffe6e6;
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
</style>