from typing import Optional
from sqlmodel import Field

from app.core.auditmixin import AuditMixin


class Product(AuditMixin, table=True):
    __tablename__ = "products"

    code: str = Field(index=True, unique=True, max_length=50)
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = None
    price: float = Field(default=0.0)
    stock: int = Field(default=0)
