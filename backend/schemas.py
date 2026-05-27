from pydantic import BaseModel, Field
from typing import Optional, List

# --- Auth-Schemas ---

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class RecipeIngredientCreate(BaseModel):
    name: str = Field(..., max_length=100)
    amount: Optional[int] = None
    unit: Optional[str] = Field(None, max_length=50)


class RecipeBase(BaseModel):
    category_id: int
    title: str = Field(..., max_length=100)
    time: Optional[int] = None
    paragraph: Optional[str] = Field(None, max_length=5000)
    image: Optional[str] = Field(None, max_length=200)
    difficulty: Optional[int] = Field(None, ge=1, le=5)


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate] = []


class RecipeResponse(RecipeBase):
    id: int

    class Config:
        from_attributes = True


class RecipeGroceryBase(BaseModel):
    recipe_id: int
    grocery_id: int
    amount: Optional[int] = None
    unit: Optional[str] = Field(None, max_length=50)


class RecipeGroceryCreate(RecipeGroceryBase):
    pass


class RecipeGroceryResponse(RecipeGroceryBase):
    id: int

    class Config:
        from_attributes = True


class RecipeUserBase(BaseModel):
    recipe_id: int
    user_id: int
    usage: Optional[str] = Field(None, max_length=100)


class RecipeUserCreate(RecipeUserBase):
    pass


class RecipeUserResponse(RecipeUserBase):
    id: int

    class Config:
        from_attributes = True


class EvaluationBase(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class EvaluationCreate(EvaluationBase):
    recipe_id: int


class EvaluationResponse(EvaluationBase):
    id: int
    user_id: int
    recipe_id: int

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class GroceryBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    image: Optional[str] = Field(None, max_length=200)

class GroceryCreate(GroceryBase):
    pass


class GroceryResponse(GroceryBase):
    id: int

    class Config:
        from_attributes = True