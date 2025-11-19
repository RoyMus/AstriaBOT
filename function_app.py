import json
from Utils import WhatsappClient
import azure.functions as func
import logging
from app.message_processor import process_message   
from app.image_processors import handle_images_from_astria
from app.payment_processors import process_payment
from app.astria_images_video_processors import update_pack_images
from db.db_maintenance import delete_outdated_records

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="handle_db_maintenance")
@app.schedule(
    schedule="0 0 4 * * 3",
    arg_name="mytimer",
    run_on_startup=False
)
async def handle_db_maintenance(mytimer: func.TimerRequest) -> None:
    logging.info('started performing maintenance')
    await delete_outdated_records()
    logging.info('finished performing maintenance')

@app.route(route="pack-tune-received")
async def receive_pack_images(req: func.HttpRequest) -> func.HttpResponse:
    """
        Webhook to receive images from Astria after prompt generation
    """
    return await handle_images_from_astria(req)

@app.route(route="payment-received")
async def recieve_payment(req: func.HttpRequest) -> func.HttpResponse:
    """
        Webhook to receive images from Astria after prompt generation
    """
    return await process_payment(req)


@app.route(route="update-images")
async def update_images(req: func.HttpRequest) -> func.HttpResponse:
    """
        Webhook to update images in azure storage from Astria
    """
    logging.info('Updating images in Azure Storage')
    await update_pack_images()
    return func.HttpResponse(
        "Images updated successfully",
        status_code=200
    )

VERIFY_TOKEN = "takar_mak"  # Set your own verify token
@app.route(route="SmsReceived",methods=["GET", "POST"])
async def receive_sms(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook to receive SMS/MMS from Meta
    """
    logging.info('Got Message From Whatsapp')   
    if req.method == "GET":
        # Handle webhook verification
        hub_verify_token = req.params.get("hub.verify_token")
        hub_challenge = req.params.get("hub.challenge")
        if hub_verify_token == VERIFY_TOKEN:
            return func.HttpResponse(hub_challenge, status_code=200)
        return func.HttpResponse("Verification failed", status_code=403)

    elif req.method == "POST":
        logging.info(f"Received Whatsapp webhook message")
        data = req.get_json()
        messages = WhatsappClient.process_incoming_messages(data)
        if len(messages) == 0:
            return func.HttpResponse(status_code=200)
        await process_message(messages)
    # Respond back
    return func.HttpResponse(
            status_code=200
        )