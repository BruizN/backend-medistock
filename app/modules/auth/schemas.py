import uuid
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "client"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str
