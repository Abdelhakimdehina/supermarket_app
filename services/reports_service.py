from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlite3

from config.settings import DATABASE_PATH

class ReportsService:
    """Service for generating various reports"""
    
    def get_connection(self):
        return sqlite3.connect(DATABASE_PATH)

    def get_sales_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get sales summary for the given period"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Default to current month if no dates provided
            if not start_date:
                today = datetime.now()
                start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
            
            # Get sales summary
            cursor.execute("""
                SELECT 
                    COALESCE(COUNT(*), 0) as total_sales,
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    COALESCE(SUM(discount_amount), 0) as total_discounts,
                    COALESCE(SUM(tax_amount), 0) as total_tax,
                    COALESCE(AVG(total_amount), 0) as average_sale,
                    COALESCE(COUNT(DISTINCT customer_id), 0) as unique_customers
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
            """, (start_date, end_date))
            
            result = cursor.fetchall()
            summary_row = result[0] if result else [0, 0, 0, 0, 0, 0]

            summary = {
                'total_sales': summary_row[0],
                'total_revenue': summary_row[1],
                'total_discounts': summary_row[2],
                'total_tax': summary_row[3],
                'average_sale': summary_row[4],
                'unique_customers': summary_row[5]
            }
            
            # Get payment method breakdown
            cursor.execute("""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
                GROUP BY payment_method
            """, (start_date, end_date))
            
            payment_methods = [{
                'payment_method': row[0],
                'count': row[1],
                'total': row[2]
            } for row in cursor.fetchall()]

            # Get hourly sales distribution
            cursor.execute("""
                SELECT 
                    strftime('%H', sale_date) as hour,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
                GROUP BY hour
                ORDER BY hour
            """, (start_date, end_date))
            
            hourly_sales = [{
                'hour': row[0],
                'count': row[1],
                'total': row[2]
            } for row in cursor.fetchall()]

        return {
            'summary': summary,
            'payment_methods': payment_methods,
            'hourly_sales': hourly_sales
        }
    
    def get_top_products(self, limit: int = 10, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get top selling products"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Default to current month
            if not start_date:
                today = datetime.now()
                start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
            
            cursor.execute("""
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
            return [{
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'total_quantity': row[3],
                'total_revenue': row[4],
                'times_sold': row[5]
            } for row in cursor.fetchall()]
    
    def get_inventory_status(self) -> Dict[str, Any]:
        """Get inventory status report"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Get low stock items
            cursor.execute("""
                SELECT 
                    id, name, category, stock_quantity, reorder_level,
                    price, cost_price
                FROM products
                WHERE stock_quantity <= reorder_level
                ORDER BY (stock_quantity * 1.0 / reorder_level)
            """)
            low_stock = [{
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'stock_quantity': row[3],
                'reorder_level': row[4],
                'price': row[5],
                'cost_price': row[6]
            } for row in cursor.fetchall()]
            
            # Get category summary
            cursor.execute("""
                SELECT 
                    category,
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_stock,
                    SUM(stock_quantity * price) as stock_value
                FROM products
                GROUP BY category
            """)
            categories = [{
                'category': row[0],
                'total_products': row[1],
                'total_stock': row[2],
                'stock_value': row[3]
            } for row in cursor.fetchall()]
            
            # Get overall summary
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(stock_quantity) as total_stock,
                    SUM(stock_quantity * price) as total_stock_value,
                    COUNT(CASE WHEN stock_quantity <= reorder_level THEN 1 END) as low_stock_count
                FROM products
            """)
            summary = cursor.fetchone()

            return {
                'low_stock': low_stock,
                'categories': categories,
                'summary': {
                    'total_products': summary[0],
                    'total_stock': summary[1],
                    'total_stock_value': summary[2],
                    'low_stock_count': summary[3]
                }
            }
    
    def get_customer_analytics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get customer analytics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Default to current month
            if not start_date:
                today = datetime.now()
                start_date = datetime(today.year, today.month, 1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
            
            # Get top customers
            cursor.execute("""
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
            top_customers = [{
                'id': row[0],
                'name': row[1],
                'visit_count': row[2],
                'total_spent': row[3],
                'average_purchase': row[4],
                'last_visit': row[5],
                'loyalty_points': row[6]
            } for row in cursor.fetchall()]
            
            # Get customer segments
            cursor.execute("""
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
            segments = [{
                'segment': row[0],
                'customer_count': row[1],
                'segment_revenue': row[2],
                'avg_visits': row[3]
            } for row in cursor.fetchall()]
            
            # Get overall summary
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT customer_id) as active_customers,
                    COUNT(DISTINCT CASE WHEN customer_id IS NULL THEN s.id END) as guest_transactions,
                    AVG(total_amount) as average_transaction,
                    CASE 
                        WHEN COUNT(DISTINCT customer_id) > 0 THEN SUM(total_amount) / COUNT(DISTINCT customer_id)
                        ELSE 0 
                    END as revenue_per_customer
                FROM sales s
                WHERE sale_date BETWEEN ? AND ?
            """, (start_date, end_date))
            summary_row = cursor.fetchone()
            summary = {
                'active_customers': summary_row[0],
                'guest_transactions': summary_row[1],
                'average_transaction': summary_row[2],
                'revenue_per_customer': summary_row[3]
            }

            return {
                'top_customers': top_customers,
                'segments': segments,
                'summary': summary
            }
    
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