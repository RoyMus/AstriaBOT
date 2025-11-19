import logging
from abc import ABC, abstractmethod
from Utils import dbClient, constants, states, WhatsappWrapper, message_ids, aiohttp_retry
from app.image_processors import handle_images, get_tunes_for_user
from datetime import datetime, timezone
import aiohttp


class StateHandler(ABC):
    """Base class for handling user states"""
    
    def __init__(self, user: dict, from_number: str, db: dbClient.AsyncDatabaseManager, 
                 session: aiohttp.ClientSession, wa: WhatsappWrapper.WhatsappWrapper):
        self.user = user
        self.from_number = from_number
        self.db = db
        self.session = session
        self.wa = wa
    
    @abstractmethod
    async def handle_media(self, message: dict, num_media: int) -> None:
        """Handle incoming media/images"""
        pass
    
    @abstractmethod
    async def handle_reply_message(self, reply_id: int, reply_data: int = None) -> None:
        """Handle single-part reply messages"""
        pass
    
    @abstractmethod
    async def handle_list_reply(self, list_id: int, list_data: int = None) -> None:
        """Handle multi-part list replies"""
        pass
    
    @abstractmethod
    async def handle_text_message(self, text: str) -> None:
        """Handle text messages"""
        pass


class NewUserStateHandler(StateHandler):
    """Handles NEW state - waiting for initial images"""
    
    async def handle_media(self, message: dict, num_media: int) -> None:
        """Process uploaded images for new user"""
        logging.info("Got images from NEW user")
        await handle_images(message, num_media, self.from_number, self.db, self.session, self.wa)
        
        user_images = await self.db.execute_query(
            f"SELECT path FROM pictures WHERE phone_number = $1",
            (self.from_number,)
        )
        
        if len(user_images) >= int(constants.MAX_IMAGES_THRESHOLD):
            logging.info("Got all images - transitioning to PICTURESLOADED")
            rowCount = await self.db.insert_data(
                f"UPDATE users SET state = $1 WHERE phone = $2 AND state = $3",
                (states.States.PICTURESLOADED.value, self.from_number, states.States.NEW.value)
            )
            if rowCount > 0:
                await self.wa.send_additional_images_request()
    
    async def handle_reply_message(self, reply_id: int, reply_data: int = None) -> None:
        """Handle reply messages in NEW state"""
        if reply_id == message_ids.BEGIN_REPLY:
            await self.wa.send_imageguidelines_msg()
        elif reply_id == message_ids.READY_FOR_IMAGE_UPLOAD:
            await self.wa.send_upload_images_request()
        elif reply_id == message_ids.SHOW_EXAMPLES:
            await self.wa.send_additional_guidelines_images()
        elif reply_id == message_ids.OVERRIDE_TUNE:
            await self._reset_user_state()
        elif reply_id == message_ids.SEND_TUNES:
            await self._send_user_tunes()
        elif reply_id == message_ids.GET_PAYMENT_LINK:
            await self._send_payment_link()
        elif reply_id == message_ids.CONTACT_SUPPORT:
            await self.wa.send_support_email()
        elif reply_id == message_ids.SEND_PACKS:
            await self.wa.send_pack_tiers_msg()
    
    async def handle_list_reply(self, list_id: int, list_data: int = None) -> None:
        """Handle list replies in NEW state"""
        if list_id == message_ids.BEGIN_REPLY:
            await self.wa.send_imageguidelines_msg()
        elif list_id == message_ids.HOW_IT_WORKS:
            await self.wa.send_howitworks_msg()
        elif list_id == message_ids.CHANGE_LANGUAGE:
            await self._change_language()
        elif list_id == message_ids.UPLOAD_MORE_IMAGES:
            await self.wa.send_upload_images_request(False)
        elif list_id == message_ids.SEND_PACKS:
            await self.wa.send_pack_tiers_msg()
        elif list_id == message_ids.OVERRIDE_TUNE:
            await self._reset_user_state()
        elif list_id == message_ids.CONTACT_SUPPORT:
            await self.wa.send_support_email()
        elif list_id == message_ids.LITE_PACK:
            await self._send_pack_options("lite")
        elif list_id == message_ids.STANDARD_PACK:
            await self._send_pack_options("standard")
        elif list_id == message_ids.PREMIUM_PACK:
            await self._send_pack_options("premium")
    
    async def handle_text_message(self, text: str) -> None:
        """Handle text in NEW state"""
        await self.wa.send_init_msg()
    
    # Helper methods
    async def _reset_user_state(self) -> None:
        """Reset user to initial state"""
        await self.db.insert_data(
            f"UPDATE users SET state = $1, tuneID = $2, entity_type = $3, chosen_pack = $4 WHERE phone = $5",
            (states.States.NEW.value, None, None, None, self.from_number)
        )
        await self.db.insert_data("DELETE FROM pictures WHERE phone_number = $1", (self.from_number,))
        await self.wa.send_imageguidelines_msg()
    
    async def _send_user_tunes(self) -> None:
        """Send user's existing tunes"""
        tunes = await get_tunes_for_user(self.from_number, self.session)
        if len(tunes) > 0:
            await self.wa.send_tunes_to_client(tunes)
    
    async def _send_payment_link(self) -> None:
        """Send payment link based on selected pack"""
        pack = await aiohttp_retry.get_with_retry(
            f"{constants.ASTRIA_API_URL}/p/{str(self.user['chosen_pack'])}",
            session=self.session,
            headers=constants.ASTRIA_API_Authentication
        )
        if not pack:
            await self.wa.send_error_message()
            return
        
        if "lite" in pack["slug"]:
            payment_link = constants.LITE_TIER_PAYMENT_LINK
        elif "standard" in pack["slug"]:
            payment_link = constants.STANDARD_TIER_PAYMENT_LINK
        else:
            payment_link = constants.PREMIUM_TIER_PAYMENT_LINK
        
        await self.wa.send_paymentlink_msg(payment_link=payment_link)
    
    async def _change_language(self) -> None:
        """Toggle user language"""
        self.user["language"] = (
            states.Languages.HEBREW.value 
            if self.user["language"] == states.Languages.ENGLISH.value 
            else states.Languages.ENGLISH.value
        )
        await self.db.insert_data(
            f"UPDATE users SET language = $1 WHERE phone = $2",
            (self.user["language"], self.from_number)
        )
        self.wa.setLanguage(self.user["language"])
        await self.wa.send_init_msg()
    
    async def _send_pack_options(self, pack_type: str) -> None:
        """Send pack options for given type"""
        from app.message_processor import send_user_pack_options
        await send_user_pack_options(self.wa, self.session, self.from_number, self.db, pack_type)


