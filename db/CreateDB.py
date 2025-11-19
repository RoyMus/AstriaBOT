# Connect to a PostgreSQL database (creates tables if they don't exist)
import psycopg2
from psycopg2 import sql
from Utils import constants
from dbConfig import db_config  # Ensure you have your PostgreSQL config here

# Connect to the PostgreSQL database
try:
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Enable foreign key constraints (PostgreSQL enforces this by default)
    # No need for PRAGMA foreign_keys as in SQLite

    # Create the "users" table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY NOT NULL,
            state INTEGER NOT NULL,
            credits TEXT NOT NULL,
            tuneID TEXT,
            chosen_pack TEXT,
            entity_type TEXT,
            language INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS msgs (
            id TEXT PRIMARY KEY NOT NULL,
            date DATE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY NOT NULL,
            date DATE NOT NULL
        )
    """)

    # Create the "pictures" table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pictures (
            phone_number TEXT NOT NULL,
            path TEXT NOT NULL,
            FOREIGN KEY (phone_number) REFERENCES users(phone) ON DELETE CASCADE
        )
    """)
    # Create the "Ratings" table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            phone_number TEXT NOT NULL,
            rating INTEGER NOT NULL,
            date DATE NOT NULL,
            feedback TEXT
        )
    """)
    # Commit changes
    conn.commit()
    print("Tables created successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection
    if conn:
        cursor.close()
        conn.close()
