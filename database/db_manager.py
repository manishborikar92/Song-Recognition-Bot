import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from datetime import datetime
import os
from config import DB_URL

class DBManager:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(DB_URL)
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
            self.create_tables()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")

    def create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                name TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inputs (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                input_data TEXT,
                date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """)

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create tables: {e}")

    def add_user(self, user_id, name=None):
        """Add a new user to the database."""
        try:
            self.cursor.execute(
                """
                INSERT INTO users (id, name) 
                VALUES (%s, %s) 
                ON CONFLICT (id) DO NOTHING
                """,
                (user_id, name)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to add user: {e}")

    def user_exists(self, user_id):
        """Check if a user exists in the database."""
        try:
            self.cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            raise RuntimeError(f"Failed to check if user exists: {e}")

    def log_input(self, user_id, input_data):
        """Log user input into the database."""
        try:
            self.cursor.execute(
                """
                INSERT INTO inputs (user_id, input_data) 
                VALUES (%s, %s)
                """,
                (user_id, input_data)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to log input: {e}")

    def get_user_history(self, user_id):
        """Retrieve all history for a specific user."""
        try:
            self.cursor.execute(
                """
                SELECT input_data, date_time 
                FROM inputs 
                WHERE user_id = %s
                ORDER BY date_time DESC
                """,
                (user_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve user history: {e}")

    def get_all_users(self):
        """Retrieve all users."""
        try:
            self.cursor.execute("SELECT id, name FROM users")
            return self.cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve all users: {e}")

    def delete_user_data(self, user_id=None):
        """Delete data for a specific user or all users."""
        try:
            if user_id:
                self.cursor.execute("DELETE FROM inputs WHERE user_id = %s", (user_id,))
                self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            else:
                self.cursor.execute("TRUNCATE TABLE inputs CASCADE")
                self.cursor.execute("TRUNCATE TABLE users CASCADE")
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to delete user data: {e}")

    def close(self):
        """Close the database connection."""
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to close the database connection: {e}")
