"""
database.py
------------
Handles the MySQL connection for the whole backend.
Every other file (app.py, gst_verification.py) imports get_db_connection()
from here instead of opening its own separate connection.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()  # reads variables from .env file

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "gst_compliance_db")


def get_db_connection():
    """
    Opens and returns a new MySQL connection.
    Call this every time you need to talk to the database,
    and close it when you're done (see usage in app.py).
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print(f"[database.py] ERROR: Could not connect to MySQL: {e}")
        return None


def test_connection():
    """Quick helper to test if the DB connection works. Run this file directly to test."""
    conn = get_db_connection()
    if conn and conn.is_connected():
        print("✅ Successfully connected to MySQL database:", DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("Tables found:", [t[0] for t in tables])
        cursor.close()
        conn.close()
    else:
        print("❌ Could not connect to the database. Check your .env file.")


if __name__ == "__main__":
    test_connection()
