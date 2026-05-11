from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import get_db_session, get_current_user
from app.core.config import settings
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
    return_url = f"{settings.BACKEND_URL}{settings.API_V1_STR}/orders/callback"
    return await service.create_checkout(current_user, order_in, return_url)

@router.api_route("/callback", methods=["GET", "POST"], include_in_schema=False)
async def webpay_callback(request: Request):
    """
    Recibe el POST o GET de Transbank.
    """
    if request.method == "POST":
        form_data = await request.form()
        token_ws = form_data.get("token_ws")
        TBK_TOKEN = form_data.get("TBK_TOKEN")
    else:
        token_ws = request.query_params.get("token_ws")
        TBK_TOKEN = request.query_params.get("TBK_TOKEN")
        
    token = token_ws or TBK_TOKEN
    frontend_url = f"{settings.FRONTEND_URL}/payment/callback"
    
    if TBK_TOKEN:
        # Pago anulado por usuario
        return RedirectResponse(f"{frontend_url}?status=cancelled&token={token}", status_code=303)
    
    if token_ws:
        return RedirectResponse(f"{frontend_url}?status=authorized&token={token_ws}", status_code=303)
        
    return RedirectResponse(f"{frontend_url}?status=error", status_code=303)

@router.post("/confirm")
async def confirm_payment(
    token_ws: str,
    service: OrderService = Depends(get_order_service)
):
    return await service.confirm_payment(token_ws)
