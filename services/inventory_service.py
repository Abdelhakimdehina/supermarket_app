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
                    p.id, p.name, p.description, p.category, p.barcode,
                    p.price, p.cost_price, p.stock_quantity, p.reorder_level,
                    p.image_path, p.is_active, p.created_at, p.updated_at,
                    COALESCE(SUM(si.subtotal), 0) as total_sales
                FROM products p
                LEFT JOIN sale_items si ON p.id = si.product_id
                WHERE p.is_active = 1
                GROUP BY p.id
                ORDER BY p.name
            """)
            products = [{
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
                "low_stock_threshold": int(row[8]),  # Alias for backward compatibility
                "image_path": row[9],
                "is_active": bool(row[10]),
                "created_at": row[11],
                "updated_at": row[12],
                "last_updated": row[12],  # Alias for backward compatibility
                "total_sales": float(row[13])
            } for row in cursor.fetchall()]
            return products
    
    def search_products(self, search_term: str) -> List[Dict[str, Any]]:
        """Search products by name, description, or barcode"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{search_term}%"
            
            cursor.execute("""
                SELECT id, name, description, barcode, category,
                       price, stock_quantity, created_at, updated_at
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
                "stock": int(row[6]),  # Alias for backward compatibility
                "stock_quantity": int(row[6]),
                "created_at": row[7],
                "updated_at": row[8],
                "last_updated": row[8]  # Alias for backward compatibility
            } for row in cursor.fetchall()]
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a single product by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, barcode, category,
                       price, stock_quantity, created_at, updated_at
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
                "stock": int(row[6]),  # Alias for backward compatibility
                "stock_quantity": int(row[6]),
                "created_at": row[7],
                "updated_at": row[8],
                "last_updated": row[8]  # Alias for backward compatibility
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
                return False

    def update_product(self, product_data: Dict[str, Any]) -> bool:
        """Update an existing product with correct field mapping"""
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
                    product_data.get('stock_quantity', product_data.get('stock', 0)),
                    product_data.get('reorder_level', 10),
                    product_data.get('image_path', ''),
                    product_data['id']
                ))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
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
    
    def adjust_stock(self, product_id: int, quantity_change: int, reason: str = "", notes: str = "", user_id: Optional[int] = None) -> bool:
        """Adjust product stock quantity and record the transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Start transaction
                cursor.execute("BEGIN TRANSACTION")
                
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
                
                # Record transaction
                cursor.execute("""
                    INSERT INTO inventory_transactions (
                        product_id, quantity_change, previous_quantity,
                        new_quantity, transaction_type, reason,
                        notes, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    quantity_change,
                    current_stock,
                    new_stock,
                    'manual' if abs(quantity_change) > 0 else 'correction',
                    reason,
                    notes,
                    user_id
                ))
                
                # Commit transaction
                conn.commit()
                return True
                
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                conn.rollback()
                return False
    
    def get_product_transactions(self, product_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history for a product"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id, t.quantity_change, t.previous_quantity,
                    t.new_quantity, t.transaction_type, t.reason,
                    t.notes, t.created_at,
                    u.username as user_name
                FROM inventory_transactions t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.product_id = ?
                ORDER BY t.created_at DESC
                LIMIT ?
            """, (product_id, limit))
            
            return [{
                "id": row[0],
                "quantity_change": row[1],
                "previous_quantity": row[2],
                "new_quantity": row[3],
                "transaction_type": row[4],
                "reason": row[5],
                "notes": row[6],
                "created_at": row[7],
                "user_name": row[8] if row[8] else "System"
            } for row in cursor.fetchall()]
    
    def get_recent_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent inventory transactions across all products"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id, t.quantity_change, t.previous_quantity,
                    t.new_quantity, t.transaction_type, t.reason,
                    t.notes, t.created_at,
                    p.name as product_name,
                    u.username as user_name
                FROM inventory_transactions t
                JOIN products p ON t.product_id = p.id
                LEFT JOIN users u ON t.user_id = u.id
                ORDER BY t.created_at DESC
                LIMIT ?
            """, (limit,))
            
            return [{
                "id": row[0],
                "quantity_change": row[1],
                "previous_quantity": row[2],
                "new_quantity": row[3],
                "transaction_type": row[4],
                "reason": row[5],
                "notes": row[6],
                "created_at": row[7],
                "product_name": row[8],
                "user_name": row[9] if row[9] else "System"
            } for row in cursor.fetchall()]