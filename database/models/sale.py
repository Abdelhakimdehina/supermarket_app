from typing import Optional, List, Dict, Any
import sqlite3
from datetime import datetime
import uuid

class SaleItem:
    """Sale item model class"""
    
    def __init__(self, id: Optional[int] = None, sale_id: Optional[int] = None,
                 product_id: int = 0, quantity: int = 0, unit_price: float = 0.0,
                 discount_percent: float = 0.0, subtotal: float = 0.0):
        self.id = id
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_percent = discount_percent
        self.subtotal = subtotal
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaleItem':
        """Create a SaleItem instance from a dictionary"""
        return cls(
            id=data.get('id'),
            sale_id=data.get('sale_id'),
            product_id=data.get('product_id', 0),
            quantity=data.get('quantity', 0),
            unit_price=data.get('unit_price', 0.0),
            discount_percent=data.get('discount_percent', 0.0),
            subtotal=data.get('subtotal', 0.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SaleItem instance to a dictionary"""
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount_percent': self.discount_percent,
            'subtotal': self.subtotal
        }


class Sale:
    """Sale model class"""
    
    def __init__(self, id: Optional[int] = None, invoice_number: str = "",
                 customer_id: Optional[int] = None, user_id: int = 0,
                 total_amount: float = 0.0, discount_amount: float = 0.0,
                 tax_amount: float = 0.0, payment_method: str = "",
                 payment_status: str = "pending", sale_date: Optional[str] = None,
                 items: Optional[List[SaleItem]] = None):
        self.id = id
        self.invoice_number = invoice_number or self._generate_invoice_number()
        self.customer_id = customer_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.sale_date = sale_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.items = items or []
    
    @staticmethod
    def _generate_invoice_number() -> str:
        """Generate a unique invoice number"""
        prefix = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4().int)[:6]
        return f"INV-{prefix}-{unique_id}"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], include_items: bool = False) -> 'Sale':
        """Create a Sale instance from a dictionary"""
        sale = cls(
            id=data.get('id'),
            invoice_number=data.get('invoice_number', ''),
            customer_id=data.get('customer_id'),
            user_id=data.get('user_id', 0),
            total_amount=data.get('total_amount', 0.0),
            discount_amount=data.get('discount_amount', 0.0),
            tax_amount=data.get('tax_amount', 0.0),
            payment_method=data.get('payment_method', ''),
            payment_status=data.get('payment_status', 'pending'),
            sale_date=data.get('sale_date')
        )
        
        if include_items and sale.id:
            sale.items = sale.get_items()
        
        return sale
    
    def to_dict(self, include_items: bool = False) -> Dict[str, Any]:
        """Convert Sale instance to a dictionary"""
        sale_dict = {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'total_amount': self.total_amount,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'sale_date': self.sale_date
        }
        
        if include_items:
            sale_dict['items'] = [item.to_dict() for item in self.items]
        
        return sale_dict
    
    @classmethod
    def get_by_id(cls, sale_id: int, include_items: bool = False) -> Optional['Sale']:
        """Get a sale by ID"""
        from database.db_manager import DBManager
        
        db = DBManager()
        result = db.execute_query(
            "SELECT * FROM sales WHERE id = ?",
            (sale_id,)
        )
        
        if result and len(result) > 0:
            sale = cls.from_dict(result[0])
            
            if include_items:
                sale.items = sale.get_items()
            
            return sale
        return None
    
    @classmethod
    def get_by_invoice(cls, invoice_number: str, include_items: bool = False) -> Optional['Sale']:
        """Get a sale by invoice number"""
        from database.db_manager import DBManager
        
        db = DBManager()
        result = db.execute_query(
            "SELECT * FROM sales WHERE invoice_number = ?",
            (invoice_number,)
        )
        
        if result and len(result) > 0:
            sale = cls.from_dict(result[0])
            
            if include_items:
                sale.items = sale.get_items()
            
            return sale
        return None
    
    def get_items(self) -> List[SaleItem]:
        """Get all items for this sale"""
        if not self.id:
            return []
        
        from database.db_manager import DBManager
        
        db = DBManager()
        result = db.execute_query(
            "SELECT * FROM sale_items WHERE sale_id = ?",
            (self.id,)
        )
        
        if result:
            return [SaleItem.from_dict(item) for item in result]
        return []
    
    def save(self) -> bool:
        """Save the sale to the database"""
        from database.db_manager import DBManager
        
        db = DBManager()
        
        if self.id:
            # Update existing sale
            try:
                db.execute_query(
                    """
                    UPDATE sales SET 
                    invoice_number = ?, customer_id = ?, user_id = ?,
                    total_amount = ?, discount_amount = ?, tax_amount = ?,
                    payment_method = ?, payment_status = ?, sale_date = ?
                    WHERE id = ?
                    """,
                    (
                        self.invoice_number, self.customer_id, self.user_id,
                        self.total_amount, self.discount_amount, self.tax_amount,
                        self.payment_method, self.payment_status, self.sale_date,
                        self.id
                    )
                )
                return True
            except sqlite3.Error:
                return False
        else:
            # Insert new sale
            try:
                result = db.execute_query(
                    """
                    INSERT INTO sales (
                        invoice_number, customer_id, user_id, total_amount,
                        discount_amount, tax_amount, payment_method, payment_status, sale_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                    """,
                    (
                        self.invoice_number, self.customer_id, self.user_id,
                        self.total_amount, self.discount_amount, self.tax_amount,
                        self.payment_method, self.payment_status, self.sale_date
                    )
                )
                
                if result and len(result) > 0:
                    self.id = result[0]['id']
                    
                    # Save sale items
                    for item in self.items:
                        item.sale_id = self.id
                        self._save_sale_item(item)
                    
                    return True
                return False
            except sqlite3.Error:
                return False
    
    def _save_sale_item(self, item: SaleItem) -> bool:
        """Save a sale item to the database"""
        from database.db_manager import DBManager
        
        db = DBManager()
        
        if item.id:
            # Update existing sale item
            try:
                db.execute_query(
                    """
                    UPDATE sale_items SET 
                    sale_id = ?, product_id = ?, quantity = ?,
                    unit_price = ?, discount_percent = ?, subtotal = ?
                    WHERE id = ?
                    """,
                    (
                        item.sale_id, item.product_id, item.quantity,
                        item.unit_price, item.discount_percent, item.subtotal,
                        item.id
                    )
                )
                return True
            except sqlite3.Error:
                return False
        else:
            # Insert new sale item
            try:
                result = db.execute_query(
                    """
                    INSERT INTO sale_items (
                        sale_id, product_id, quantity, unit_price,
                        discount_percent, subtotal
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    RETURNING id
                    """,
                    (
                        item.sale_id, item.product_id, item.quantity,
                        item.unit_price, item.discount_percent, item.subtotal
                    )
                )
                
                if result and len(result) > 0:
                    item.id = result[0]['id']
                    return True
                return False
            except sqlite3.Error:
                return False