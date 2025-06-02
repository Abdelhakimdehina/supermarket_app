from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlite3

from database.db_manager import DBManager

class ReportsService:
    """Service for generating various reports"""
    
    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get sales summary for the given period"""
        db = DBManager()
        try:
            # Default to current month if no dates provided
            if not start_date:
                today = datetime.now()
                start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
            
            # Get sales summary
            result = db.execute_query("""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(total_amount) as total_revenue,
                    SUM(discount_amount) as total_discounts,
                    SUM(tax_amount) as total_tax,
                    AVG(total_amount) as average_sale,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
            """, (start_date, end_date))
            
            summary = result[0] if result else {}
            
            # Get payment method breakdown
            payment_methods = db.execute_query("""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
                GROUP BY payment_method
            """, (start_date, end_date))
            
            # Get hourly sales distribution
            hourly_sales = db.execute_query("""
                SELECT 
                    strftime('%H', sale_date) as hour,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
                GROUP BY hour
                ORDER BY hour
            """, (start_date, end_date))
            
            return {
                'summary': summary,
                'payment_methods': payment_methods,
                'hourly_sales': hourly_sales
            }
        finally:
            db.close()
    
    def get_top_products(self, limit: int = 10, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get top selling products"""
        db = DBManager()
        try:
            # Default to current month
            if not start_date:
                today = datetime.now()
                start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
            
            return db.execute_query("""
                SELECT 
                    p.id,
                    p.name,
                    p.category,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.subtotal) as total_revenue,
                    COUNT(DISTINCT s.id) as times_sold
                FROM products p
                JOIN sale_items si ON p.id = si.product_id
                JOIN sales s ON si.sale_id = s.id
                WHERE s.sale_date BETWEEN ? AND ?
                GROUP BY p.id
                ORDER BY total_quantity DESC
                LIMIT ?
            """, (start_date, end_date, limit))
        finally:
            db.close()
    
    def get_inventory_status(self) -> Dict[str, Any]:
        """Get inventory status report"""
        db = DBManager()
        try:
            # Get low stock items
            low_stock = db.execute_query("""
                SELECT 
                    id, name, category, stock_quantity, reorder_level,
                    price, cost_price
                FROM products
                WHERE stock_quantity <= reorder_level
                ORDER BY (stock_quantity * 1.0 / reorder_level)
            """)
            
            # Get category summary
            categories = db.execute_query("""
                SELECT 
                    category,
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_stock,
                    SUM(stock_quantity * price) as stock_value
                FROM products
                GROUP BY category
            """)
            
            # Get overall summary
            summary = db.execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_stock,
                    SUM(stock_quantity * price) as total_stock_value,
                    COUNT(CASE WHEN stock_quantity <= reorder_level THEN 1 END) as low_stock_count
                FROM products
            """)[0]
            
            return {
                'low_stock': low_stock,
                'categories': categories,
                'summary': summary
            }
        finally:
            db.close()
    
    def get_customer_analytics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get customer analytics"""
        db = DBManager()
        try:
            # Default to current month
            if not start_date:
                today = datetime.now()
                start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
            
            # Get top customers
            top_customers = db.execute_query("""
                SELECT 
                    c.id,
                    c.name,
                    COUNT(s.id) as visit_count,
                    SUM(s.total_amount) as total_spent,
                    AVG(s.total_amount) as average_purchase,
                    MAX(s.sale_date) as last_visit,
                    c.loyalty_points
                FROM customers c
                JOIN sales s ON c.id = s.customer_id
                WHERE s.sale_date BETWEEN ? AND ?
                GROUP BY c.id
                ORDER BY total_spent DESC
                LIMIT 10
            """, (start_date, end_date))
            
            # Get customer segments
            segments = db.execute_query("""
                WITH customer_stats AS (
                    SELECT 
                        c.id,
                        COUNT(s.id) as visit_count,
                        SUM(s.total_amount) as total_spent,
                        AVG(s.total_amount) as average_purchase
                    FROM customers c
                    LEFT JOIN sales s ON c.id = s.customer_id
                    WHERE s.sale_date BETWEEN ? AND ?
                    GROUP BY c.id
                )
                SELECT 
                    CASE 
                        WHEN total_spent > 1000 THEN 'VIP'
                        WHEN total_spent > 500 THEN 'Regular'
                        WHEN total_spent > 100 THEN 'Occasional'
                        ELSE 'New'
                    END as segment,
                    COUNT(*) as customer_count,
                    SUM(total_spent) as segment_revenue,
                    AVG(visit_count) as avg_visits
                FROM customer_stats
                GROUP BY segment
            """, (start_date, end_date))
            
            # Get overall summary
            summary = db.execute_query("""
                SELECT 
                    COUNT(DISTINCT customer_id) as active_customers,
                    COUNT(DISTINCT CASE WHEN customer_id IS NULL THEN s.id END) as guest_transactions,
                    AVG(total_amount) as average_transaction,
                    SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
                FROM sales s
                WHERE sale_date BETWEEN ? AND ?
            """, (start_date, end_date))[0]
            
            return {
                'top_customers': top_customers,
                'segments': segments,
                'summary': summary
            }
        finally:
            db.close()
    
    def get_daily_report(self, date: str = None) -> Dict[str, Any]:
        """Get comprehensive daily report"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        end_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')
        
        return {
            'sales': self.get_sales_summary(date, end_date),
            'top_products': self.get_top_products(5, date, end_date),
            'inventory': self.get_inventory_status(),
            'customers': self.get_customer_analytics(date, end_date)
        } 