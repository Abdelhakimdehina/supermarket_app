import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import DATABASE_PATH
from services.product_service import ProductService

class SaleService:
    """Service for managing sales"""
    
    def __init__(self):
        """Initialize the service"""
        self.db_path = DATABASE_PATH
        self.product_service = ProductService()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_sale(self, sale_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new sale"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Start transaction
                cursor.execute("BEGIN TRANSACTION")
                
                # Insert sale record
                cursor.execute("""
                    INSERT INTO sales (
                        payment_method, subtotal, tax, total,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, DATETIME('now'), DATETIME('now'))
                """, (
                    sale_data["payment_method"],
                    sale_data["subtotal"],
                    sale_data["tax"],
                    sale_data["total"]
                ))
                
                sale_id = cursor.lastrowid
                
                # Insert sale items and update stock
                for item in sale_data["items"]:
                    # Insert sale item
                    cursor.execute("""
                        INSERT INTO sale_items (
                            sale_id, product_id, quantity, price,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, DATETIME('now'), DATETIME('now'))
                    """, (
                        sale_id,
                        item["product_id"],
                        item["quantity"],
                        item["price"]
                    ))
                    
                    # Update product stock
                    cursor.execute("""
                        UPDATE products
                        SET stock = stock - ?,
                            updated_at = DATETIME('now')
                        WHERE id = ? AND stock >= ?
                    """, (
                        item["quantity"],
                        item["product_id"],
                        item["quantity"]
                    ))
                    
                    if cursor.rowcount == 0:
                        # Not enough stock
                        raise Exception(f"Not enough stock for product {item['product_id']}")
                
                # Commit transaction
                conn.commit()
                
                # Return created sale
                return self.get_sale(sale_id)
                
            except Exception as e:
                # Rollback transaction on error
                conn.rollback()
                print(f"Error creating sale: {e}")
                return None
    
    def get_sale(self, sale_id: int) -> Optional[Dict[str, Any]]:
        """Get a sale by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get sale
            cursor.execute("""
                SELECT 
                    id, payment_method, subtotal, tax, total,
                    created_at, updated_at
                FROM sales
                WHERE id = ?
            """, (sale_id,))
            
            sale_row = cursor.fetchone()
            if not sale_row:
                return None
            
            # Get sale items
            cursor.execute("""
                SELECT 
                    si.product_id, p.name, si.quantity, si.price,
                    si.created_at, si.updated_at
                FROM sale_items si
                JOIN products p ON p.id = si.product_id
                WHERE si.sale_id = ?
            """, (sale_id,))
            
            items = [{
                "product_id": row[0],
                "product_name": row[1],
                "quantity": row[2],
                "price": float(row[3]),
                "created_at": row[4],
                "updated_at": row[5]
            } for row in cursor.fetchall()]
            
            return {
                "id": sale_row[0],
                "payment_method": sale_row[1],
                "subtotal": float(sale_row[2]),
                "tax": float(sale_row[3]),
                "total": float(sale_row[4]),
                "created_at": sale_row[5],
                "updated_at": sale_row[6],
                "items": items
            }
    
    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get sales within date range"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, payment_method, subtotal, tax, total,
                    created_at, updated_at
                FROM sales
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            sales = []
            
            for row in cursor.fetchall():
                sale_id = row[0]
                
                # Get sale items
                cursor.execute("""
                    SELECT 
                        si.product_id, p.name, si.quantity, si.price,
                        si.created_at, si.updated_at
                    FROM sale_items si
                    JOIN products p ON p.id = si.product_id
                    WHERE si.sale_id = ?
                """, (sale_id,))
                
                items = [{
                    "product_id": item_row[0],
                    "product_name": item_row[1],
                    "quantity": item_row[2],
                    "price": float(item_row[3]),
                    "created_at": item_row[4],
                    "updated_at": item_row[5]
                } for item_row in cursor.fetchall()]
                
                sales.append({
                    "id": row[0],
                    "payment_method": row[1],
                    "subtotal": float(row[2]),
                    "tax": float(row[3]),
                    "total": float(row[4]),
                    "created_at": row[5],
                    "updated_at": row[6],
                    "items": items
                })
            
            return sales
    
    def get_daily_sales_total(self, date: Optional[datetime] = None) -> float:
        """Get total sales for a day"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if date:
                date_str = date.strftime("%Y-%m-%d")
            else:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0)
                FROM sales
                WHERE DATE(created_at) = DATE(?)
            """, (date_str,))
            
            return float(cursor.fetchone()[0])
    
    def get_monthly_sales_total(self, year: int, month: int) -> float:
        """Get total sales for a month"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0)
                FROM sales
                WHERE strftime('%Y', created_at) = ?
                AND strftime('%m', created_at) = ?
            """, (str(year), str(month).zfill(2)))
            
            return float(cursor.fetchone()[0])
    
    def get_sales_by_payment_method(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get sales totals grouped by payment method"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total) as total
                FROM sales
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND created_at >= ?"
                params.append(start_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            if end_date:
                query += " AND created_at <= ?"
                params.append(end_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            query += " GROUP BY payment_method"
            
            cursor.execute(query, params)
            
            return [{
                "payment_method": row[0],
                "count": row[1],
                "total": float(row[2])
            } for row in cursor.fetchall()]