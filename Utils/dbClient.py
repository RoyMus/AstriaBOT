import asyncpg


class AsyncDatabaseManager:
    def __init__(self, db_config):
        """
        Initialize the AsyncDatabaseManager with the database configuration.
        :param db_config: A dictionary containing database connection parameters
                          (e.g., host, database, user, password, port).
        """
        self.db_config = db_config
        self.conn = None

    async def __aenter__(self):
        self.conn = await asyncpg.connect(
            user=self.db_config.get("user"),
            password=self.db_config.get("password"),
            database=self.db_config.get("database"),
            host=self.db_config.get("host"),
            port=self.db_config.get("port"),
            ssl="require"
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

    async def execute_query(self, query: str, params: tuple = None):
        """
        Execute a query and return the results as a list of dictionaries.
        :param query: The SQL query to execute.
        :param params: A tuple of parameters to pass to the query.
        :return: A list of dictionaries representing the query results.
        """
        rows = await self.conn.fetch(query, *(params or ()))
        return [dict(row) for row in rows]

    async def execute_query_one(self, query: str, params: tuple = None):
        """
        Execute a query and return a single result as a dictionary.
        :param query: The SQL query to execute.
        :param params: A tuple of parameters to pass to the query.
        :return: A dictionary representing the single query result.
        """
        row = await self.conn.fetchrow(query, *(params or ()))
        return dict(row) if row else None

    async def insert_data(self, query, params=None):
        """
        Insert data into the database.
        :param query: The SQL query to execute.
        :param params: A tuple of parameters to pass to the query.
        :return: The number of rows affected.
        """
        result = await self.conn.execute(query, *(params or ()))
        # asyncpg returns a string like 'INSERT 0 1', so we parse the last part
        return int(result.split()[-1])