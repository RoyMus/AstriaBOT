import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.image_processors import handle_images_from_astria
from app.astria_images_video_processors import update_pack_images


class ImageHandler:
    """Handles all image processing operations"""
    
    def __init__(self, event_broker):
        self.event_broker = event_broker
    
    async def handle_astria_images(self, req) -> None:
        """Process images received from Astria webhook"""
        logging.info("Processing images from Astria")
        
        # Use existing image processor
        response = await handle_images_from_astria(req)
        
        # Publish event for other services
        # (e.g., message service can notify user)
        # event = ImageProcessedEvent(
        #     data={...}
        # )
        # await self.event_broker.publish(event)
        
        return response
    
    async def update_pack_images(self) -> None:
        """Update pack images in Azure Storage"""
        logging.info("Updating pack images")
        
        # Use existing image update processor
        await update_pack_images()
        
        # Publish event
        # event = PackImagesUpdatedEvent(...)
        # await self.event_broker.publish(event)