class PicturesLoadedStateHandler(StateHandler):
    """Handles PICTURESLOADED state - waiting for pack selection"""
    
    async def handle_media(self, message: dict, num_media: int) -> None:
        """Allow additional images in PICTURESLOADED state"""
        await handle_images(message, num_media, self.from_number, self.db, self.session, self.wa)
    
    async def handle_reply_message(self, reply_id: int, reply_data: int = None) -> None:
        """Handle reply messages in PICTURESLOADED state"""
        if reply_id == message_ids.SHOW_PACK_IMAGES and reply_data is not None:
            await self._send_video_examples(reply_data)
        elif reply_id == message_ids.SET_TUNE and reply_data is not None:
            await self._set_tune(reply_data)
        elif reply_id == message_ids.UPLOAD_MORE_IMAGES:
            await self.wa.send_upload_images_request(False)
        elif reply_id == message_ids.OVERRIDE_TUNE:
            await self._reset_user_state()
        else:
            await self._handle_generic_reply(reply_id)
    
    async def handle_list_reply(self, list_id: int, list_data: int = None) -> None:
        """Handle list replies in PICTURESLOADED state"""
        if list_id == message_ids.BEGIN_REPLY:
            await self.wa.send_imageguidelines_msg()
        elif list_id == message_ids.HOW_IT_WORKS:
            await self.wa.send_howitworks_msg()
        elif list_id == message_ids.CHANGE_LANGUAGE:
            await self._change_language()
        elif list_id == message_ids.SEND_PACKS:
            await self.wa.send_pack_tiers_msg()
        elif list_id == message_ids.OVERRIDE_TUNE:
            await self._reset_user_state()
        elif list_id == message_ids.CONTACT_SUPPORT:
            await self.wa.send_support_email()
        elif list_id == message_ids.LITE_PACK:
            await self._send_pack_options("lite")
        elif list_id == message_ids.STANDARD_PACK:
            await self._send_pack_options("standard")
        elif list_id == message_ids.PREMIUM_PACK:
            await self._send_pack_options("premium")
    
    async def handle_text_message(self, text: str) -> None:
        """Handle text in PICTURESLOADED state"""
        await self.wa.send_additional_images_request()
    
    # Helper methods
    async def _send_video_examples(self, pack_id: int) -> None:
        """Send video examples for pack"""
        url = f"{constants.STORAGE_BLOB_URL}/videos/videos/{pack_id}_{self.user['entity_type']}.mp4"
        logging.info(f"Sending video examples from {url}")
        await self.wa.send_video_example(url)
    
    async def _set_tune(self, pack_id: int) -> None:
        """Set user's tune"""
        pack = await aiohttp_retry.get_with_retry(
            f"{constants.ASTRIA_API_URL}/p/{str(pack_id)}",
            session=self.session,
            headers=constants.ASTRIA_API_Authentication
        )
        if not pack:
            await self.wa.send_error_message()
            return
        
        await self.db.insert_data(
            f"UPDATE users SET tuneID = $1, entity_type = $2, chosen_pack = $3 WHERE phone = $4",
            (str(pack_id), pack["name"], None, self.from_number)
        )
        from app.message_processor import send_user_pack_options
        await send_user_pack_options(self.wa, self.session, self.from_number, self.db, "")
    
    async def _reset_user_state(self) -> None:
        """Reset user to NEW state"""
        await self.db.insert_data(
            f"UPDATE users SET state = $1, tuneID = $2, entity_type = $3, chosen_pack = $4 WHERE phone = $5",
            (states.States.NEW.value, None, None, None, self.from_number)
        )
        await self.db.insert_data("DELETE FROM pictures WHERE phone_number = $1", (self.from_number,))
        await self.wa.send_imageguidelines_msg()
    
    async def _change_language(self) -> None:
        """Toggle user language"""
        self.user["language"] = (
            states.Languages.HEBREW.value 
            if self.user["language"] == states.Languages.ENGLISH.value 
            else states.Languages.ENGLISH.value
        )
        await self.db.insert_data(
            f"UPDATE users SET language = $1 WHERE phone = $2",
            (self.user["language"], self.from_number)
        )
        self.wa.setLanguage(self.user["language"])
        await self.wa.send_init_msg()
    
    async def _send_pack_options(self, pack_type: str) -> None:
        """Send pack options"""
        from app.message_processor import send_user_pack_options
        await send_user_pack_options(self.wa, self.session, self.from_number, self.db, pack_type)
    
    async def _handle_generic_reply(self, reply_id: int) -> None:
        """Handle generic replies"""
        if reply_id == message_ids.BEGIN_REPLY:
            await self.wa.send_imageguidelines_msg()
        elif reply_id == message_ids.SHOW_EXAMPLES:
            await self.wa.send_additional_guidelines_images()
        elif reply_id == message_ids.SEND_PACKS:
            await self.wa.send_pack_tiers_msg()
        elif reply_id == message_ids.CONTACT_SUPPORT:
            await self.wa.send_support_email()


