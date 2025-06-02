import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SessionManager:
    """Manage user sessions"""
    
    def __init__(self):
        """Initialize session manager"""
        # Get session file path
        self.session_dir = Path.home() / '.supermarket_app'
        self.session_file = self.session_dir / 'session.json'
        
        # Create session directory if it doesn't exist
        self.session_dir.mkdir(exist_ok=True)
    
    def save_session(self, username: str, remember: bool = False) -> bool:
        """Save session data"""
        try:
            session_data = {
                'username': username,
                'remember': remember
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            return True
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """Load session data"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def clear_session(self) -> bool:
        """Clear session data"""
        try:
            if self.session_file.exists():
                os.remove(self.session_file)
            
            return True
            
        except Exception as e:
            print(f"Error clearing session: {e}")
            return False
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        session = self.load_session()
        return session is not None 