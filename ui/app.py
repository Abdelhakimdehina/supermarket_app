import os
import customtkinter as ctk
from typing import Dict, Type, Optional, Any
from config.constants import SCREEN_LOGIN, SCREEN_DASHBOARD, SCREEN_USER_MANAGEMENT, SCREEN_POS
from config.settings import APP_NAME, SCREEN_MIN_WIDTH, SCREEN_MIN_HEIGHT
from ui.base.base_frame import BaseFrame
from ui.screens.login.login_screen import LoginScreen
from ui.screens.dashboard.dashboard_screen import DashboardScreen
from ui.screens.settings.user_management import UserManagementScreen
from ui.screens.pos.pos_screen import POSScreen

class App(ctk.CTk):
    """Main application window"""
    
    def __init__(self, width: int, height: int):
        super().__init__()
        
        # Configure window
        self.title("Supermarket Management System")
        self.geometry(f"{width}x{height}")
        self.minsize(800, 600)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize screens dictionary
        self.screens: Dict[str, BaseFrame] = {}
        self.current_screen: Optional[BaseFrame] = None
        
        # Register screens first
        self.register_screens()
        
        # Then initialize and show login screen
        self.show_screen(SCREEN_LOGIN)
    
    def register_screens(self):
        """Register all application screens"""
        # Create screen instances
        self.screens[SCREEN_LOGIN] = LoginScreen(self)
        self.screens[SCREEN_DASHBOARD] = DashboardScreen(self)
        self.screens[SCREEN_POS] = POSScreen(self)
        
        # Configure each screen
        for screen in self.screens.values():
            screen.grid(row=0, column=0, sticky="nsew")
            screen.grid_remove()  # Hide screen
            screen.init_ui()  # Initialize UI components
    
    def show_screen(self, name: str, data: Dict = None):
        """Show a screen by name"""
        # Check if screen exists
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' not found")
        
        # Get target screen
        target_screen = self.screens[name]
        
        # Pass data if provided
        if data:
            target_screen.receive_data(data)
        
        # Hide current screen
        if self.current_screen:
            self.current_screen.grid_remove()
        
        # Show new screen
        target_screen.grid()
        target_screen.on_screen_shown()
        
        # Update current screen
        self.current_screen = target_screen