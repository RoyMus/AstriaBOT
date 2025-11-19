from datetime import datetime, timezone
import azure.functions as func
from Utils import constants, WhatsappWrapper
import aiohttp
import logging
from Utils import dbClient
from app import image_processors
from db import dbConfig
from Utils import aiohttp_retry
async def process_payment(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    paymentID = data['EntityID']
    phone_number = data['Properties']['Property_M-5'][0]
    full_name = data['Properties']['Property_M-10'][0]
    tier = str(data['Properties']['Property_M-3'][0]['Name'])
    logging.info(f"Received payment notification: paymentID={paymentID}, phone_number={phone_number}, full_name={full_name}, tier={tier}")
    async with dbClient.AsyncDatabaseManager(dbConfig.db_config) as db:
        if paymentID:
            paymentID = str(paymentID)
            try:
                await db.insert_data(f"INSERT INTO payments (id, date) VALUES ($1, $2)", (paymentID, datetime.now(timezone.utc).date()))
                logging.info("Processing payment with id " + paymentID)
            except Exception as e:
                logging.info(f"payment stopped due to {e}")
                return func.HttpResponse("OK",status_code=200)

        if phone_number:
            try:
                result = await db.execute_query_one(f"SELECT chosen_pack,tuneid,entity_type,language FROM users WHERE phone = $1",
                                                (phone_number,))
                if result:
                    pack_id = result.get("chosen_pack", None)
                    entity_type = result.get("entity_type", None)
                    async with aiohttp.ClientSession() as session:
                        pack_data = await aiohttp_retry.get_with_retry(f"{constants.ASTRIA_API_URL}/p/{str(pack_id)}",
                                            session=session, headers=constants.ASTRIA_API_Authentication)
                        if not pack_data:
                            return func.HttpResponse("Error fetching pack data", status_code=500)
                        if tier.lower() not in pack_data['slug']:
                            slug_without_tier = ''.join(pack_data['slug'].split('-')[:-1])
                            pack_id = await find_suitable_pack(tier,slug_without_tier,entity_type)
                            await db.execute_query(f"UPDATE users SET chosen_pack = $1 WHERE phone = $2",
                                                (str(pack_id) if pack_id else None, phone_number))
                        tune_id = result.get("tuneid", None)
                        language = result.get("language", None)
                        async with WhatsappWrapper.WhatsappWrapper(phone_number,language) as wa:
                            await wa.send_paymentreceived_msg(full_name)
                            user_images = await db.execute_query(f"SELECT path FROM pictures WHERE phone_number = $1",
                                                                (phone_number,))
                            if pack_id:
                                await image_processors.tune_model_using_pack(wa, phone_number, user_images, db, session,
                                                                    pack_id, tune_id, entity_type)
                    
            except Exception as e:
                logging.error(f"Error inserting payment data: {e}")
                return func.HttpResponse("Error inserting payment data", status_code=500)
            
    return func.HttpResponse("OK",status_code=200)

async def find_suitable_pack(tier,current_slug,entity_type,wa:WhatsappWrapper.WhatsappWrapper=None):
    chosen_pack = None
    async with aiohttp.ClientSession() as session:
        packs = await aiohttp_retry.get_with_retry(f"{constants.ASTRIA_API_URL}/packs",
                            session=session, headers=constants.ASTRIA_API_Authentication)
        if not packs:
            await wa.send_error_message()
            return None
    for pack in packs:
        costs = pack["costs"].get(entity_type)
        if costs is None:
            continue
        slug_without_tier = ''.join(pack['slug'].split('-')[:-1])
        if chosen_pack is None and tier.lower() in pack['slug']:
            chosen_pack = pack['id']
            continue
        if tier.lower() in pack['slug'] and current_slug in slug_without_tier:
            chosen_pack = pack['id']
            break
    return chosen_pack