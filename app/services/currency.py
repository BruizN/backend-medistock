import httpx
import logging

logger = logging.getLogger(__name__)

class CurrencyService:
    @staticmethod
    async def get_usd_to_clp() -> float:
        """
        Obtiene el tipo de cambio actual desde una API externa (open.er-api.com).
        
        PREGUNTA DEL PROFESOR: "¿Qué pasa si esta API externa se cae?"
        Respuesta en código: Usamos un bloque try-except. Si ocurre cualquier error 
        de red (httpx.RequestError) o excepción, lo capturamos en el 'except Exception as e' 
        y en lugar de que el servidor "crashee", devolvemos un valor por defecto (Fallback de 950.0). 
        Esto asegura que el sistema siga funcionando de forma resiliente.
        """
        try:
            # Usamos httpx.AsyncClient() en lugar del clásico 'requests' porque FastAPI es asíncrono.
            # Esto evita que nuestro servidor se bloquee esperando la respuesta.
            async with httpx.AsyncClient() as client:
                response = await client.get("https://open.er-api.com/v6/latest/USD")
                
                # Validamos que el código HTTP sea 200 (OK) antes de procesar el JSON
                if response.status_code == 200:
                    data = response.json()
                    # Extraemos la tasa de cambio a CLP (Peso Chileno). Si no existe en el JSON, usamos 950.0 por defecto.
                    clp_rate = data.get("rates", {}).get("CLP", 950.0)
                    return float(clp_rate)
                
                # Si la API responde con un error 500 o 404, usamos nuestro valor de respaldo
                return 950.0  
        except Exception as e:
            # Capturamos el error para que quede registrado en los logs del sistema, 
            # pero el usuario final no ve una pantalla de error, solo ve el valor 950.0.
            logger.error(f"Error técnico conectando a la API de monedas: {e}")
            return 950.0
