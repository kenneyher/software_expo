import sqlite3
import os
from pathlib import Path

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".mandarina")
DB_FILE = os.path.join(CONFIG_DIR, "mandarina.db")


def set_up_db() -> None:
    
    os.makedirs(CONFIG_DIR, exist_ok=True)  # ensuring directory exits

    # Create or connect to DB_FILE. This will automatically create the file if it does not exist
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Creating tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            content TEXT,
            priority TEXT CHECK (priority IN ('Low', 'Medium', 'High')),
            status TEXT CHECK (status IN ('Pending', 'Completed')),
            date DATE,
            hour INTEGER,
            minute INTEGER,
            user_id INTEGER,
            FOREIGN KEY (user_id)
                REFERENCES user (user_id)
        )
    ''')

    conn.commit()
    conn.close()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    return conn