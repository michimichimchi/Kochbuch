from typing import Annotated, List
import time

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

import models
import schemas
from auth import (
    DUMMY_HASH,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import Base, engine, get_db
from models import User, Recipe, Category, Grocery, RecipeGrocery
from schemas import Token, UserRegister, UserResponse


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


wait_for_db()
Base.metadata.create_all(bind=engine)


def seed_database():
    db = next(get_db())

    if db.query(Recipe).count() > 0:
        return

    categories = ["Vorspeise", "Hauptgericht", "Dessert"]
    for cat in categories:
        if db.query(Category).filter_by(name=cat).first() is None:
            db.add(Category(name=cat))
    db.commit()

    starter = db.query(Category).filter_by(name="Vorspeise").first().id
    main_dish = db.query(Category).filter_by(name="Hauptgericht").first().id
    dessert = db.query(Category).filter_by(name="Dessert").first().id

    recipes = [
        Recipe(
            title="Tomatensuppe",
            category_id=starter,
            time=10,
            difficulty=1,
            image="https://images.unsplash.com/photo-1547592166-23ac45744acd?q=80&w=1471&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            paragraph="Klassische Tomatensuppe mit frischen Kräutern.",
        ),
        Recipe(
            title="Gurkensalat",
            category_id=starter,
            time=20,
            difficulty=2,
            image="https://plus.unsplash.com/premium_photo-1701870910794-f2ed7f50a088?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            paragraph="Frischer Gurkensalat.",
        ),
        Recipe(
            title="Spaghetti Bolognese",
            category_id=main_dish,
            time=45,
            difficulty=2,
            image="https://images.unsplash.com/photo-1622973536968-3ead9e780960?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            paragraph="Italienische Pasta mit Hackfleisch-Tomatensoße.",
        ),
        Recipe(
            title="Pizza Salami",
            category_id=main_dish,
            time=30,
            difficulty=1,
            image="https://images.unsplash.com/photo-1564128442383-9201fcc740eb?q=80&w=1531&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            paragraph="Leckere Pizza mit Salami und Mozzarella.",
        ),
        Recipe(
            title="Erdbeerquark",
            category_id=dessert,
            time=60,
            difficulty=3,
            image="https://images.unsplash.com/photo-1729542920554-411daacea77b?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            paragraph="Cremiger Erdbeerquark mit frischen Erdbeeren.",
        ),
    ]

    db.add_all(recipes)
    db.commit()

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

    r_tomatensuppe = db.query(Recipe).filter_by(title="Tomatensuppe").first().id
    r_gurkensalat = db.query(Recipe).filter_by(title="Gurkensalat").first().id
    r_spaghetti_bolognese = db.query(Recipe).filter_by(title="Spaghetti Bolognese").first().id
    r_pizza_salami = db.query(Recipe).filter_by(title="Pizza Salami").first().id
    r_erdbeerquark = db.query(Recipe).filter_by(title="Erdbeerquark").first().id

    g_tomaten = db.query(Grocery).filter_by(name="Tomaten").first().id
    g_zwiebeln = db.query(Grocery).filter_by(name="Zwiebeln").first().id
    g_knoblauch = db.query(Grocery).filter_by(name="Knoblauch").first().id
    g_olivenoel = db.query(Grocery).filter_by(name="Olivenöl").first().id
    g_basilikum = db.query(Grocery).filter_by(name="Basilikum").first().id
    g_gurke = db.query(Grocery).filter_by(name="Gurke").first().id
    g_essig = db.query(Grocery).filter_by(name="Essig").first().id
    g_pasta = db.query(Grocery).filter_by(name="Pasta").first().id
    g_hackfleisch = db.query(Grocery).filter_by(name="Hackfleisch").first().id
    g_teig = db.query(Grocery).filter_by(name="Pizzateig").first().id
    g_mozzarella = db.query(Grocery).filter_by(name="Mozzarella").first().id
    g_salami = db.query(Grocery).filter_by(name="Salami").first().id
    g_tomsosse = db.query(Grocery).filter_by(name="Tomatensoße").first().id
    g_quark = db.query(Grocery).filter_by(name="Quark").first().id
    g_erdbeeren = db.query(Grocery).filter_by(name="Erdbeeren").first().id

    recipe_groceries = [
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_tomaten, amount=10, unit="Stück"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_zwiebeln, amount=2, unit="Stück"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_knoblauch, amount=2, unit="Zehe"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_olivenoel, amount=2, unit="EL"),
        RecipeGrocery(recipe_id=r_tomatensuppe, grocery_id=g_basilikum, amount=2, unit="TL"),
        RecipeGrocery(recipe_id=r_gurkensalat, grocery_id=g_gurke, amount=2, unit="Stück"),
        RecipeGrocery(recipe_id=r_gurkensalat, grocery_id=g_essig, amount=4, unit="EL"),
        RecipeGrocery(recipe_id=r_gurkensalat, grocery_id=g_olivenoel, amount=2, unit="EL"),
        RecipeGrocery(recipe_id=r_spaghetti_bolognese, grocery_id=g_pasta, amount=500, unit="g"),
        RecipeGrocery(recipe_id=r_spaghetti_bolognese, grocery_id=g_hackfleisch, amount=200, unit="g"),
        RecipeGrocery(recipe_id=r_spaghetti_bolognese, grocery_id=g_tomaten, amount=10, unit="Stück"),
        RecipeGrocery(recipe_id=r_pizza_salami, grocery_id=g_teig, amount=1, unit="Blech"),
        RecipeGrocery(recipe_id=r_pizza_salami, grocery_id=g_mozzarella, amount=400, unit="g"),
        RecipeGrocery(recipe_id=r_pizza_salami, grocery_id=g_salami, amount=10, unit="Scheiben"),
        RecipeGrocery(recipe_id=r_pizza_salami, grocery_id=g_tomsosse, amount=200, unit="ml"),
        RecipeGrocery(recipe_id=r_erdbeerquark, grocery_id=g_quark, amount=1, unit="kg"),
        RecipeGrocery(recipe_id=r_erdbeerquark, grocery_id=g_erdbeeren, amount=250, unit="g"),
    ]

    db.add_all(recipe_groceries)
    db.commit()


