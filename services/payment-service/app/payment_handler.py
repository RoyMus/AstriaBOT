import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.payment_processors import process_payment


class PaymentHandler:
    """Handles payment processing operations"""
    
    def __init__(self, event_broker):
        self.event_broker = event_broker
    
    async def process_payment(self, req) -> None:
        """Process payment from webhook"""
        logging.info("Processing payment")
        
        # Use existing payment processor
        response = await process_payment(req)
        
        # Publish PaymentReceivedEvent for other services
        # (e.g., message service can notify user about successful payment)
        # event = PaymentReceivedEvent(
        #     data={...}
        # )
        # await self.event_broker.publish(event)
        
        return response
