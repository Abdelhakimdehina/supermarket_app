from typing import Optional, List, Dict, Any
import sqlite3
from datetime import datetime

class Product:
    """Product model class"""
    
    def __init__(self, id: Optional[int] = None, name: str = "", description: str = "", 
                 category: str = "", barcode: str = "", price: float = 0.0,
                 cost_price: float = 0.0, stock_quantity: int = 0,
                 reorder_level: int = 10, image_path: str = "", is_active: bool = True, 
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.barcode = barcode
        self.price = price
        self.cost_price = cost_price
        self.stock_quantity = stock_quantity
        self.reorder_level = reorder_level
        self.image_path = image_path
        self.is_active = is_active
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = updated_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Create a Product instance from a dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=data.get('category', ''),
            barcode=data.get('barcode', ''),
            price=data.get('price', 0.0),
            cost_price=data.get('cost_price', 0.0),
            stock_quantity=data.get('stock_quantity', 0),
            reorder_level=data.get('reorder_level', 10),
            image_path=data.get('image_path', ''),
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Product instance to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'barcode': self.barcode,
            'price': self.price,
            'cost_price': self.cost_price,
            'stock_quantity': self.stock_quantity,
            'reorder_level': self.reorder_level,
            'image_path': self.image_path,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def get_by_id(cls, product_id: int) -> Optional['Product']:
        """Get a product by ID"""
        from database.db_manager import DBManager
        
        db = DBManager()
        result = db.execute_query(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )
        
        if result and len(result) > 0:
            return cls.from_dict(result[0])
        return None
    
    @classmethod
    def get_by_barcode(cls, barcode: str) -> Optional['Product']:
        """Get a product by barcode"""
        from database.db_manager import DBManager
        
        db = DBManager()
        result = db.execute_query(
            "SELECT * FROM products WHERE barcode = ?",
            (barcode,)
        )
        
        if result and len(result) > 0:
            return cls.from_dict(result[0])
        return None
    
    @classmethod
    def get_all(cls, active_only: bool = True) -> List['Product']:
        """Get all products"""
        from database.db_manager import DBManager
        
        db = DBManager()
        query = "SELECT * FROM products"
        params = ()
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY name"
        
        result = db.execute_query(query, params)
        
        if result:
            return [cls.from_dict(item) for item in result]
        return []
    
    @classmethod
    def search(cls, search_term: str, category: Optional[str] = None, 
               active_only: bool = True) -> List['Product']:
        """Search for products by name, description, or barcode"""
        from database.db_manager import DBManager
        
        db = DBManager()
        query = """
            SELECT * FROM products 
            WHERE (name LIKE ? OR description LIKE ? OR barcode LIKE ?)
        """
        params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if active_only:
            query += " AND is_active = 1"
        
        query += " ORDER BY name"
        
        result = db.execute_query(query, tuple(params))
        
        if result:
            return [cls.from_dict(item) for item in result]
        return []
    
    def save(self) -> bool:
        """Save the product to the database"""
        from database.db_manager import DBManager
        
        db = DBManager()
        self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if self.id:
            # Update existing product
            try:
                db.execute_query(
                    """
                    UPDATE products SET 
                    name = ?, description = ?, category = ?, barcode = ?,
                    price = ?, cost_price = ?, stock_quantity = ?, reorder_level = ?,
                    image_path = ?, is_active = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        self.name, self.description, self.category, self.barcode,
                        self.price, self.cost_price, self.stock_quantity, self.reorder_level,
                        self.image_path, 1 if self.is_active else 0, self.updated_at,
                        self.id
                    )
                )
                return True
            except sqlite3.Error:
                return False
        else:
            # Insert new product
            try:
                result = db.execute_query(
                    """
                    INSERT INTO products (
                        name, description, category, barcode, price, cost_price,
                        stock_quantity, reorder_level, image_path, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                    """,
                    (
                        self.name, self.description, self.category, self.barcode,
                        self.price, self.cost_price, self.stock_quantity, self.reorder_level,
                        self.image_path, 1 if self.is_active else 0,
                        self.created_at, self.updated_at
                    )
                )
                
                if result and len(result) > 0:
                    self.id = result[0]['id']
                    return True
                return False
            except sqlite3.Error:
                return False
    
    def update_stock(self, quantity_change: int) -> bool:
        """Update product stock quantity"""
        if not self.id:
            return False
        
        new_quantity = self.stock_quantity + quantity_change
        if new_quantity < 0:
            return False
        
        self.stock_quantity = new_quantity
        return self.save()