import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from werkzeug.security import generate_password_hash
from config.settings import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD

def init_db():
    """Initialize the database with schema and sample data"""
    # Get the database directory path
    db_dir = Path(__file__).parent.parent / 'data'
    
    # Create the data directory if it doesn't exist
    db_dir.mkdir(exist_ok=True)
    
    # Database file path
    db_path = db_dir / 'supermarket.db'
    
    # Remove existing database file
    if db_path.exists():
        os.remove(db_path)
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute schema
        with open(Path(__file__).parent / 'schema.sql', 'r') as f:
            cursor.executescript(f.read())
        
        # Read and execute sample data
        with open(Path(__file__).parent / 'sample_data.sql', 'r') as f:
            cursor.executescript(f.read())
        
        # Create default admin user with password from settings
        password_hash = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
        cursor.execute("""
            INSERT INTO users (
                username, password_hash, full_name, email, role,
                is_active, created_at, updated_at
            ) VALUES (
                ?, ?, 'System Administrator', 'admin@example.com', 'admin',
                1, DATETIME('now'), DATETIME('now')
            )
        """, (DEFAULT_ADMIN_USERNAME, password_hash))
        
        # Commit changes
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    init_db() 