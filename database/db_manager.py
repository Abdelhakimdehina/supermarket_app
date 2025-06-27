import os
import sqlite3
from typing import Optional, List, Dict, Any

from config.settings import DATABASE_PATH, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD
from config.constants import ROLE_ADMIN
from utils.security import hash_password

class DBManager:
    """Database manager for the application"""
    
    def __init__(self):
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        # Initialize database
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables if they don't exist
        self.create_tables()
        
        # Create default admin user if no users exist
        self.create_default_admin()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Users table
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
        
        # Products table
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
        
        # Create sample products if none exist
        cursor.execute("SELECT COUNT(*) as count FROM products")
        result = cursor.fetchone()
        
        if result['count'] == 0:
            # Add sample products
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
        
        # Inventory transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity_change INTEGER NOT NULL,
            previous_quantity INTEGER NOT NULL,
            new_quantity INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            reason TEXT,
            notes TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Customers table
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
        
        # Sales table
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
        
        # Sale items table
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
        
        # Commit changes
        self.conn.commit()
    
    def create_default_admin(self):
        """Create default admin user if no users exist"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        
        if result['count'] == 0:
            # Create default admin user
            hashed_password = hash_password(DEFAULT_ADMIN_PASSWORD)
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                (DEFAULT_ADMIN_USERNAME, hashed_password, "Administrator", ROLE_ADMIN)
            )
            self.conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[Dict[str, Any]]]:
        """Execute a query and return the results"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            return [dict(row) for row in results]
        else:
            self.conn.commit()
            return None
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()