from typing import Annotated, List

import time
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models import User, Recipe, Category, Grocery, RecipeGrocery
from sqlalchemy import func, text

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

# es wird 10 mal versucht sich mit der db zu verbinen, mit Pause von 3 Sekunden dazwischen.
# Wenn Verbindung erfolgreich ist, wird Funktion mit Rückgabewert None verlassen. 
# Wenn nach 10 Versuchen keine Verbindung zustande kommt, wird eine RuntimeError mit entsprechender 
# Fehlermeldung ausgelöst.
def wait_for_db(retries=10, delay=3):
    for i in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Datenbankverbindung erfolgreich!")
            return
        except OperationalError:
            print(f"Datenbankverbindung fehlgeschlagen. Neuer Versuch in {delay} Sekunden...")
            time.sleep(delay)
    raise RuntimeError("Datenbankverbindung konnte nach mehreren Versuchen nicht hergestellt werden.")

# Funktion wird aufgerufen, um sicherzustellen, dass die Anwendung erst startet, 
# wenn die Datenbank erreichbar ist. Wichtig, da frontend gestartet wurde,
# ohne dass db-server bereit war und dieser dann nicht mehr gestartet werden konnte
wait_for_db()
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
        Recipe(title="Gurkensalat", category_id=starter, time=20, difficulty=2,
               paragraph="Frischer Gurkensalat."),
        Recipe(title="Spaghetti Bolognese", category_id=main_dish, time=45, difficulty=2,
               paragraph="Italienische Pasta mit Hackfleisch-Tomatensoße."),
        Recipe(title="Pizza Salami", category_id=main_dish, time=30, difficulty=1,
               paragraph="Leckere Pizza mit Salami und Mozzarella."),
        Recipe(title="Erdbeerquark", category_id=dessert, time=60, difficulty=3,
               paragraph="Cremiger Erdbeerquark mit frischen Erdbeeren."),
    ]
    # add_all() Rezepte werden im Arbeitsspeicher vorgemerkt
    # commit() speichert sie dann tatsächlich in der DB (INSERT-Befehl wird ausgeführt)
    db.add_all(recipes)
    db.commit()

    # Beispiel-Zutaten anlegen
    groceries = [
        Grocery(name="Tomaten"),
        Grocery(name="Zwiebeln"),
        Grocery(name="Knoblauch"),
        Grocery(name="Olivenöl"),
        Grocery(name="Basilikum"),
        Grocery(name="Gurke"),
        Grocery(name="Essig"),
        Grocery(name="Pasta"),
        Grocery(name="Hackfleisch"),
        Grocery(name="Pizzateig"),
        Grocery(name="Mozzarella"),
        Grocery(name="Salami"),
        Grocery(name="Tomatensoße"),
        Grocery(name="Quark"),
        Grocery(name="Erdbeeren"),
    ]
    db.add_all(groceries)
    db.commit()

     
    # IDs der Rezepte dynamisch holen
    # Für Zuordnung Rezept und Zutaten
    r_tomatensuppe = db.query(Recipe).filter_by(title="Tomatensuppe").first().id
    r_gurkensalat  = db.query(Recipe).filter_by(title="Gurkensalat").first().id
    r_spagetti_bolognese     = db.query(Recipe).filter_by(title="Spaghetti Bolognese").first().id
    r_pizza_salami        = db.query(Recipe).filter_by(title="Pizza Salami").first().id
    r_erdbeerquark       = db.query(Recipe).filter_by(title="Erdbeerquark").first().id

    # IDs der Zutaten dynamisch holen
    # Für Zuordnung Rezept und Zutaten
    g_tomaten    = db.query(Grocery).filter_by(name="Tomaten").first().id
    g_zwiebeln   = db.query(Grocery).filter_by(name="Zwiebeln").first().id
    g_knoblauch  = db.query(Grocery).filter_by(name="Knoblauch").first().id
    g_olivenoel  = db.query(Grocery).filter_by(name="Olivenöl").first().id
    g_basilikum  = db.query(Grocery).filter_by(name="Basilikum").first().id
    g_gurke      = db.query(Grocery).filter_by(name="Gurke").first().id
    g_essig      = db.query(Grocery).filter_by(name="Essig").first().id
    g_pasta      = db.query(Grocery).filter_by(name="Pasta").first().id
    g_hackfl     = db.query(Grocery).filter_by(name="Hackfleisch").first().id
    g_teig       = db.query(Grocery).filter_by(name="Pizzateig").first().id
    g_mozzarella = db.query(Grocery).filter_by(name="Mozzarella").first().id
    g_salami     = db.query(Grocery).filter_by(name="Salami").first().id
    g_tomsosse   = db.query(Grocery).filter_by(name="Tomatensoße").first().id
    g_quark      = db.query(Grocery).filter_by(name="Quark").first().id
    g_erdbeeren  = db.query(Grocery).filter_by(name="Erdbeeren").first().id

    # Zuordnungen der Rezepte und der Zutaten mit Mengenangaben und Einheiten anlegen
    recipe_groceries = [
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_tomaten,   amount=10, unit="Stück"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_zwiebeln,  amount=2,  unit="Stück"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_knoblauch, amount=2,  unit="Zehe"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_olivenoel, amount=2,  unit="EL"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_basilikum, amount=2,  unit="TL"),
        RecipeGrocery(recipe_id=r_gurkensalat,    grocery_id=g_gurke,     amount=2,  unit="Stück"),
        RecipeGrocery(recipe_id=r_gurkensalat,    grocery_id=g_essig,     amount=4,  unit="EL"),
        RecipeGrocery(recipe_id=r_gurkensalat,    grocery_id=g_olivenoel, amount=2,  unit="EL"),
        RecipeGrocery(recipe_id=r_spagetti_bolognese, grocery_id=g_pasta,     amount=500, unit="g"),
        RecipeGrocery(recipe_id=r_spagetti_bolognese, grocery_id=g_hackfl,    amount=200, unit="g"),
        RecipeGrocery(recipe_id=r_spagetti_bolognese, grocery_id=g_tomaten,   amount=10, unit="Stück"),
        RecipeGrocery(recipe_id=r_pizza_salami,    grocery_id=g_teig,      amount=1,  unit="Blech"),
        RecipeGrocery(recipe_id=r_pizza_salami,    grocery_id=g_mozzarella,amount=400, unit="g"),
        RecipeGrocery(recipe_id=r_pizza_salami,    grocery_id=g_salami,    amount=10, unit="Scheiben"),
        RecipeGrocery(recipe_id=r_pizza_salami,    grocery_id=g_tomsosse,  amount=200, unit="ml"),
        RecipeGrocery(recipe_id=r_erdbeerquark,    grocery_id=g_quark,     amount=1,  unit="kg"),
        RecipeGrocery(recipe_id=r_erdbeerquark,    grocery_id=g_erdbeeren, amount=250, unit="g"),
    ]
    
    db.add_all(recipe_groceries)
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


