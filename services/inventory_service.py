import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import DATABASE_PATH

class InventoryService:
    """Service for managing inventory"""
    
    def __init__(self):
        """Initialize the service"""
        self.db_path = DATABASE_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, name, description, category, barcode,
                    price, cost_price, stock_quantity, reorder_level,
                    image_path, is_active, created_at, updated_at
                FROM products
                WHERE is_active = 1
                ORDER BY name
            """)
            
            return [{
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "category": row[3],
                "barcode": row[4],
                "price": float(row[5]),
                "cost_price": float(row[6]),
                "stock": int(row[7]),  # Alias for backward compatibility
                "stock_quantity": int(row[7]),
                "reorder_level": int(row[8]),
                "image_path": row[9],
                "is_active": bool(row[10]),
                "created_at": row[11],
                "updated_at": row[12]
            } for row in cursor.fetchall()]
    
    def search_products(self, search_term: str) -> List[Dict[str, Any]]:
        """Search products by name, description, or barcode"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{search_term}%"
            
            cursor.execute("""
                SELECT id, name, description, barcode, category,
                       price, stock, created_at, updated_at
                FROM products
                WHERE is_active = 1
                AND (name LIKE ? OR description LIKE ? OR barcode LIKE ?)
                ORDER BY name
            """, (search_pattern, search_pattern, search_pattern))
            
            return [{
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "barcode": row[3],
                "category": row[4],
                "price": float(row[5]),
                "stock": int(row[6]),
                "created_at": row[7],
                "updated_at": row[8]
            } for row in cursor.fetchall()]
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a single product by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, barcode, category,
                       price, stock, created_at, updated_at
                FROM products
                WHERE id = ? AND is_active = 1
            """, (product_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "barcode": row[3],
                "category": row[4],
                "price": float(row[5]),
                "stock": int(row[6]),
                "created_at": row[7],
                "updated_at": row[8]
            }
    
    def add_product(self, product_data: Dict[str, Any]) -> bool:
        """Add a new product"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO products (
                        name, description, category, barcode,
                        price, cost_price, stock_quantity, reorder_level,
                        image_path, is_active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, DATETIME('now'), DATETIME('now'))
                """, (
                    product_data.get('name', ''),
                    product_data.get('description', ''),
                    product_data.get('category', ''),
                    product_data.get('barcode', ''),
                    product_data.get('price', 0.0),
                    product_data.get('cost_price', 0.0),
                    product_data.get('stock_quantity', 0),
                    product_data.get('reorder_level', 10),
                    product_data.get('image_path', '')
                ))
                
                conn.commit()
                return True
                
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return False
    
    def update_product(self, product_data: Dict[str, Any]) -> bool:
        """Update an existing product"""
        with self.get_connection() as conn:
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
                    product_data['id']
                ))
                
                conn.commit()
                return True
                
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return False
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product"""
        with self.get_connection() as conn:
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
                return False
    
    def adjust_stock(self, product_id: int, quantity_change: int, reason: str = "") -> bool:
        """Adjust product stock quantity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Get current stock
                cursor.execute("""
                    SELECT stock_quantity 
                    FROM products 
                    WHERE id = ? AND is_active = 1
                """, (product_id,))
                
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
                return False 