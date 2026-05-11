import uuid
from typing import List
from pydantic import BaseModel

class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    product_id: uuid.UUID
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}

class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: float
    items: List[OrderItemResponse] = []

    model_config = {"from_attributes": True}

class PaymentInitResponse(BaseModel):
    token: str
    url: str
    order_id: uuid.UUID
