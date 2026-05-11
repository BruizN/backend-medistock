from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import get_db_session, get_current_user
from app.modules.auth.models import User
from app.modules.orders.schemas import OrderCreate, PaymentInitResponse
from app.modules.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

def get_order_service(session: AsyncSession = Depends(get_db_session)) -> OrderService:
    return OrderService(session)

@router.post("/checkout", response_model=PaymentInitResponse)
async def checkout(
    order_in: OrderCreate,
    request: Request,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    # Determine origin or use a specific frontend URL
    # Assuming frontend will be running on another port
    return_url = "http://localhost:5173/payment/callback"
    return await service.create_checkout(current_user, order_in, return_url)

@router.post("/confirm")
async def confirm_payment(
    token_ws: str,
    service: OrderService = Depends(get_order_service)
):
    return await service.confirm_payment(token_ws)
