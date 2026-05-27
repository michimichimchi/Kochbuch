from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from models import User, Recipe, Category

from auth import (
    DUMMY_HASH,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import Base, engine, get_db
import models
import schemas
from schemas import Token, UserRegister, UserResponse

# Tabellen anlegen (falls noch nicht vorhanden)
Base.metadata.create_all(bind=engine)

# Funktion, um Beispielrezepte anzulegen. Wird beim Start der Anwendung aufgerufen.
def seed_database():
    # aktuelle Datenbank-Session holen
    db = next(get_db())
    
    # Prüfen, ob Recipe einträge hat. wenn ja, dann wurde seed wahrscheinlich schon ausgeführt
    # und wird deshalb übersprungen. So werden doppelte Einträge und Datenbankfehler vermieden
    if db.query(Recipe).count() > 0:
        return  # DB hat schon Einträge, seeden überspringen
    
    # Kategorien anlegen
    # Kategorien in Liste gegeben. Liste wird geprüft, ob die category der Liste so schon 
    # in der DB existiert. Wenn nicht, wird sie angelegt. So werden doppelte Einträge vermieden.
    categories = ["Vorspeise", "Hauptgericht", "Dessert"]
    for cat in categories:
        if db.query(Category).filter_by(name=cat).first() is None:
            db.add(Category(name=cat))
    db.commit()
    
    # id aus Tabelle category holen, damit man diese für das Anlegen der Rezepte nehmen kann.
    # Die category_id ist nämlich Pflichtfeld in Tabelle Recipe (ForeignKey auf Category)
    starter = db.query(Category).filter_by(name="Vorspeise").first().id
    main_dish = db.query(Category).filter_by(name="Hauptgericht").first().id
    dessert = db.query(Category).filter_by(name="Dessert").first().id
    
    # Beispielrezepte anlegen
    recipes = [
        Recipe(title="Tomatensuppe", category_id=starter, time=10, difficulty=1,
               paragraph="Klassische Tomatensuppe mit frischen Kräutern."),
        Recipe(title="Salat", category_id=starter, time=20, difficulty=2,
               paragraph="Frischer gemischter Salat mit saisonalem Gemüse."),
        Recipe(title="Spaghetti Bolognese", category_id=main_dish, time=45, difficulty=2,
               paragraph="Italienische Pasta mit Hackfleisch-Tomatensoße."),
        Recipe(title="Pizza", category_id=main_dish, time=30, difficulty=1,
               paragraph="Leckere Pizza mit frischen Zutaten."),
        Recipe(title="Schokoladenmousse", category_id=dessert, time=60, difficulty=3,
               paragraph="Cremiges Mousse au Chocolat für besondere Anlässe."),
    ]
    
    # add_all() Rezepte werden im Arbeitsspeicher vorgemerkt
    # commit() speichert sie dann tatsächlich in der DB (INSERT-Befehl wird ausgeführt)
    db.add_all(recipes)
    db.commit()
    
# Funktion wird aufgerufen
seed_database()

app = FastAPI(title="Mein Projekt", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Erlaubt Anfragen von diesem Ursprung (Frontend-Entwicklungsserver)
    allow_credentials=True,  # Erlaubt das Senden von Cookies und Authentifizierungsinformationen
    allow_methods=["*"],  # Erlaubt alle HTTP-Methoden (GET, POST, etc.)
    allow_headers=["*"],  # Erlaubt alle Header (z.B. Authorization für Bearer-Token)
)

# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Authentifizierung
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Neuen Benutzer anlegen. Passwort wird als Argon2-Hash gespeichert."""
    # TODO: Implementiert diese Funktion
    # 1. Prüft, ob username oder email bereits existieren (→ 400)
    # 2. Passwort hashen mit get_password_hash()
    # 3. User-Objekt anlegen, in DB speichern, zurückgeben
    if db.query(User).filter(User.username == data.username).first() is not None: # Prüft, ob der zu erstellende Benutzername schon in der DB existiert
        raise HTTPException(status_code=400, detail="Username bereits vergeben")  # Wenn ja, code 400 asugeben und Fehlermeldung "Username bereits vergeben"
    if db.query(User).filter(User.email == data.email).first() is not None:       # gleiches Spiel für email
        raise HTTPException(status_code=400, detail="Email bereits vergeben")
    hashed_password = get_password_hash(data.password)                            # Funktion get_password_hash() aus auth.py aufrufen, um einen sicheren Hash des Passworts zu erzeugen  
    user = User(username=data.username, email=data.email, hashed_password=hashed_password)  # user Objekt mit den übergebenen Daten und dem erzeugten Hash anlegen
    db.add(user)       # User-Objekt zur DB-Session hinzufügen
    db.commit()        # Änderungen in der DB speichern (INSERT ausführen)
    db.refresh(user)   # Aktualisiert das user-Objekt mit den Daten aus der DB (z.B. automatisch generierte ID)
    return user        # User-Objekt zurückgeben (wird automatisch in UserResponse umgewandelt)


@app.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    OAuth2 Password Flow: Empfängt username + password als Formular-Daten.
    Gibt einen JWT zurück.
    """
    # TODO: Implementiert diese Funktion
    # 1. Benutzer anhand von form_data.username in der DB suchen
    # 2. Passwort mit verify_password() prüfen (Timing-Schutz: DUMMY_HASH nutzen)
    # 3. Bei Fehler: 401 zurückgeben (generische Meldung!)
    # 4. JWT mit create_access_token() erzeugen und zurückgeben
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None:
        verify_password(form_data.password, DUMMY_HASH) # Timing-Angriff-Schutz: Auch bei unbekanntem Benutzer wird ein Hash-Vergleich durchgeführt. Dann weiß Angreifer nicht,  ob Benutzer existiert oder nicht (sonst wäre die Reaktionszeit bei unbekanntem Benutzer deutlich kürzer, da kein Hash-Vergleich stattfindet)
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    if verify_password(form_data.password, user.hashed_password) is False:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/my-profile", response_model=UserResponse)
def get_profile(
    current_username: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Gibt das Profil des eingeloggten Benutzers zurück (geschützter Endpoint)."""
    # TODO: Implementiert diese Funktion
    # Hinweis: current_username kommt bereits validiert aus dem JWT (via Depends)
    user = db.query(User).filter(User.username == current_username).first()
    if user is None:
        raise HTTPException (status_code=404, detail="Benutzer nicht gefunden") # Sollte eigentlich nie passieren, da current_username nur gültige Benutzernamen enthält. Trotzdem gut, das abzufangen.
    return user


# ---------------------------------------------------------------------------
# TODO: Eure eigenen Endpoints hier einfügen
# ---------------------------------------------------------------------------

from sqlalchemy import or_

@app.get("/recipes", response_model=List[schemas.RecipeResponse])
def get_recipes(search: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Recipe)
    if search:
        # Suche im Titel (case-insensitive)
        query = query.filter(models.Recipe.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@app.post("/recipes", response_model=schemas.RecipeResponse)
def create_recipe(
    recipe: schemas.RecipeCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_recipe = models.Recipe(**recipe.model_dump(), user_id=current_user.id)
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Beispiel:
# @app.get("/items")
# def get_items(db: Session = Depends(get_db)):
#     return db.query(Item).all()
#
# @app.post("/items", status_code=201)
# def create_item(data: ItemCreate, db: Session = Depends(get_db)):
#     item = Item(**data.model_dump())
#     db.add(item)
#     db.commit()
#     db.refresh(item)
#     return item
