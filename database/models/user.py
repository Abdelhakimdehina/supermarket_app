from typing import Optional, Dict, List, Any
import sqlite3
from datetime import datetime

from database.db_manager import DBManager
from utils.security import hash_password, verify_password

class User:
    """User model for the application"""
    
    def __init__(self, id: int = None, username: str = None, password: str = None, 
                 full_name: str = None, email: str = None, role: str = None, 
                 is_active: bool = True, created_at: str = None, last_login: str = None):
        self.id = id
        self.username = username
        self.password = password  # Hashed password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.last_login = last_login
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Get a user by username"""
        db = DBManager()
        try:
            result = db.execute_query(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            if result and len(result) > 0:
                return cls.from_dict(result[0])
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password=data.get('password'),
            full_name=data.get('full_name'),
            email=data.get('email'),
            role=data.get('role'),
            is_active=bool(data.get('is_active', 1)),
            created_at=data.get('created_at'),
            last_login=data.get('last_login')
        )
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """Convert User instance to a dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'is_active': 1 if self.is_active else 0,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
        
        if include_password:
            data['password'] = self.password
        
        return data
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Get a user by ID"""
        db = DBManager()
        try:
            results = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
            if results and len(results) > 0:
                return User.from_dict(results[0])
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all() -> List['User']:
        """Get all users"""
        db = DBManager()
        try:
            results = db.execute_query("SELECT * FROM users ORDER BY username")
            return [User.from_dict(row) for row in results] if results else []
        finally:
            db.close()
    
    def save(self) -> bool:
        """Save user to database"""
        db = DBManager()
        try:
            if self.id:
                # Update existing user
                query = """
                    UPDATE users SET 
                    username = ?, password = ?, full_name = ?, 
                    email = ?, role = ?, is_active = ?
                    WHERE id = ?
                """
                params = (
                    self.username, self.password, self.full_name,
                    self.email, self.role, 1 if self.is_active else 0,
                    self.id
                )
            else:
                # Insert new user
                query = """
                    INSERT INTO users (
                        username, password, full_name, email,
                        role, is_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.username, self.password, self.full_name,
                    self.email, self.role, 1 if self.is_active else 0,
                    self.created_at
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
    
    def update_password(self, new_password: str) -> bool:
        """Update user password"""
        if not self.id:
            return False
        
        try:
            self.password = hash_password(new_password)
            return self.save()
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete user from database"""
        if not self.id:
            return False
        
        db = DBManager()
        try:
            query = "DELETE FROM users WHERE id = ?"
            params = (self.id,)
            db.execute_query(query, params)
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    def update_last_login(self) -> bool:
        """Update user's last login timestamp"""
        if not self.id:
            return False
        
        db = DBManager()
        try:
            query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
            params = (self.id,)
            db.execute_query(query, params)
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            db.close()