import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import get_db_connection
from utils.session import SessionManager

class AuthService:
    """Service class for authentication and user management"""
    
    def __init__(self):
        """Initialize the auth service"""
        self.session_manager = SessionManager()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get user by username
            cursor.execute("""
                SELECT id, username, password_hash, full_name, email, role
                FROM users
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            
            if user and check_password_hash(user[2], password):
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'full_name': user[3],
                    'email': user[4],
                    'role': user[5]
                }
                # Set user in session
                self.session_manager.set_user(user_data)
                return user_data
            
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username without password verification (for session-based auth)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, full_name, email, role
                FROM users
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'full_name': user[2],
                    'email': user[3],
                    'role': user[4]
                }
            
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, full_name, email, role
                FROM users
                WHERE id = ? AND is_active = 1
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'full_name': user[2],
                    'email': user[3],
                    'role': user[4]
                }
            
            return None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """Create a new user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Hash password
            password_hash = generate_password_hash(user_data['password'])
            
            cursor.execute("""
                INSERT INTO users (
                    username, password_hash, full_name, email, role,
                    is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                user_data['username'],
                password_hash,
                user_data['full_name'],
                user_data['email'],
                user_data['role'],
                now, now
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """Update an existing user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Start with base fields
            fields = ['full_name', 'email', 'role']
            values = [user_data['full_name'], user_data['email'], user_data['role']]
            
            # Add password if provided
            if 'password' in user_data:
                fields.append('password_hash')
                values.append(generate_password_hash(user_data['password']))
            
            # Build update query
            query = f"""
                UPDATE users
                SET {', '.join(f'{field} = ?' for field in fields)},
                    updated_at = ?
                WHERE id = ?
            """
            
            # Add timestamp and user_id to values
            values.extend([now, user_id])
            
            # Execute update
            cursor.execute(query, values)
            conn.commit()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def delete_user(self, user_id: int) -> bool:
        """Soft delete a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                UPDATE users
                SET is_active = 0,
                    updated_at = ?
                WHERE id = ?
            """, (now, user_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get current password hash
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row or not check_password_hash(row[0], current_password):
                return False
            
            # Update password
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_password_hash = generate_password_hash(new_password)
            
            cursor.execute("""
                UPDATE users
                SET password_hash = ?,
                    updated_at = ?
                WHERE id = ?
            """, (new_password_hash, now, user_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if successful"""
        user = self.authenticate(username, password)
        if user:
            self.session_manager.set_user(user)
            return user
        return None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the currently logged in user"""
        return self.session_manager.get_user()
    
    def logout(self) -> bool:
        """Log out the current user by clearing the session"""
        try:
            self.session_manager.clear_session()
            return True
        except Exception as e:
            print(f"Error during logout: {e}")
            return False