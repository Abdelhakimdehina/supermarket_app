import customtkinter as ctk
from typing import Dict, Type, Optional

from config.constants import (
    SCREEN_LOGIN, SCREEN_DASHBOARD, SCREEN_POS,
    SCREEN_INVENTORY, SCREEN_SETTINGS,
    SCREEN_MIN_WIDTH, SCREEN_MIN_HEIGHT
)
from ui.base.base_frame import BaseFrame
from ui.screens.login.login_screen import LoginScreen
from ui.screens.dashboard.dashboard_screen import DashboardScreen
from ui.screens.pos.pos_screen import POSScreen
from ui.screens.inventory.inventory_screen import InventoryScreen

class SupermarketApp(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Supermarket Management System")
        self.geometry(f"{SCREEN_MIN_WIDTH}x{SCREEN_MIN_HEIGHT}")
        self.minsize(SCREEN_MIN_WIDTH, SCREEN_MIN_HEIGHT)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize screens
        self.screens: Dict[str, Type[BaseFrame]] = {}
        self.current_screen: Optional[BaseFrame] = None
        
        # Register screens
        self.register_screen(SCREEN_LOGIN, LoginScreen)
        self.register_screen(SCREEN_DASHBOARD, DashboardScreen)
        self.register_screen(SCREEN_POS, POSScreen)
        self.register_screen(SCREEN_INVENTORY, InventoryScreen)
        
        # Show initial screen
        self.show_screen(SCREEN_LOGIN)
    
    def register_screen(self, name: str, screen_class: Type[BaseFrame]):
        """Register a screen with the application"""
        self.screens[name] = screen_class
    
    def show_screen(self, name: str, data: Optional[Dict] = None):
        """Show a screen by name"""
        if name not in self.screens:
            raise ValueError(f"Screen {name} not found")
        
        # Hide current screen
        if self.current_screen:
            self.current_screen.grid_forget()
        
        # Create and show new screen
        screen_class = self.screens[name]
        self.current_screen = screen_class(self)
        self.current_screen.grid(row=0, column=0, sticky="nsew")
        
        # Pass data if provided
        if data:
            self.current_screen.receive_data(data)
        
        # Notify screen it's being shown
        self.current_screen.on_screen_shown()

if __name__ == "__main__":
    app = SupermarketApp()
    app.mainloop() 