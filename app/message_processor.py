import json 
import logging
from Utils import dbClient, constants, states, WhatsappWrapper, WhatsappClient
import aiohttp
from db import dbConfig
from datetime import datetime, timezone
from app.image_processors import handle_images, tune_model_using_pack, get_tunes_for_user
from Utils import message_ids, aiohttp_retry
from app.state_handlers import StateHandlerFactory


async def send_user_pack_options(wa: WhatsappWrapper.WhatsappWrapper, session: aiohttp.ClientSession, from_number: str,db:dbClient.AsyncDatabaseManager,type_of_pack:str):
    packs = await aiohttp_retry.get_with_retry(f"{constants.ASTRIA_API_URL}/packs?listed=true",
                        session=session, headers=constants.ASTRIA_API_Authentication)
    if not packs:
        await wa.send_error_message()
        return
    logging.info(f"Got packs: {packs}")
    row = await db.execute_query_one(f"SELECT entity_type FROM users WHERE phone = $1", (from_number,))
    if row:
        entity_type = row["entity_type"]
        relevant_packs = [pack for pack in packs if type_of_pack in pack["slug"]]
        if type_of_pack == "lite":
            price = constants.LITE_TIER_PRICE
        elif type_of_pack == "standard":
            price = constants.STANDARD_TIER_PRICE
        else:
            price = constants.PREMIUM_TIER_PRICE
        await wa.send_prepacks_msg(relevant_packs,entity_type,price)

async def send_video_examples(wa: WhatsappWrapper.WhatsappWrapper, pack_id: str, entity_type: str):
    url = f"{constants.STORAGE_BLOB_URL}/{pack_id}_{entity_type}.mp4"
    logging.info(f"Sending video examples from {url}")
    await wa.send_video_example(url)


async def _parse_reply_id(reply_message: dict) -> tuple:
    """Parse reply message and return (id, data) tuple"""
    reply_id = reply_message.get("id", -1)
    if reply_id == -1:
        return None, None
    
    reply_parts = str(reply_id).split("_")
    if len(reply_parts) > 1:
        return int(reply_parts[0]), int(reply_parts[1])
    else:
        return int(reply_parts[0]), None


async def _parse_list_reply(list_reply: dict) -> tuple:
    """Parse list reply and return (id, data) tuple"""
    list_id = list_reply.get("id", -1)
    if list_id == -1:
        return None, None
    
    list_parts = str(list_id).split("_")
    if len(list_parts) > 1:
        return int(list_parts[0]), int(list_parts[1])
    else:
        return int(list_parts[0]), None


async def _handle_reply_message(handler : StateHandlerFactory.StateHandler, reply_message: dict, user: dict) -> None:
    """Route reply message to appropriate handler method"""
    reply_id, reply_data = await _parse_reply_id(reply_message)
    if reply_id is None:
        return
    
    # Handle star rating specially
    if reply_id == message_ids.STAR_RATING and reply_data is not None:
        await handler.db.insert_data(
            f"INSERT INTO ratings (phone_number, rating, date) VALUES ($1, $2, $3)",
            (handler.from_number, reply_data, datetime.now(timezone.utc).date())
        )
        should_ask_for_feedback = reply_data < 4
        await handler.wa.send_feedback_comment(should_ask_for_feedback)
        if should_ask_for_feedback:
            user["state"] = states.States.WRITING_FEEDBACK.value
            await handler.db.insert_data(
                f"UPDATE users SET state = $1 WHERE phone = $2",
                (user["state"], handler.from_number)
            )
        return
    
    # Handle pack selection
    if reply_id not in [message_ids.BEGIN_REPLY, message_ids.READY_FOR_IMAGE_UPLOAD, 
                        message_ids.SHOW_EXAMPLES, message_ids.OVERRIDE_TUNE, 
                        message_ids.SEND_TUNES, message_ids.GET_PAYMENT_LINK,
                        message_ids.CONTACT_SUPPORT, message_ids.SEND_PACKS,
                        message_ids.SHOW_PACK_IMAGES, message_ids.SET_TUNE]:
        # It's a pack selection (numeric id)
        logging.info(f"User selected pack {reply_id}")
        async with handler.session.get(f"{constants.ASTRIA_API_URL}/packs",
                                    headers=constants.ASTRIA_API_Authentication) as response:
            if not response.ok:
                return
            packs = await response.json()
            for pack in packs:
                if pack["id"] == reply_id:
                    if user["state"] in [states.States.PICTURESLOADED.value, states.States.TUNEREADY.value]:
                        await handler.db.insert_data(
                            f"UPDATE users SET chosen_pack = $1 WHERE phone = $2",
                            (str(reply_id), handler.from_number)
                        )
                        await handler.wa.send_user_agreement_msg()
                    return
    
    # Delegate to state handler
    await handler.handle_reply_message(reply_id, reply_data)


