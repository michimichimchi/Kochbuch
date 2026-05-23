from pydantic import BaseModel, Field


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


# Basis Schema
class RecipeBase(BaseModel):
    title: str = Field(..., max_length=255, description="Der Name des Rezepts")
    ingredients: str = Field(...)
    instructions: str = Field(...)

# Schema für POST-Request
class RecipeCreate(RecipeBase):
    pass

# Schema für API Response
class RecipeResponse(RecipeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True 

# TODO: Fügt hier eure eigenen Schemas hinzu
# class ItemCreate(BaseModel):
#     name: str
#     price: int
#
# class ItemResponse(BaseModel):
#     id: int
#     name: str
#     price: int
#     model_config = {"from_attributes": True}