seed_database()

app = FastAPI(title="Mein Projekt", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first() is not None:
        raise HTTPException(status_code=400, detail="Username bereits vergeben")

    if db.query(User).filter(User.email == data.email).first() is not None:
        raise HTTPException(status_code=400, detail="Email bereits vergeben")

    hashed_password = get_password_hash(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.post("/token", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if user is None:
        verify_password(form_data.password, DUMMY_HASH)
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
    user = db.query(User).filter(User.username == current_username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    return user


@app.get("/recipes/top", response_model=List[schemas.RecipeResponse])
def get_top_recipes(limit: int = 3, db: Session = Depends(get_db)):
    top_recipes = (
        db.query(models.Recipe)
        .outerjoin(models.Evaluation, models.Recipe.id == models.Evaluation.recipe_id)
        .group_by(models.Recipe.id)
        .order_by(func.coalesce(func.avg(models.Evaluation.rating), 0).desc())
        .limit(limit)
        .all()
    )

    return top_recipes


@app.get("/recipes", response_model=List[schemas.RecipeResponse])
def get_recipes(
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.Recipe).filter(models.Recipe.is_public == True)

    if search:
        query = query.filter(models.Recipe.title.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()


@app.get("/recipes/me", response_model=List[schemas.RecipeResponse])
def get_my_recipes(
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == current_username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    return (
        db.query(models.Recipe)
        .join(models.RecipeUser)
        .filter(
            models.RecipeUser.user_id == user.id,
            models.RecipeUser.usage == "creator",
        )
        .all()
    )


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    groceries = (
        db.query(models.RecipeGrocery)
        .filter(models.RecipeGrocery.recipe_id == recipe_id)
        .all()
    )

    ingredients_list = []

    for g in groceries:
        grocery_item = db.query(models.Grocery).filter(models.Grocery.id == g.grocery_id).first()

        if grocery_item:
            ingredients_list.append(
                {
                    "name": grocery_item.name,
                    "amount": g.amount,
                    "unit": g.unit,
                }
            )

    return {
        "id": recipe.id,
        "title": recipe.title,
        "category_id": recipe.category_id,
        "time": recipe.time,
        "difficulty": recipe.difficulty,
        "paragraph": recipe.paragraph,
        "image": recipe.image,
        "ingredients": ingredients_list,
    }


@app.post("/recipes", response_model=schemas.RecipeResponse)
def create_recipe(
    recipe: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user),
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
        usage="creator",
    )

    db.add(recipe_user)

    for ingredient in recipe.ingredients:
        grocery = db.query(models.Grocery).filter(models.Grocery.name == ingredient.name).first()

        if grocery is None:
            grocery = models.Grocery(name=ingredient.name)
            db.add(grocery)
            db.commit()
            db.refresh(grocery)

        recipe_grocery = models.RecipeGrocery(
            recipe_id=new_recipe.id,
            grocery_id=grocery.id,
            amount=ingredient.amount,
            unit=ingredient.unit,
        )

        db.add(recipe_grocery)

    db.commit()
    db.refresh(new_recipe)

    return new_recipe


@app.get("/recipes/{recipe_id}/evaluations")
def get_recipe_evaluations(recipe_id: int, db: Session = Depends(get_db)):
    evaluations = (
        db.query(models.Evaluation, models.User)
        .join(models.User, models.Evaluation.user_id == models.User.id)
        .filter(models.Evaluation.recipe_id == recipe_id)
        .all()
    )

    return [
        {
            "id": evaluation.id,
            "rating": evaluation.rating,
            "comment": evaluation.comment,
            "username": user.username,
        }
        for evaluation, user in evaluations
    ]


@app.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.username == current_username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Rezept nicht gefunden")

    ownership = (
        db.query(models.RecipeUser)
        .filter(
            models.RecipeUser.recipe_id == recipe_id,
            models.RecipeUser.user_id == user.id,
            models.RecipeUser.usage == "creator",
        )
        .first()
    )

    if ownership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Du bist nicht berechtigt, dieses Rezept zu löschen",
        )

    try:
        db.query(models.RecipeGrocery).filter(
            models.RecipeGrocery.recipe_id == recipe_id
        ).delete()

        db.query(models.RecipeUser).filter(
            models.RecipeUser.recipe_id == recipe_id
        ).delete()

        db.query(models.Evaluation).filter(
            models.Evaluation.recipe_id == recipe_id
        ).delete()

        db.delete(recipe)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Fehler beim Löschen des Rezepts")

    return None


@app.get("/evaluations", response_model=List[schemas.EvaluationResponse])
def get_all_evaluations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return db.query(models.Evaluation).offset(skip).limit(limit).all()


@app.post("/evaluations", response_model=schemas.EvaluationResponse)
def create_evaluation(
    evaluation: schemas.EvaluationCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.username == current_username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")

    new_evaluation = models.Evaluation(
        **evaluation.model_dump(),
        user_id=user.id,
    )

    db.add(new_evaluation)
    db.commit()
    db.refresh(new_evaluation)

    return new_evaluation