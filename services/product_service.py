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
                SELECT id, name, description, category, barcode,
                       price, cost_price, stock_quantity, reorder_level,
                       image_path, is_active, created_at, updated_at
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
                query += """ AND (
                    name LIKE ? OR 
                    description LIKE ? OR 
                    barcode LIKE ?
                )"""
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            # Execute query
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            products = []
            for row in rows:
                products.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'barcode': row[4],
                    'price': float(row[5]),
                    'cost_price': float(row[6]),
                    'stock': int(row[7]),
                    'stock_quantity': int(row[7]),
                    'reorder_level': int(row[8]),
                    'image_path': row[9],
                    'is_active': bool(row[10]),
                    'created_at': row[11],
                    'updated_at': row[12]
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
                SELECT id, name, description, category, barcode,
                       price, cost_price, stock_quantity, reorder_level,
                       image_path, is_active, created_at, updated_at
                FROM products
                WHERE id = ?
            """, (product_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category': row[3],
                    'barcode': row[4],
                    'price': float(row[5]),
                    'cost_price': float(row[6]),
                    'stock': int(row[7]),
                    'stock_quantity': int(row[7]),
                    'reorder_level': int(row[8]),
                    'image_path': row[9],
                    'is_active': bool(row[10]),
                    'created_at': row[11],
                    'updated_at': row[12]
                }
            
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO products (
                    name, description, category, barcode,
                    price, cost_price, stock_quantity, reorder_level,
                    image_path, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'), DATETIME('now'))
            """, (
                product_data.get('name', ''),
                product_data.get('description', ''),
                product_data.get('category', ''),
                product_data.get('barcode', ''),
                product_data.get('price', 0.0),
                product_data.get('cost_price', 0.0),
                product_data.get('stock_quantity', 0),
                product_data.get('reorder_level', 10),
                product_data.get('image_path', ''),
                1  # is_active
            ))
            
            conn.commit()
            product_id = cursor.lastrowid
            return self.get_product(product_id)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE products SET
                name = ?, description = ?, category = ?, barcode = ?,
                price = ?, cost_price = ?, stock_quantity = ?, reorder_level = ?,
                image_path = ?, updated_at = DATETIME('now')
                WHERE id = ?
            """, (
                product_data.get('name', ''),
                product_data.get('description', ''),
                product_data.get('category', ''),
                product_data.get('barcode', ''),
                product_data.get('price', 0.0),
                product_data.get('cost_price', 0.0),
                product_data.get('stock_quantity', 0),
                product_data.get('reorder_level', 10),
                product_data.get('image_path', ''),
                product_id
            ))
            
            conn.commit()
            return self.get_product(product_id)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE products SET
                is_active = 0,
                updated_at = DATETIME('now')
                WHERE id = ?
            """, (product_id,))
            
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
            # Get current stock
            cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
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
                UPDATE products SET
                stock_quantity = ?,
                updated_at = DATETIME('now')
                WHERE id = ?
            """, (new_stock, product_id))
            
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