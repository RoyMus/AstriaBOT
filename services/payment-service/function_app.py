import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import azure.functions as func
from app.payment_handler import PaymentHandler
from shared.event_broker import get_event_broker

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
event_broker = get_event_broker()
payment_handler = PaymentHandler(event_broker)

@app.route(route="payment-received")
async def receive_payment(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook to receive payment notifications
    Processes payment and publishes PaymentReceivedEvent
    """
    try:
        logging.info('Received payment webhook')
        await payment_handler.process_payment(req)
        return func.HttpResponse("Payment processed successfully", status_code=200)
    except Exception as e:
        logging.error(f"Failed to process payment: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
