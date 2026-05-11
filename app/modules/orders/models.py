import uuid
from sqlmodel import Field
from app.core.auditmixin import AuditMixin

class Order(AuditMixin, table=True):
    __tablename__ = "orders"
    user_id: uuid.UUID = Field(index=True)
    status: str = Field(default="pending", max_length=50)
    payment_id: str | None = Field(default=None, max_length=255)
    total_amount: float = Field(default=0.0)

class OrderItem(AuditMixin, table=True):
    __tablename__ = "order_items"
    order_id: uuid.UUID = Field(index=True)
    product_id: uuid.UUID = Field(index=True)
    quantity: int = Field(default=1)
    unit_price: float = Field(default=0.0)
