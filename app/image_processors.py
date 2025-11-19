import asyncio
from collections import Counter
import json
import aiohttp
import logging
import azure.functions as func
import requests
from starlette.requests import FormData
from Utils import constants,WhatsappWrapper, dbClient, utils,states,aiohttp_retry
from db import dbConfig
from datetime import datetime, timezone,timedelta


async def get_tunes_for_user(from_number: str, session: aiohttp.ClientSession) -> list:
    user_tunes = []

    tunes = await aiohttp_retry.get_with_retry(f"{constants.ASTRIA_API_URL}/tunes",
                        session=session, headers=constants.ASTRIA_API_Authentication)
    if not tunes:
        return user_tunes
    for tune in tunes:
        if tune.get("title") == from_number:
            expiry_date = tune.get("expires_at")
            if not expiry_date:
                continue
            user_tunes.append(
                {
                    "id": tune.get("id"),
                    "title": tune.get("title"),
                    "name": tune.get("name"),
                    "created_at": datetime.fromisoformat(tune.get("created_at")).strftime("%Y-%m-%d %H:%M:%S"),
                    "expires_at": datetime.fromisoformat(expiry_date).strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
    return user_tunes    
async def get_characteristics(image_data, session) -> [tuple]:
    data = aiohttp.FormData()
    data.add_field("file", image_data, content_type="image/png")
    data.add_field("name", "person")
    characteristics = {}
    inspect_data = await aiohttp_retry.post_with_retry(f"{constants.ASTRIA_API_URL}/images/inspect",
                            session=session, headers=constants.ASTRIA_API_Authentication, data=data)
    if not inspect_data:
        return characteristics
    for key, value in inspect_data.items():
        if isinstance(value, str) and value:
            characteristics[key] = value
    return characteristics

async def aggregate_characteristics(images,session):
    aggregated = {}
    # Iterate over characteristics and collect string values
    for image in images:
        characteristics = await get_characteristics(image, session)
        for key, value in characteristics.items():
            if isinstance(value, str):
                aggregated.setdefault(key, []).append(value)

    common_values = {}

    for key, values in aggregated.items():
        # Only set value if high enough percentage exists
        if len(values) < len(images) / 2:
            continue
        # Find the most common value
        most_common_value = Counter(values).most_common(1)[0][0]
        common_values[key] = most_common_value

    return common_values
async def tune_model_using_pack(wa: WhatsappWrapper.WhatsappWrapper, from_number: str, user_images: list[str],
                                db: dbClient.AsyncDatabaseManager,
                                session: aiohttp.ClientSession, pack_id: int, tune_id: str,entity_type:str):
    # send to astria
    callback = f"{constants.WEBHOOK_URL}&phone_number={from_number}"
    logging.info(f"callback {callback}")
    if tune_id:
        data = [
            ("tune[tune_ids][]", tune_id),
            ("tune[prompt_attributes][callback]", callback),
        ]
    else:
        data = [
            ("tune[title]", f"{from_number}"),
            ("tune[name]", entity_type),
            ("tune[prompts_callback]", callback),
        ]
        images = []
        if user_images:
            for i, row in enumerate(user_images):
                try:
                    image_data = await wa.get_whatsapp_image(row["path"])
                    data.append(("tune[images][]", image_data))
                    images.append(image_data)
                except Exception as e:
                    #Ignoring expired or deleted images
                    logging.error(f"Error fetching image {row['path']}: {e}")
                    continue

        aggregated_characteristics = await aggregate_characteristics(images, session)
        for key, value in aggregated_characteristics.items():
            data.append((f"tune[characteristics][{key}]", value))
        result = await aiohttp_retry.post_with_retry(f"{constants.ASTRIA_API_URL}/p/{pack_id}/tunes",
                            session=session, headers=constants.ASTRIA_API_Authentication, data=data)
        if not result:
            await wa.send_error_message()
            return
        logging.info(f"Got result {result}") 
        if "id" in result:
            tuneID = result["id"]
            eta = result["eta"]
            logging.info(f"PICTURESLOADED with tune_id {tuneID}")
            await db.insert_data(f"UPDATE users SET tuneID = ($1), state = ($2) WHERE phone = ($3)",
                            (str(tuneID), states.States.TUNEREADY.value, from_number))
            await db.insert_data("DELETE FROM pictures WHERE phone_number = $1", (from_number,))
            timeLeft = datetime.fromisoformat(eta) - datetime.now(timezone.utc)
            await wa.send_processingimages_msg(timeLeft)
        else:
            timeLeft = timedelta(minutes=2)
            await wa.send_processingimages_msg(timeLeft)

async def handle_images_from_astria(req: func.HttpRequest):
    phoneNumber = req.params.get('phone_number')
    logging.info(f"Received pack images for {phoneNumber}")
    
    try:
        data = req.get_json()
    except ValueError as e:
        logging.error(f"Failed to parse JSON data: {e}")
        return func.HttpResponse("Invalid JSON data", status_code=400)

    if not phoneNumber:
        logging.error("Missing phone number parameter")
        return func.HttpResponse("Missing phone number", status_code=400)

    try:
        language = states.Languages.ENGLISH.value
        async with dbClient.AsyncDatabaseManager(dbConfig.db_config) as db:
            row = await db.execute_query_one(f"SELECT language FROM users WHERE phone = $1", (phoneNumber,))
            if row:
                language = row.get("language", None)
                
        async with WhatsappWrapper.WhatsappWrapper(phoneNumber, language) as wc:
            await wc.send_preimagesent_msg()
            
            # Add retry logic for image/video sending
            max_retries = 3
            retry_delay = 1  # seconds
            
            async def send_media_with_retry(url, is_video=False):
                for attempt in range(max_retries):
                    try:
                        response = requests.head(url, allow_redirects=True, timeout=10)
                        content_type = response.headers.get('Content-Type', '')
                        
                        if 'image' in content_type and not is_video:
                            await wc.send_image_to_client(phoneNumber, url)
                        elif 'video' in content_type and is_video:
                            await wc.send_video_to_client(phoneNumber, url)
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            logging.error(f"Failed to send media after {max_retries} attempts: {e}")
                            raise
                        await asyncio.sleep(retry_delay * (attempt + 1))

            if isinstance(data, list):
                for prompt in data:
                    images = prompt.get("images", [])
                    for image in images:
                        await send_media_with_retry(image)
            else:
                prompt = data.get("prompt")
                if prompt:
                    images = prompt.get("images", [])
                    for image in images:
                        await send_media_with_retry(image)

            await asyncio.sleep(1)
            await wc.send_postimagesent_msg()

    except Exception as e:
        logging.error(f"Error processing images: {str(e)}")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

    return func.HttpResponse("OK", status_code=200)


async def inspect_image(image_data, from_number, media_id, db : dbClient.AsyncDatabaseManager, session, wa: WhatsappWrapper.WhatsappWrapper,message_id:str):
    data = aiohttp.FormData()
    data.add_field("file", image_data, filename="person.png", 
                   content_type="image/png")
    data.add_field("name", "person")
    inspect_data = await aiohttp_retry.post_with_retry(f"{constants.ASTRIA_API_URL}/images/inspect",
                        session=session, headers=constants.ASTRIA_API_Authentication, data=data)
    if not inspect_data:
        await wa.send_error_message()
        return
    entity_type = inspect_data.get("name",None)
    reason = utils.find_error_in_image_inspect(inspect_data,wa.GetLanguage())
    if reason is not None:
        # Send Reason to whatsapp client
        logging.warning(f"Image failed due to {reason}")
        await wa.respond_to_user_image(message_id,reason)
        reaction_emoji = "❌"
    else:
        logging.info(f"Image inserted to db")
        await db.insert_data(f"INSERT INTO pictures (phone_number, path) VALUES ($1,$2)",
                        [from_number, str(media_id)])
        reaction_emoji = "🤩"
        await db.insert_data(f"UPDATE users SET entity_type = $1 WHERE phone = $2 and entity_type IS NULL",
                        (entity_type, from_number))
    await wa.send_reaction_emoji(message_id,reaction_emoji)

async def handle_images(data: FormData, num_media: int, from_number: str,
                        db: dbClient.AsyncDatabaseManager, session: aiohttp.ClientSession, wa: WhatsappWrapper.WhatsappWrapper):
    logging.info(data)
    for i in range(num_media):
        media_id = int(data.get(f"MediaID{i}",0))
        message_id = data.get(f"SmsMessageSid",0)
        image_data = await wa.get_whatsapp_image(media_id)
        await inspect_image(image_data, from_number, media_id, db, session, wa,message_id)