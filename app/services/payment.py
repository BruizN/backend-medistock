from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
import logging

logger = logging.getLogger(__name__)

class WebpayService:
    def __init__(self):
        # We use the integration/sandbox environment
        self.tx = Transaction()
        # By default, transbank-sdk uses Integration (Sandbox) credentials when initialized without args
    
    def create_transaction(self, buy_order: str, session_id: str, amount: float, return_url: str):
        try:
            response = self.tx.create(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url
            )
            return response
        except Exception as e:
            logger.error(f"Error creating Webpay transaction: {e}")
            raise

    def commit_transaction(self, token: str):
        try:
            response = self.tx.commit(token=token)
            return response
        except Exception as e:
            logger.error(f"Error committing Webpay transaction: {e}")
            raise
