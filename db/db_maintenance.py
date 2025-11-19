import datetime
from Utils import dbClient
from db import dbConfig
from Utils.dbClient import AsyncDatabaseManager

async def delete_outdated_records():
    async with AsyncDatabaseManager(dbConfig.db_config) as db:
        await db.insert_data(f"DELETE FROM msgs WHERE date < ($1)",
                                                    [(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).date()])