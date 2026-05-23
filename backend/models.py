from sqlalchemy import Column, Integer, String, CheckConstraint, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)

class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)

    title = Column(String(100), unique=True, nullable=False, index=True)
    time = Column(Integer)
    paragraph = Column(String(5000))
    image = Column(String(200))
    difficulty = Column(Integer, CheckConstraint("difficulty >= 1 AND difficulty <= 5"))

class RecipeGrocery(Base):
    __tablename__ = "recipe_grocery"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)
    grocery_id = Column(Integer, ForeignKey("grocery.id"), nullable=False)

    amount = Column(Integer)
    unit = Column(String(50))

class RecipeTool(Base):
    __tablename__ = "recipe_tool"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tool.id"), nullable=False)

class RecipeUser(Base):
    __tablename__ = "recipe_user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipe.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    usage = Column(String(100))

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

class Grocery(Base):
    __tablename__ = "grocery"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    image = Column(String(200))

    durability_score = Column(Integer, CheckConstraint("durability_score >= 1 AND durability_score <= 5"))
    durability = Column(String(200))

    availability_score = Column(Integer, CheckConstraint("availability_score >= 1 AND availability_score <= 5"))
    availability = Column(String(200))

class Tool(Base):
    __tablename__ = "tool"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True)
    description = Column(String(200))