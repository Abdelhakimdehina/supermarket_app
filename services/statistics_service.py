import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime, date

from config.settings import DATABASE_PATH, LOW_STOCK_THRESHOLD

class StatisticsService:
    """Service for getting dashboard statistics"""
    
    def __init__(self):
        """Initialize the service"""
        self.db_path = DATABASE_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_today_stats(self) -> Dict[str, Any]:
        """Get today's statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            today = date.today().strftime("%Y-%m-%d")
            
            # Get today's sales total
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales
                WHERE DATE(sale_date) = ?
            """, (today,))
            today_sales = cursor.fetchone()[0]
            
            # Get items sold today
            cursor.execute("""
                SELECT COALESCE(SUM(quantity), 0)
                FROM sale_items si
                JOIN sales s ON s.id = si.sale_id
                WHERE DATE(s.sale_date) = ?
            """, (today,))
            items_sold = cursor.fetchone()[0]
            
            # Get low stock items count using fixed threshold
            cursor.execute("""
                SELECT COUNT(*)
                FROM products
                WHERE stock_quantity <= ?
            """, (LOW_STOCK_THRESHOLD,))
            low_stock = cursor.fetchone()[0]
            
            # Get total customers (for now, just count sales with unique dates)
            cursor.execute("""
                SELECT COUNT(*)
                FROM customers
            """)
            total_customers = cursor.fetchone()[0]
            
            # Get monthly revenue
            current_month = datetime.now().strftime("%Y-%m")
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount), 0)
                FROM sales
                WHERE strftime('%Y-%m', sale_date) = ?
            """, (current_month,))
            monthly_revenue = cursor.fetchone()[0]
            
            # Get pending orders (not implemented yet)
            pending_orders = 0
            
            return {
                "today_sales": float(today_sales),
                "items_sold": int(items_sold),
                "low_stock": int(low_stock),
                "total_customers": int(total_customers),
                "monthly_revenue": float(monthly_revenue),
                "pending_orders": int(pending_orders)
            } 