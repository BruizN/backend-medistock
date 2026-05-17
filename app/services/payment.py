from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
import logging

logger = logging.getLogger(__name__)

class WebpayService:
    def __init__(self):
        """
        Usamos el SDK oficial de Transbank para Python (transbank-sdk).
        En lugar de usar credenciales reales, inicializamos el SDK con IntegrationType.TEST.
        Esto nos conecta al entorno "Sandbox" (de pruebas) usando los CommerceCodes públicos
        de Transbank, evitando exponer datos bancarios reales en el código.
        """
        self.options = WebpayOptions(
            IntegrationCommerceCodes.WEBPAY_PLUS, 
            IntegrationApiKeys.WEBPAY, 
            IntegrationType.TEST
        )
        self.tx = Transaction(self.options)
    
    def create_transaction(self, buy_order: str, session_id: str, amount: float, return_url: str):
        """
        Paso 1 del Flujo Webpay: "Crear Transacción".
        Le enviamos a Transbank el monto y el ID de la orden. Transbank nos responde
        con una URL segura y un Token único. Luego el Frontend usa esos datos
        para redirigir al usuario a la pantalla de pago del banco.
        """
        try:
            response = self.tx.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url
            )
            return response
        except Exception as e:
            logger.error(f"Error creando transacción Webpay: {e}")
            raise

    def commit_transaction(self, token: str):
        """
        Cuando el usuario vuelve de Webpay, Transbank nos entrega el Token. 
        Obligatoriamente debemos llamar a 'tx.commit(token)'. Esta función consulta a Transbank 
        "¿Este token fue aprobado o rechazado por el banco?". Si no hacemos este paso, 
        podríamos entregar productos gratis a tarjetas rechazadas.
        """
        try:
            response = self.tx.commit(token=token)
            return response
        except Exception as e:
            logger.error(f"Error confirmando transacción Webpay (token inválido o expirado): {e}")
            raise
