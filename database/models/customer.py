from typing import Optional, List, Dict, Any
import sqlite3
from datetime import datetime

from database.db_manager import DBManager

class Customer:
    """Customer model class"""
    
    def __init__(self, id: Optional[int] = None, name: str = "", phone: str = "",
                 email: str = "", address: str = "", loyalty_points: int = 0,
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.loyalty_points = loyalty_points
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.updated_at = updated_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Customer':
        """Create a Customer instance from a dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            loyalty_points=data.get('loyalty_points', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Customer instance to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'loyalty_points': self.loyalty_points,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def get_by_id(cls, customer_id: int) -> Optional['Customer']:
        """Get a customer by ID"""
        db = DBManager()
        try:
            result = db.execute_query(
                "SELECT * FROM customers WHERE id = ?",
                (customer_id,)
            )
            if result and len(result) > 0:
                return cls.from_dict(result[0])
            return None
        finally:
            db.close()
    
    @classmethod
    def get_by_phone(cls, phone: str) -> Optional['Customer']:
        """Get a customer by phone number"""
        db = DBManager()
        try:
            result = db.execute_query(
                "SELECT * FROM customers WHERE phone = ?",
                (phone,)
            )
            if result and len(result) > 0:
                return cls.from_dict(result[0])
            return None
        finally:
            db.close()
    
    @classmethod
    def get_all(cls) -> List['Customer']:
        """Get all customers"""
        db = DBManager()
        try:
            results = db.execute_query(
                "SELECT * FROM customers ORDER BY name"
            )
            return [cls.from_dict(row) for row in results] if results else []
        finally:
            db.close()
    
    @classmethod
    def search(cls, search_term: str) -> List['Customer']:
        """Search for customers by name, phone, or email"""
        db = DBManager()
        try:
            results = db.execute_query(
                """
                SELECT * FROM customers 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY name
                """,
                (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            )
            return [cls.from_dict(row) for row in results] if results else []
        finally:
            db.close()
    
    def save(self) -> bool:
        """Save customer to database"""
        db = DBManager()
        try:
            self.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if self.id:
                # Update existing customer
                query = """
                    UPDATE customers SET 
                    name = ?, phone = ?, email = ?, address = ?,
                    loyalty_points = ?, updated_at = ?
                    WHERE id = ?
                """
                params = (
                    self.name, self.phone, self.email, self.address,
                    self.loyalty_points, self.updated_at, self.id
                )
            else:
                # Insert new customer
                query = """
                    INSERT INTO customers (
                        name, phone, email, address,
                        loyalty_points, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.name, self.phone, self.email, self.address,
                    self.loyalty_points, self.created_at, self.updated_at
                )
            
            result = db.execute_query(query, params)
            
            if not self.id and result:
                self.id = result[0]['id']
            
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    def delete(self) -> bool:
        """Delete customer from database"""
        if not self.id:
            return False
        
        db = DBManager()
        try:
            db.execute_query(
                "DELETE FROM customers WHERE id = ?",
                (self.id,)
            )
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    def update_loyalty_points(self, points: int) -> bool:
        """Update customer loyalty points"""
        if not self.id:
            return False
        
        self.loyalty_points += points
        return self.save() 