@app.get("/recipes/top", response_model=List[schemas.RecipeResponse])
def get_top_recipes(limit: int = 3, db: Session = Depends(get_db)):
    """Holt die Rezepte mit der höchsten Durchschnittsbewertung."""
    
    top_recipes = (
        db.query(models.Recipe)
        # Verknüpft die Rezepte mit eurer neuen Evaluation-Tabelle
        .outerjoin(models.Evaluation, models.Recipe.id == models.Evaluation.recipe_id)
        # Gruppiert alles pro Rezept
        .group_by(models.Recipe.id)
        # Berechnet den Durchschnitt aus der Spalte 'rating' und sortiert absteigend
        .order_by(func.coalesce(func.avg(models.Evaluation.rating), 0).desc())
        .limit(limit)
        .all()
    )
    
    return top_recipes


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

@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    return recipe

@app.post("/recipes", response_model=schemas.RecipeResponse)
def create_recipe(
    recipe: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.username == current_username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    recipe_data = recipe.model_dump(exclude={"ingredients"})
    new_recipe = models.Recipe(**recipe_data)

    try:
        db.add(new_recipe)
        db.commit()
        db.refresh(new_recipe)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Rezepttitel existiert bereits")

    recipe_user = models.RecipeUser(
        recipe_id=new_recipe.id,
        user_id=user.id,
        usage="creator"
    )

    db.add(recipe_user)

    for ingredient in recipe.ingredients:
        grocery = db.query(models.Grocery).filter(
            models.Grocery.name == ingredient.name
        ).first()

        if grocery is None:
            grocery = models.Grocery(name=ingredient.name)
            db.add(grocery)
            db.commit()
            db.refresh(grocery)

        recipe_grocery = models.RecipeGrocery(
            recipe_id=new_recipe.id,
            grocery_id=grocery.id,
            amount=ingredient.amount,
            unit=ingredient.unit
        )

        db.add(recipe_grocery)

    db.commit()
    db.refresh(new_recipe)

    return new_recipe


@app.get("/evaluations", response_model=List[schemas.EvaluationResponse])
def get_evaluations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Evaluation).offset(skip).limit(limit).all()


@app.post("/evaluations", response_model=schemas.EvaluationResponse)
def create_evaluation(
    evaluation: schemas.EvaluationCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.username == current_username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    new_evaluation = models.Evaluation(
        **evaluation.model_dump(),
        user_id=user.id
    )

    db.add(new_evaluation)
    db.commit()
    db.refresh(new_evaluation)

    return new_evaluation

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