import os
import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import DATABASE_PATH
from config.constants import ROLE_ADMIN

def reset_database():
    """Reset the database and create a fresh admin user"""
    # Delete existing database file
    try:
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            print(f"Deleted existing database: {DATABASE_PATH}")
    except Exception as e:
        print(f"Error deleting database: {e}")
        return False
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            role TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            barcode TEXT UNIQUE,
            price REAL NOT NULL,
            cost_price REAL,
            stock_quantity INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 10,
            image_path TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create customers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create sales table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            payment_method TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create sale items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_percent REAL DEFAULT 0,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Create admin user and sample users
        sample_users = [
            ("admin", "admin123", "Administrator", "admin@supermarket.com", ROLE_ADMIN),
            ("john", "john123", "John Smith", "john.smith@supermarket.com", "cashier"),
            ("sarah", "sarah123", "Sarah Johnson", "sarah.j@supermarket.com", "manager"),
            ("mike", "mike123", "Mike Wilson", "mike.w@supermarket.com", "cashier"),
            ("emma", "emma123", "Emma Davis", "emma.d@supermarket.com", "inventory"),
        ]
        
        for username, password, full_name, email, role in sample_users:
            cursor.execute(
                """
                INSERT INTO users (
                    username, password, full_name, email, role
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (username, generate_password_hash(password), full_name, email, role)
            )
        
        print("\nAdmin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Please use these exact credentials to log in.\n")
        
        # Create sample products
        sample_products = [
            ('Milk', 'Fresh whole milk', 'Dairy', '123456789', 3.99, 2.50, 50, 10),
            ('Bread', 'White bread', 'Bakery', '987654321', 2.49, 1.20, 30, 15),
            ('Apple', 'Fresh red apples', 'Fruits & Vegetables', '456789123', 0.50, 0.30, 100, 20),
            ('Chicken', 'Fresh chicken breast', 'Meat & Poultry', '789123456', 5.99, 4.00, 20, 5),
            ('Cola', 'Cola soft drink', 'Beverages', '321654987', 1.99, 1.00, 60, 24),
            ('Chips', 'Potato chips', 'Snacks', '147258369', 2.99, 1.50, 40, 15),
        ]
        
        cursor.executemany(
            """
            INSERT INTO products (
                name, description, category, barcode,
                price, cost_price, stock_quantity, reorder_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sample_products
        )
        
        # Create sample customers
        sample_customers = [
            ('John Doe', '1234567890', 'john@example.com', '123 Main St', 100),
            ('Jane Smith', '9876543210', 'jane@example.com', '456 Oak Ave', 50),
            ('Bob Wilson', '5555555555', 'bob@example.com', '789 Pine St', 75),
        ]
        
        cursor.executemany(
            """
            INSERT INTO customers (
                name, phone, email, address, loyalty_points
            ) VALUES (?, ?, ?, ?, ?)
            """,
            sample_customers
        )
        
        # Commit changes
        conn.commit()
        print("Database reset successfully!")
        return True
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    reset_database() 