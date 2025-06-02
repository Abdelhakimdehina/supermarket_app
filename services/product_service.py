import sqlite3
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from database.connection import get_db_connection

from config.settings import DATABASE_PATH

class ProductService:
    """Service for managing products"""
    
    def __init__(self):
        """Initialize the service"""
        self.db_path = DATABASE_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_products(
        self, 
        category: Optional[str] = None, 
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get products based on category and search term"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Base query
            query = """
                SELECT id, name, description, price, stock, category, barcode
                FROM products
                WHERE is_active = 1
            """
            params = []
            
            # Add category filter if provided
            if category:
                query += " AND category = ?"
                params.append(category)
            
            # Add search filter if provided
            if search_term:
                query += " AND (name LIKE ? OR barcode LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%"])
            
            # Execute query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            products = []
            for row in rows:
                products.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': float(row[3]),
                    'stock': int(row[4]),
                    'category': row[5],
                    'barcode': row[6]
                })
            
            return products
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
            
        finally:
            cursor.close()
            conn.close()
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a single product by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, description, price, stock, category, barcode
                FROM products
                WHERE id = ? AND is_active = 1
            """, (product_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': float(row[3]),
                    'stock': int(row[4]),
                    'category': row[5],
                    'barcode': row[6]
                }
            
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[int]:
        """Create a new product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                INSERT INTO products (
                    name, description, price, stock, category, barcode,
                    is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                product_data['name'],
                product_data.get('description'),
                product_data['price'],
                product_data.get('stock', 0),
                product_data['category'],
                product_data.get('barcode'),
                now, now
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Update an existing product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                UPDATE products
                SET name = ?,
                    description = ?,
                    price = ?,
                    stock = ?,
                    category = ?,
                    barcode = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                product_data['name'],
                product_data.get('description'),
                product_data['price'],
                product_data.get('stock', 0),
                product_data['category'],
                product_data.get('barcode'),
                now,
                product_id
            ))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                UPDATE products
                SET is_active = 0,
                    updated_at = ?
                WHERE id = ?
            """, (now, product_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def update_stock(self, product_id: int, quantity_change: int) -> bool:
        """Update product stock quantity"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get current stock
            cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            current_stock = row[0]
            new_stock = current_stock + quantity_change
            
            # Don't allow negative stock
            if new_stock < 0:
                return False
            
            # Update stock
            cursor.execute("""
                UPDATE products
                SET stock = ?,
                    updated_at = ?
                WHERE id = ?
            """, (new_stock, now, product_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Get products with stock below threshold"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, name, description, price, stock, category, barcode, 
                    created_at, updated_at
                FROM products
                WHERE stock <= ?
                ORDER BY stock ASC
            """, (threshold,))
            
            rows = cursor.fetchall()
            
            return [{
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "stock": row[4],
                "category": row[5],
                "barcode": row[6],
                "created_at": row[7],
                "updated_at": row[8]
            } for row in rows]