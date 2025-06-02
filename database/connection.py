import sqlite3
from pathlib import Path

def get_db_connection():
    """Get a connection to the SQLite database"""
    db_path = Path(__file__).parent.parent / 'data' / 'supermarket.db'
    return sqlite3.connect(db_path) 