import json
import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import azure.functions as func
from app.image_handler import ImageHandler
from shared.event_broker import get_event_broker

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
event_broker = get_event_broker()
image_handler = ImageHandler(event_broker)

@app.route(route="pack-tune-received")
async def receive_pack_images(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook to receive images from Astria after tune/prompt generation
    Processes and stores images, publishes ImageProcessedEvent
    """
    try:
        logging.info('Received pack/tune images from Astria')
        await image_handler.handle_astria_images(req)
        return func.HttpResponse("Images processed successfully", status_code=200)
    except Exception as e:
        logging.error(f"Failed to process Astria images: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


@app.route(route="update-images")
async def update_images(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook to update pack preview images in Azure Storage from Astria
    Publishes PackImagesUpdatedEvent
    """
    try:
        logging.info('Updating pack images in Azure Storage')
        await image_handler.update_pack_images()
        
        return func.HttpResponse("Images updated successfully", status_code=200)
    except Exception as e:
        logging.error(f"Failed to update images: {e}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
