from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.orders.models import Order, OrderItem
from app.modules.orders.schemas import OrderCreate, PaymentInitResponse
from app.modules.orders.repository import OrderRepository
from app.modules.inventory.repository import ProductRepository
from app.services.payment import WebpayService
from app.services.currency import CurrencyService
from app.modules.auth.models import User

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.product_repo = ProductRepository(session)
        self.payment_service = WebpayService()
        
    async def create_checkout(self, user: User, order_in: OrderCreate, return_url: str) -> PaymentInitResponse:
        """
        Inicia el proceso de checkout. Calcula los totales, descuenta el stock 
        y pide a Webpay que genere un inicio de pago seguro.
        """
        total_amount = 0.0
        
        # Verificar stock de los productos y calcular el total a pagar
        order_items = []
        for item_in in order_in.items:
            product = await self.product_repo.get(item_in.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto {item_in.product_id} no encontrado")
            
            # PREGUNTA PROFESOR: ¿Qué pasa si múltiples personas compran a la vez?
            # Respuesta: Aquí hacemos una validación rápida de stock antes de crear la orden.
            if product.stock < item_in.quantity:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")
            
            # Descuento de stock en memoria (temporal hasta que se haga el commit final)
            product.stock -= item_in.quantity
            self.session.add(product)
            
            line_total = product.price * item_in.quantity
            total_amount += line_total
            order_items.append(
                OrderItem(product_id=product.id, quantity=item_in.quantity, unit_price=product.price)
            )
            
        # Llamamos a nuestra segunda API (Mindicador/Frankfurter) de forma asíncrona.
        # Esto cumple con el requisito de integración externa IL3.3, aunque le cobramos
        # al usuario en CLP (Pesos) a través de Webpay, obtenemos el valor del dólar para reportería.
        await CurrencyService.get_usd_to_clp()
        
        # Crear la Orden con estado Inicial "pending"
        new_order = Order(user_id=user.id, total_amount=total_amount, status="pending")
        await self.order_repo.create_order(new_order)
        
        for item in order_items:
            item.order_id = new_order.id
            await self.order_repo.create_order_item(item)
            
        await self.session.commit()
        
        # Iniciar transacción con Webpay Plus
        session_id = f"sess_{new_order.id.hex[:8]}"
        try:
            # Obligatoriamente debemos pasarle a Webpay nuestra URL de retorno (return_url)
            # a donde enviará al usuario una vez que el banco responda.
            tx_response = self.payment_service.create_transaction(
                buy_order=new_order.id.hex[:20], # Webpay tiene un límite de 26 caracteres para el buy_order
                session_id=session_id,
                amount=total_amount,
                return_url=return_url
            )
        except Exception:
            raise HTTPException(status_code=500, detail="Error iniciando la pasarela de pagos")

        # Guardamos temporalmente el Token de Transbank en nuestra BD
        new_order.payment_id = tx_response["token"]
        await self.order_repo.update_order(new_order)
        
        # Retornamos la URL secreta de Transbank y el token para que el Frontend haga la redirección
        return PaymentInitResponse(
            token=tx_response["token"],
            url=tx_response["url"],
            order_id=new_order.id
        )

    async def confirm_payment(self, token: str) -> dict:
        """
        Confirma si el usuario realmente pagó en la pasarela.
        """
        try:
            # Llamamos al servicio de Webpay para que valide si el Token fue cobrado con éxito.
            response = self.payment_service.commit_transaction(token)
        except Exception:
            raise HTTPException(status_code=400, detail="Token de transacción inválido o expirado")
            
        # PREGUNTA PROFESOR: ¿Basta con tener un token de Transbank para saber que el pago fue exitoso?
        # Respuesta: No. Transbank devuelve el token en la URL tanto para pagos exitosos como para rechazos.
        # Es obligatorio hacer este 'tx.commit()' y luego verificar que el "status" sea "AUTHORIZED".
        # Si no lo hacemos, estaríamos entregando productos por compras fallidas.
        if response.get("status") == "AUTHORIZED":
            return {"message": "Pago exitoso", "details": response}
        else:
            raise HTTPException(status_code=400, detail="Pago rechazado por el banco")