class TuneReadyStateHandler(StateHandler):
    """Handles TUNEREADY state - returning customer"""
    
    async def handle_media(self, message: dict, num_media: int) -> None:
        """Don't accept new images when tune is ready"""
        logging.info("Ignoring media upload in TUNEREADY state")
        return
    
    async def handle_reply_message(self, reply_id: int, reply_data: int = None) -> None:
        """Handle reply messages in TUNEREADY state"""
        if reply_id == message_ids.SHOW_PACK_IMAGES and reply_data is not None:
            await self._send_video_examples(reply_data)
        elif reply_id == message_ids.OVERRIDE_TUNE:
            await self._reset_user_state()
        elif reply_id == message_ids.SEND_TUNES:
            await self._send_user_tunes()
        elif reply_id == message_ids.GET_PAYMENT_LINK:
            await self._send_payment_link()
        elif reply_id == message_ids.CONTACT_SUPPORT:
            await self.wa.send_support_email()
        elif reply_id == message_ids.SEND_PACKS:
            await self.wa.send_pack_tiers_msg()
    
    async def handle_list_reply(self, list_id: int, list_data: int = None) -> None:
        """Handle list replies in TUNEREADY state"""
        if list_id == message_ids.BEGIN_REPLY:
            await self.wa.send_returning_customer_msg()
        elif list_id == message_ids.HOW_IT_WORKS:
            await self.wa.send_howitworks_msg()
        elif list_id == message_ids.CHANGE_LANGUAGE:
            await self._change_language()
        elif list_id == message_ids.SEND_PACKS:
            await self.wa.send_pack_tiers_msg()
        elif list_id == message_ids.OVERRIDE_TUNE:
            await self._reset_user_state()
        elif list_id == message_ids.CONTACT_SUPPORT:
            await self.wa.send_support_email()
        elif list_id == message_ids.LITE_PACK:
            await self._send_pack_options("lite")
        elif list_id == message_ids.STANDARD_PACK:
            await self._send_pack_options("standard")
        elif list_id == message_ids.PREMIUM_PACK:
            await self._send_pack_options("premium")
    
    async def handle_text_message(self, text: str) -> None:
        """Handle text in TUNEREADY state"""
        await self.wa.send_returning_customer_msg()
    
    # Helper methods
    async def _send_video_examples(self, pack_id: int) -> None:
        """Send video examples"""
        url = f"https://whatsappuploadimages.blob.core.windows.net/videos/videos/{pack_id}_{self.user['entity_type']}.mp4"
        logging.info(f"Sending video examples from {url}")
        await self.wa.send_video_example(url)
    
    async def _reset_user_state(self) -> None:
        """Reset user to NEW state"""
        await self.db.insert_data(
            f"UPDATE users SET state = $1, tuneID = $2, entity_type = $3, chosen_pack = $4 WHERE phone = $5",
            (states.States.NEW.value, None, None, None, self.from_number)
        )
        await self.db.insert_data("DELETE FROM pictures WHERE phone_number = $1", (self.from_number,))
        await self.wa.send_imageguidelines_msg()
    
    async def _send_user_tunes(self) -> None:
        """Send user's tunes"""
        tunes = await get_tunes_for_user(self.from_number, self.session)
        if len(tunes) > 0:
            await self.wa.send_tunes_to_client(tunes)
    
    async def _send_payment_link(self) -> None:
        """Send payment link"""
        pack = await aiohttp_retry.get_with_retry(
            f"{constants.ASTRIA_API_URL}/p/{str(self.user['chosen_pack'])}",
            session=self.session,
            headers=constants.ASTRIA_API_Authentication
        )
        if not pack:
            await self.wa.send_error_message()
            return
        
        if "lite" in pack["slug"]:
            payment_link = constants.LITE_TIER_PAYMENT_LINK
        elif "standard" in pack["slug"]:
            payment_link = constants.STANDARD_TIER_PAYMENT_LINK
        else:
            payment_link = constants.PREMIUM_TIER_PAYMENT_LINK
        
        await self.wa.send_paymentlink_msg(payment_link=payment_link)
    
    async def _change_language(self) -> None:
        """Toggle language"""
        self.user["language"] = (
            states.Languages.HEBREW.value 
            if self.user["language"] == states.Languages.ENGLISH.value 
            else states.Languages.ENGLISH.value
        )
        await self.db.insert_data(
            f"UPDATE users SET language = $1 WHERE phone = $2",
            (self.user["language"], self.from_number)
        )
        self.wa.setLanguage(self.user["language"])
        await self.wa.send_init_msg()
    
    async def _send_pack_options(self, pack_type: str) -> None:
        """Send pack options"""
        from app.message_processor import send_user_pack_options
        await send_user_pack_options(self.wa, self.session, self.from_number, self.db, pack_type)


