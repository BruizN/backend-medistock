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
    """
    ENDPOINT DE CHECKOUT: El usuario desde el Frontend hace click en "Pagar".
    Recibe la orden de compra, y usa el OrderService para registrarla en la base
    de datos y pedirle a Transbank el Token de inicio de pago.
    """
    # Determinamos dinámicamente nuestra URL basándonos en si estamos en localhost o Render
    # Esta es la URL secreta donde Transbank nos debe "devolver" al usuario después de pagar.
    return_url = f"{settings.BACKEND_URL}{settings.API_V1_STR}/orders/callback"
    return await service.create_checkout(current_user, order_in, return_url)

@router.api_route("/callback", methods=["GET", "POST"], include_in_schema=False)
async def webpay_callback(
    request: Request,
    service: OrderService = Depends(get_order_service)
):
    """
    ENDPOINT DE CALLBACK (EL MÁS CRÍTICO): 
    Aquí es donde Transbank (Webpay) aterriza una vez que el usuario ingresó su tarjeta.
    Soporta GET y POST porque a veces los navegadores o los proxys (como Render) 
    convierten la redirección de POST a GET por motivos de seguridad HTTP (Redirección 301).
    """
    # Extraemos el token del cuerpo de la petición (POST) o de la URL (GET)
    if request.method == "POST":
        form_data = await request.form()
        token_ws = form_data.get("token_ws") # Viene si el pago terminó (sea éxito o rechazo)
        TBK_TOKEN = form_data.get("TBK_TOKEN") # Viene si el usuario apretó "Anular"
    else:
        token_ws = request.query_params.get("token_ws")
        TBK_TOKEN = request.query_params.get("TBK_TOKEN")
        
    token = token_ws or TBK_TOKEN
    frontend_url = f"{settings.FRONTEND_URL}/payment/callback"
    
    if TBK_TOKEN:
        # El usuario se arrepintió y apretó "Anular compra y volver al comercio" en Webpay
        return RedirectResponse(f"{frontend_url}?status=cancelled&token={token}", status_code=303)
    
    if token_ws:
        try:
            # Validamos el estado real del pago consultando el token en los servidores de Transbank
            await service.confirm_payment(token_ws)
            # Si no explota, es porque el pago fue Autorizado. Redirigimos al Frontend con éxito.
            return RedirectResponse(f"{frontend_url}?status=authorized&token={token_ws}", status_code=303)
        except Exception:
            # Si explota (Exception), es porque Transbank dijo que la tarjeta fue rechazada o no tiene fondos.
            # Capturamos el error silenciosamente y redirigimos al Frontend con estado "rechazado".
            return RedirectResponse(f"{frontend_url}?status=rejected&token={token_ws}", status_code=303)
        
    # Caso borde: Llegó al endpoint sin ningún token válido
    return RedirectResponse(f"{frontend_url}?status=error", status_code=303)

@router.post("/confirm")
async def confirm_payment(
    token_ws: str,
    service: OrderService = Depends(get_order_service)
):
    return await service.confirm_payment(token_ws)
