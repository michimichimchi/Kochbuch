import { writable } from 'svelte/store';
export const loggedInStore = writable(false);

/** Basis-URL des FastAPI-Backends */
const API_BASE = 'http://localhost:8000';

/** Hilfsfunktion: gibt den gespeicherten JWT zurück (oder null) */
function getToken(): string | null {
	return localStorage.getItem('token');
}

/** Hilfsfunktion: speichert den JWT im localStorage */
function saveToken(token: string): void {
	localStorage.setItem('token', token);
}

/** Hilfsfunktion: löscht den JWT (Logout) */
export function logout(): void {
	localStorage.removeItem('token');
	loggedInStore.set(false);
}

/** Gibt true zurück, wenn ein Token gespeichert ist */
export function isLoggedIn(): boolean {
	return getToken() !== null;
}

/**
 * Login via OAuth2 Password Flow.
 * Sendet username + password als Formular-Daten (nicht JSON!) an POST /token.
 * Speichert den erhaltenen access_token im localStorage.
 */
export async function login(username: string, password: string): Promise<void> {
	// TODO: Implementiert diese Funktion
	// Hinweis: URLSearchParams für Form-Daten verwenden
	//          Content-Type: 'application/x-www-form-urlencoded'
	//          Bei Erfolg: saveToken(data.access_token) aufrufen
	const res = await fetch(`${API_BASE}/token`, {                           // URL des Token-Endpunkts, z.B. http://localhost:8000/token
		method: "POST",                                                      // HTTP-Methode POST
		headers: { "Content-Type": "application/x-www-form-urlencoded" },    // Header für Form-Daten
		body: new URLSearchParams({ username, password})                     // Form-Daten mit username und password
	});
	if (!res.ok) throw new Error("Benutzername oder Passwort falsch");       // Fehlerbehandlung bei ungültigen Anmeldedaten, !res prüft, ob die Antwort keinen erfolgreichen Statuscode hat
	const data = await res.json();                                           // Antwort als JSON parsen, erwartet wird ein Objekt mit einem access_token-Feld
	saveToken(data.access_token);                                            // Funktion saveToken aufrufen, die Token im localStorage speichert, damit er für zukünftige Anfragen verwendet werden kann
	loggedInStore.set(true);
}

/**
 * Führt einen authentifizierten GET-Request aus.
 * Hängt den Bearer-Token aus dem localStorage als Authorization-Header an.
 */
export async function fetchProtected<T>(path: string, options: RequestInit = {}): Promise<T> {
    const token = getToken();                                          
    if (!token) throw new Error("Nicht eingeloggt");                     

    const res = await fetch(`${API_BASE}${path}`, {                      
        ...options, // <--- Packt method: "POST", body etc. aus
        headers: { 
            ...options.headers, // <--- Übernimmt z.B. unseren Content-Type
            Authorization: `Bearer ${token}` 
        }                    
    });

    if (res.status === 401) {                                            
        logout();
        throw new Error("Nicht autorisiert");
    }

    if (!res.ok) {
        const err: any = new Error("Fehler beim Abrufen der geschützten Daten");
        err.status = res.status;   
        throw err;
    }

    return res.json();                                                   
}

/**
 * Führt einen nicht authentifizierten GET-Request aus.
 */
export async function fetchPublic<T>(path: string): Promise<T> {      // Hier wird ein öffentlicher GET-Request durchgeführt, man muss nicht angemeldet sein -> ist somit für öffentliche Ressourcen
	// TODO: Implementiert diese Funktion
	const res = await fetch(`${API_BASE}${path}`);
	if (!res.ok) throw new Error("Fehler beim Abrufen der öffentlichen Daten");  // Fehlerbehandlung für ungültige Antworten / Fehler die auftreten wie z.B. 404 Not Found oder 500 Serverfehler
	return res.json();                 // Antwort als JSON parsen und zurückgeben, erwartet wird die öffentliche Ressource, z.B. eine Liste von Artikeln oder allgemeine Informationen, abhängig von der angeforderten Route
}

// TODO: Ergänzt hier eigene API-Funktionen, z. B.:
// export async function getItems() {
//   return fetchPublic<Item[]>('/items');
// }
//
// export async function createItem(data: { name: string; price: number }) {
//   const token = getToken();
//   const res = await fetch(`${API_BASE}/items`, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'Authorization': `Bearer ${token}`
//     },
//     body: JSON.stringify(data)
//   });
//   if (!res.ok) throw new Error('Erstellen fehlgeschlagen');
//   return res.json();
// }


// Hier wird die Registrierung eines neuen Benutzers durchgeführt, es werden die erforderlichen Daten (username, email, password) als JSON an den /register-Endpunkt gesendet
export async function register(username: string, email: string, password: string): Promise<void> {   
	const res = await fetch(`${API_BASE}/auth/register`, {              // URL des Registrierungs-Endpunkts, z.B. http://localhost:8000/register
		method: "POST",                                            // HTTP-Methode Post, da an Server gesendet wird
		headers: { "Content-Type": "application/json" },           // Header für JSON-Daten, damit das Backend die Daten als JSON interpretieren kann
		body: JSON.stringify({ username, email, password })        // JSON-String aus den übergebenen Parametern erstellen, damit sie im Request-Body gesendet werden können, erwartet wird ein Objekt mit den Feldern username, email und password
	});
	if (!res.ok) throw new Error("Benutzername oder E-Mail bereits vergeben");        // Fehlerbehandlung, wenn die Registrierung nicht erfolgreich war, z.B. weil der Benutzername oder die E-Mail bereits existiert, !res prüft, ob die Antwort keinen erfolgreichen Statuscode hat
	const data = await res.json();          // Antwort als JSON parsen, erwartet wird ein Objekt mit einem access_token-Feld, das den JWT enthält, damit der Nutzer nach der Registrierung automatisch eingeloggt wird
	saveToken(data.access_token);           // Funktion saveToken aufrufen, um Token im localStorage zu speichern
	loggedInStore.set(true);              // loggedInStore auf true setzen, damit die UI weiß, dass der Nutzer jetzt eingeloggt ist
}