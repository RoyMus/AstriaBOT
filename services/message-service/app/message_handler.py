import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.message_processor import process_message


class MessageHandler:
    """Orchestrates message processing workflow"""
    
    def __init__(self, event_broker):
        self.event_broker = event_broker
    
    async def process_messages(self, messages: list) -> None:
        """Process incoming WhatsApp messages"""
        for message in messages:
            logging.info(f"Processing message: {message.get('SmsMessageSid')}")
            
            try:
                # Use existing message processor with event broker
                await process_message(messages, event_broker=self.event_broker)
            except Exception as e:
                logging.error(f"Failed to process message: {e}")
                raise
