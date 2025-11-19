import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from db.db_maintenance import delete_outdated_records


class MaintenanceHandler:
    """Handles database maintenance operations"""
    
    def __init__(self, event_broker):
        self.event_broker = event_broker
    
    async def cleanup_outdated_records(self) -> None:
        """Clean up outdated records from database"""
        logging.info("Starting database cleanup")
        
        # Use existing maintenance processor
        await delete_outdated_records()
        
        logging.info("Database cleanup completed")
