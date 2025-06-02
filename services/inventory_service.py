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
                SELECT id, name, description, barcode, category,
                       price, stock, created_at, updated_at
                FROM products
                WHERE is_active = 1
                ORDER BY name
            """)
            
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
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO products (
                        name, description, barcode, category,
                        price, stock, is_active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                """, (
                    product_data["name"],
                    product_data.get("description", ""),
                    product_data.get("barcode", ""),
                    product_data["category"],
                    float(product_data["price"]),
                    int(product_data.get("stock", 0)),
                    now, now
                ))
                conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error adding product: {e}")
                return False
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Update an existing product"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    UPDATE products
                    SET name = ?,
                        description = ?,
                        barcode = ?,
                        category = ?,
                        price = ?,
                        stock = ?,
                        updated_at = ?
                    WHERE id = ? AND is_active = 1
                """, (
                    product_data["name"],
                    product_data.get("description", ""),
                    product_data.get("barcode", ""),
                    product_data["category"],
                    float(product_data["price"]),
                    int(product_data["stock"]),
                    now,
                    product_id
                ))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error updating product: {e}")
                return False
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    UPDATE products
                    SET is_active = 0,
                        updated_at = ?
                    WHERE id = ? AND is_active = 1
                """, (now, product_id))
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error deleting product: {e}")
                return False
    
    def adjust_stock(self, product_id: int, quantity: int) -> bool:
        """Adjust product stock (positive for additions, negative for removals)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # First check if adjustment would result in negative stock
                cursor.execute("""
                    SELECT stock FROM products
                    WHERE id = ? AND is_active = 1
                """, (product_id,))
                
                current_stock = cursor.fetchone()
                if not current_stock or current_stock[0] + quantity < 0:
                    return False
                
                # Update stock
                cursor.execute("""
                    UPDATE products
                    SET stock = stock + ?,
                        updated_at = ?
                    WHERE id = ? AND is_active = 1
                """, (quantity, now, product_id))
                
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error adjusting stock: {e}")
                return False 