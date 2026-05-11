from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import get_db_session, get_current_user
from app.modules.auth.models import User
from app.modules.orders.schemas import OrderCreate, PaymentInitResponse
from app.modules.orders.service import OrderService
from app.services.currency import CurrencyService

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/exchange-rate")
async def get_exchange_rate():
    rate = await CurrencyService.get_usd_to_clp()
    return {"currency": "USD", "clp_rate": rate}

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
    # Return URL is now handled by the backend directly inside the service
    return_url = "http://localhost:8000/api/v1/orders/callback"
    return await service.create_checkout(current_user, order_in, return_url)

@router.post("/callback", include_in_schema=False)
async def webpay_callback(
    request: Request,
    token_ws: str = Form(default=None),
    TBK_TOKEN: str = Form(default=None),
    TBK_ORDEN_COMPRA: str = Form(default=None),
    TBK_ID_SESION: str = Form(default=None)
):
    """
    Recibe el POST de Transbank.
    Si viene token_ws, el pago puede ser confirmado.
    Si viene TBK_TOKEN, el pago fue anulado por el usuario.
    """
    token = token_ws or TBK_TOKEN
    frontend_url = "http://localhost:5173/payment/callback"
    
    if TBK_TOKEN:
        # Pago anulado por usuario
        return RedirectResponse(f"{frontend_url}?status=cancelled&token={token}", status_code=303)
    
    if token_ws:
        # Aquí normalmente confirmaríamos el pago con service.confirm_payment(token_ws)
        # Pero para mantener el flujo simple y delegar el estado al frontend:
        return RedirectResponse(f"{frontend_url}?status=authorized&token={token_ws}", status_code=303)
        
    return RedirectResponse(f"{frontend_url}?status=error", status_code=303)

@router.post("/confirm")
async def confirm_payment(
    token_ws: str,
    service: OrderService = Depends(get_order_service)
):
    return await service.confirm_payment(token_ws)
