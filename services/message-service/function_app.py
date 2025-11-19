import json
import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from Utils import WhatsappClient
import azure.functions as func
from app.message_handler import MessageHandler
from shared.event_broker import get_event_broker, Event

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
event_broker = get_event_broker()

@app.route(route="SmsReceived", methods=["GET", "POST"])
async def receive_sms(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook to receive SMS/MMS from Meta/WhatsApp
    Triggers message processing state machine
    """
    logging.info('Got Message From Whatsapp')
    VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "takar_mak")
    
    if req.method == "GET":
        # Handle webhook verification
        hub_verify_token = req.params.get("hub.verify_token")
        hub_challenge = req.params.get("hub.challenge")
        if hub_verify_token == VERIFY_TOKEN:
            return func.HttpResponse(hub_challenge, status_code=200)
        return func.HttpResponse("Verification failed", status_code=403)

    elif req.method == "POST":
        try:
            logging.info(f"Received Whatsapp webhook message")
            data = req.get_json()
            messages = WhatsappClient.process_incoming_messages(data)
            
            if len(messages) == 0:
                return func.HttpResponse(status_code=200)
            
            # Process messages through state machine
            handler = MessageHandler(event_broker)
            await handler.process_messages(messages)
            
            return func.HttpResponse(status_code=200)
        except Exception as e:
            logging.error(f"Error processing WhatsApp message: {e}")
            return func.HttpResponse("Internal error", status_code=500)