class WritingFeedbackStateHandler(StateHandler):
    """Handles WRITING_FEEDBACK state - user providing feedback"""
    
    async def handle_media(self, message: dict, num_media: int) -> None:
        """Don't process media in feedback state"""
        return
    
    async def handle_reply_message(self, reply_id: int, reply_data: int = None) -> None:
        """Handle reply in feedback state"""
        pass
    
    async def handle_list_reply(self, list_id: int, list_data: int = None) -> None:
        """Handle list reply in feedback state"""
        pass
    
    async def handle_text_message(self, text: str) -> None:
        """Process feedback text"""
        await self.db.insert_data(
            f"UPDATE ratings SET feedback = $1 WHERE phone_number = $2 AND date = $3",
            (text, self.from_number, datetime.now(timezone.utc).date())
        )
        await self.wa.send_feedback_comment(False)
        await self.db.insert_data(
            f"UPDATE users SET state = $1 WHERE phone = $2",
            (states.States.TUNEREADY.value, self.from_number)
        )
        await self.wa.send_support_email()


class StateHandlerFactory:
    """Factory for creating appropriate state handlers"""
    
    _handlers = {
        states.States.NEW.value: NewUserStateHandler,
        states.States.PICTURESLOADED.value: PicturesLoadedStateHandler,
        states.States.TUNEREADY.value: TuneReadyStateHandler,
        states.States.WRITING_FEEDBACK.value: WritingFeedbackStateHandler,
    }
    
    @staticmethod
    def create_handler(state: int, user: dict, from_number: str, 
                      db: dbClient.AsyncDatabaseManager, session: aiohttp.ClientSession,
                      wa: WhatsappWrapper.WhatsappWrapper) -> StateHandler:
        """Create appropriate handler for user state"""
        handler_class = StateHandlerFactory._handlers.get(state)
        if handler_class is None:
            logging.warning(f"Unknown state {state}, defaulting to NEW")
            handler_class = NewUserStateHandler
        return handler_class(user, from_number, db, session, wa)
