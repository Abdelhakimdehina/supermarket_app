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
                
                # Generate invoice number
                invoice_number = self._generate_invoice_number()
                
                # Insert sale record
                cursor.execute("""
                    INSERT INTO sales (
                        invoice_number, customer_id, user_id,
                        total_amount, discount_amount, tax_amount,
                        payment_method, payment_status, sale_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'))
                """, (
                    invoice_number,
                    sale_data.get("customer_id"),
                    sale_data["user_id"],
                    sale_data["total"],
                    sale_data.get("discount", 0.0),
                    sale_data["tax"],
                    sale_data["payment_method"],
                    "completed",  # Default status
                ))
                
                sale_id = cursor.lastrowid
                
                # Insert sale items and update stock
                for item in sale_data["items"]:
                    # Get current stock
                    cursor.execute("""
                        SELECT stock_quantity
                        FROM products
                        WHERE id = ? AND stock_quantity >= ?
                    """, (
                        item["product_id"],
                        item["quantity"]
                    ))
                    
                    row = cursor.fetchone()
                    if not row:
                        raise Exception(f"Not enough stock for product {item['product_id']}")
                    
                    current_stock = row[0]
                    new_stock = current_stock - item["quantity"]
                    
                    # Insert sale item
                    cursor.execute("""
                        INSERT INTO sale_items (
                            sale_id, product_id, quantity,
                            unit_price, discount_percent, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        sale_id,
                        item["product_id"],
                        item["quantity"],
                        item["price"],
                        item.get("discount_percent", 0.0),
                        item["quantity"] * item["price"]
                    ))
                    
                    # Update product stock
                    cursor.execute("""
                        UPDATE products
                        SET stock_quantity = ?,
                            updated_at = DATETIME('now')
                        WHERE id = ?
                    """, (
                        new_stock,
                        item["product_id"]
                    ))
                    
                    # Record inventory transaction
                    cursor.execute("""
                        INSERT INTO inventory_transactions (
                            product_id, quantity_change, previous_quantity,
                            new_quantity, transaction_type, reason,
                            notes, user_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item["product_id"],
                        -item["quantity"],  # Negative for sales
                        current_stock,
                        new_stock,
                        'sale',
                        f'Sale #{invoice_number}',
                        None,
                        sale_data["user_id"]
                    ))
                
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
                    id, invoice_number, customer_id, user_id,
                    total_amount, discount_amount, tax_amount,
                    payment_method, payment_status, sale_date
                FROM sales
                WHERE id = ?
            """, (sale_id,))
            
            sale_row = cursor.fetchone()
            if not sale_row:
                return None
            
            # Get sale items
            cursor.execute("""
                SELECT 
                    si.product_id, p.name, si.quantity, si.unit_price,
                    si.discount_percent, si.subtotal
                FROM sale_items si
                JOIN products p ON p.id = si.product_id
                WHERE si.sale_id = ?
            """, (sale_id,))
            
            items = [{
                "product_id": row[0],
                "product_name": row[1],
                "quantity": row[2],
                "price": float(row[3]),
                "discount_percent": float(row[4]),
                "subtotal": float(row[5])
            } for row in cursor.fetchall()]
            
            return {
                "id": sale_row[0],
                "invoice_number": sale_row[1],
                "customer_id": sale_row[2],
                "user_id": sale_row[3],
                "total": float(sale_row[4]),
                "discount": float(sale_row[5]),
                "tax": float(sale_row[6]),
                "payment_method": sale_row[7],
                "payment_status": sale_row[8],
                "sale_date": sale_row[9],
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
                    id, invoice_number, customer_id, user_id,
                    total_amount, discount_amount, tax_amount,
                    payment_method, payment_status, sale_date
                FROM sales
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND sale_date >= ?"
                params.append(start_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            if end_date:
                query += " AND sale_date <= ?"
                params.append(end_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            query += " ORDER BY sale_date DESC"
            
            cursor.execute(query, params)
            sales = []
            
            for row in cursor.fetchall():
                sale_id = row[0]
                
                # Get sale items
                cursor.execute("""
                    SELECT 
                        si.product_id, p.name, si.quantity, si.unit_price,
                        si.discount_percent, si.subtotal
                    FROM sale_items si
                    JOIN products p ON p.id = si.product_id
                    WHERE si.sale_id = ?
                """, (sale_id,))
                
                items = [{
                    "product_id": item_row[0],
                    "product_name": item_row[1],
                    "quantity": item_row[2],
                    "price": float(item_row[3]),
                    "discount_percent": float(item_row[4]),
                    "subtotal": float(item_row[5])
                } for item_row in cursor.fetchall()]
                
                sales.append({
                    "id": row[0],
                    "invoice_number": row[1],
                    "customer_id": row[2],
                    "user_id": row[3],
                    "total": float(row[4]),
                    "discount": float(row[5]),
                    "tax": float(row[6]),
                    "payment_method": row[7],
                    "payment_status": row[8],
                    "sale_date": row[9],
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
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales
                WHERE DATE(sale_date) = DATE(?)
            """, (date_str,))
            
            return float(cursor.fetchone()[0])
    
    def get_monthly_sales_total(self, year: int, month: int) -> float:
        """Get total sales for a month"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales
                WHERE strftime('%Y', sale_date) = ?
                AND strftime('%m', sale_date) = ?
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
                    SUM(total_amount) as total
                FROM sales
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND sale_date >= ?"
                params.append(start_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            if end_date:
                query += " AND sale_date <= ?"
                params.append(end_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            query += " GROUP BY payment_method"
            
            cursor.execute(query, params)
            
            return [{
                "payment_method": row[0],
                "count": row[1],
                "total": float(row[2])
            } for row in cursor.fetchall()]
    
    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number"""
        prefix = datetime.now().strftime('%Y%m%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the last invoice number for today
            cursor.execute("""
                SELECT invoice_number
                FROM sales
                WHERE DATE(sale_date) = DATE('now')
                ORDER BY invoice_number DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                # Extract sequence number and increment
                last_number = int(row[0].split('-')[-1])
                sequence = str(last_number + 1).zfill(4)
            else:
                # Start with 0001
                sequence = '0001'
            
            return f"INV-{prefix}-{sequence}"