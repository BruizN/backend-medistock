import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.types import CleanCode, CleanText


class ProductBase(BaseModel):
    code: CleanCode
    name: CleanText
    description: Optional[CleanText] = None
    price: float = Field(default=0.0, ge=0)
    stock: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[CleanText] = None
    description: Optional[CleanText] = None
    price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