async def _handle_list_reply(handler, list_reply: dict, user: dict) -> None:
    """Route list reply to appropriate handler method"""
    list_id, list_data = await _parse_list_reply(list_reply)
    if list_id is None:
        return
    
    # Handle star rating specially (for list replies)
    if list_id == message_ids.STAR_RATING and list_data is not None:
        await handler.db.insert_data(
            f"INSERT INTO ratings (phone_number, rating, date) VALUES ($1, $2, $3)",
            (handler.from_number, list_data, datetime.now(timezone.utc).date())
        )
        should_ask_for_feedback = list_data < 4
        await handler.wa.send_feedback_comment(should_ask_for_feedback)
        if should_ask_for_feedback:
            user["state"] = states.States.WRITING_FEEDBACK.value
            await handler.db.insert_data(
                f"UPDATE users SET state = $1 WHERE phone = $2",
                (user["state"], handler.from_number)
            )
        return
    
    # Delegate to state handler
    await handler.handle_list_reply(list_id, list_data)
                                
async def process_message(messages):
    logging.info('Processing message from queue') 
    for message in messages:
        num_media = int(message.get("NumMedia", 0))  # Number of media files
        from_number = message.get("From")
        reply_message = message.get("reply",0)
        list_reply = message.get("list_reply",0)
        invalid_media = message.get("InvalidMedia",False)
        message_id = message.get(f"SmsMessageSid",0)
        text_body = message.get("Body", "")
        async with aiohttp.ClientSession() as session:
            async with dbClient.AsyncDatabaseManager(dbConfig.db_config) as db:
                if not invalid_media:
                    user = None
                    try:
                        await db.insert_data(f"INSERT INTO msgs (id, date) VALUES ($1, $2)", (message["SmsMessageSid"], datetime.now(timezone.utc).date()))
                        logging.info("Processing message with id " + message["SmsMessageSid"])
                    except Exception as e:
                        logging.info(f"Message duplicate stopped {e}")
                        return
                user = await db.execute_query_one(f"SELECT * FROM users WHERE phone = $1", (from_number,))
                if user is None:
                    logging.info(f"{from_number} User entered db")
                    try:
                        user = dict()
                        user["credits"] = "0"
                        user["tuneID"] = None
                        user["chosen_pack"] = None
                        user["entity_type"] = None
                        user["state"] = states.States.NEW.value
                        user["phone"] = from_number
                        user["language"] = states.Languages.ENGLISH.value
                        await db.insert_data(f"INSERT INTO users (phone, state, credits, tuneID, chosen_pack,entity_type, language) VALUES ($1, $2, '0', NULL, NULL,NULL, $3)",
                                    [from_number, user["state"], user["language"]])
                        
                    except Exception as ex:
                        return
                    
                async with WhatsappWrapper.WhatsappWrapper(from_number,user["language"]) as wa:
                    await wa.send_typing_indicator(message_id)
                    if invalid_media:
                        await wa.send_invalid_media_message()
                        return
                    
                    # Use state machine to handle message
                    handler = StateHandlerFactory.create_handler(
                        user["state"], user, from_number, db, session, wa
                    )
                    
                    if num_media > 0:
                        logging.info(f"Processing media for user in state {user['state']}")
                        await handler.handle_media(message, num_media)
                    
                    elif reply_message != 0:
                        await _handle_reply_message(handler, reply_message, user)
                    
                    elif list_reply != 0:
                        await _handle_list_reply(handler, list_reply, user)
                    
                    else:
                        await handler.handle_text_message(text_body)
