import logging
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

import azure.functions as func
from app.maintenance_handler import MaintenanceHandler
from shared.event_broker import get_event_broker

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
event_broker = get_event_broker()
maintenance_handler = MaintenanceHandler(event_broker)

@app.function_name(name="handle_db_maintenance")
@app.schedule(
    schedule="0 0 4 * * 3",  # Every Wednesday at 4:00 AM UTC
    arg_name="mytimer",
    run_on_startup=False
)
async def handle_db_maintenance(mytimer: func.TimerRequest) -> None:
    """
    Scheduled task to clean up outdated records from database
    Runs weekly to maintain database performance
    """
    try:
        logging.info('Starting database maintenance task')
        await maintenance_handler.cleanup_outdated_records()
        logging.info('Finished database maintenance task')
    except Exception as e:
        logging.error(f"Database maintenance failed: {e}")
        raise
