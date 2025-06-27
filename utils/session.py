import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SessionManager:
    """Manages user sessions"""
    
    _instance = None
    _user = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize session manager"""
        if self._initialized:
            return
            
        # Get session file path
        self.session_dir = Path.home() / '.supermarket_app'
        self.session_file = self.session_dir / 'session.json'
        
        # Create session directory if it doesn't exist
        self.session_dir.mkdir(exist_ok=True)
        
        # Load existing session if any
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    if session_data.get('remember', False):
                        SessionManager._user = session_data.get('user')
            except Exception as e:
                print(f"Error loading session: {e}")
        
        self._initialized = True
    
    def set_user(self, user_data: Dict[str, Any], remember: bool = True):
        """Set the current user"""
        SessionManager._user = user_data
        if remember:
            self.save_session(user_data)
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get the current user"""
        return SessionManager._user
    
    def get_user_id(self) -> Optional[int]:
        """Get the current user ID"""
        if SessionManager._user:
            return SessionManager._user.get('id')
        return None
    
    def clear_session(self):
        """Clear the current session"""
        SessionManager._user = None
        if self.session_file.exists():
            try:
                self.session_file.unlink()
            except Exception as e:
                print(f"Error deleting session file: {e}")
    
    def save_session(self, user_data: Dict[str, Any]) -> bool:
        """Save session data"""
        try:
            session_data = {
                'user': user_data,
                'remember': True,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            return True
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        return SessionManager._user is not None 