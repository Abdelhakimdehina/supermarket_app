import customtkinter as ctk
from typing import Dict, Any, Optional
import datetime

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    SCREEN_INVENTORY, SCREEN_POS, SCREEN_CUSTOMERS, 
    SCREEN_REPORTS, SCREEN_SETTINGS
)
from ui.base.base_frame import BaseFrame
from services.auth_service import AuthService
from services.statistics_service import StatisticsService
from utils.session import SessionManager

class DashboardScreen(BaseFrame):
    """Dashboard screen for the application"""
    
    def __init__(self, master, **kwargs):
        # Initialize services
        self.auth_service = AuthService()
        self.stats_service = StatisticsService()
        self.session_manager = SessionManager()
        
        # Initialize stat widgets dictionary before super().__init__
        self.stat_widgets = {}
        
        super().__init__(master, **kwargs)
        
        # User data
        self.user_data = None
        
        # Set background color
        self.configure(fg_color=("#f0f0f0", "#2c3e50"))
    
    def init_ui(self):
        """Initialize UI components"""
        # Create main container with 2 columns
        self.grid_columnconfigure(0, weight=0)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Content (expandable)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area
        self.create_content_area()
    
    # Fix the settings button in the create_sidebar method
    def create_sidebar(self):
        """Create sidebar with navigation menu"""
        # Sidebar frame
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)  # Push everything up
        
        # App title
        title_label = ctk.CTkLabel(
            sidebar, 
            text="Supermarket", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=(PADDING_LARGE, PADDING_MEDIUM))
        
        # Navigation buttons
        self.create_nav_button(sidebar, "Dashboard", 1, lambda: None)  # Current screen
        self.create_nav_button(sidebar, "Point of Sale", 2, lambda: self.navigate_to(SCREEN_POS))
        self.create_nav_button(sidebar, "Inventory", 3, lambda: self.navigate_to(SCREEN_INVENTORY))
        self.create_nav_button(sidebar, "Customers", 4, lambda: self.navigate_to(SCREEN_CUSTOMERS))
        self.create_nav_button(sidebar, "Reports", 5, lambda: self.navigate_to(SCREEN_REPORTS))
        self.create_nav_button(sidebar, "Settings", 6, lambda: self.on_settings_click())
        
        # User info at bottom
        self.user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.user_frame.grid(row=11, column=0, sticky="ew", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        self.user_name_label = ctk.CTkLabel(
            self.user_frame, 
            text="User: Not logged in", 
            font=ctk.CTkFont(size=12)
        )
        self.user_name_label.grid(row=0, column=0, sticky="w", padx=PADDING_SMALL)
        
        self.user_role_label = ctk.CTkLabel(
            self.user_frame, 
            text="Role: None", 
            font=ctk.CTkFont(size=12)
        )
        self.user_role_label.grid(row=1, column=0, sticky="w", padx=PADDING_SMALL)
        
        # Logout button
        logout_button = ctk.CTkButton(
            sidebar, 
            text="Logout", 
            command=self.logout,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        logout_button.grid(row=12, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM, sticky="ew")
    
    def create_nav_button(self, parent, text, row, command):
        """Create a navigation button"""
        button = ctk.CTkButton(
            parent, 
            text=text, 
            command=command,
            anchor="w",
            fg_color="transparent" if text != "Dashboard" else None,
            hover_color=("#e0e0e0", "#4a6885"),
            state="disabled" if text not in ["Dashboard", "Point of Sale", "Inventory", "Logout"] else "normal"  # Enable Inventory
        )
        button.grid(row=row, column=0, padx=PADDING_SMALL, pady=(PADDING_SMALL, 0), sticky="ew")
    
    def create_content_area(self):
        """Create main content area"""
        # Content frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)
        
        # Header with welcome message and date
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
        header.grid_columnconfigure(0, weight=1)
        
        self.welcome_label = ctk.CTkLabel(
            header, 
            text="Welcome to the Dashboard", 
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        self.welcome_label.grid(row=0, column=0, sticky="w")
        
        date_label = ctk.CTkLabel(
            header, 
            text=datetime.datetime.now().strftime("%A, %B %d, %Y"), 
            font=ctk.CTkFont(size=14),
            anchor="e"
        )
        date_label.grid(row=0, column=1, sticky="e")
        
        # Dashboard widgets container
        dashboard = ctk.CTkFrame(self.content)
        dashboard.grid(row=1, column=0, sticky="nsew")
        dashboard.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard.grid_rowconfigure((0, 1), weight=1)
        
        # Quick stats widgets with initial values
        self.create_stat_widget(dashboard, "Today's Sales", "$0.00", 0, 0)
        self.create_stat_widget(dashboard, "Items Sold Today", "0", 0, 1)
        self.create_stat_widget(dashboard, "Low Stock Items", "0", 0, 2)
        self.create_stat_widget(dashboard, "Total Customers", "0", 1, 0)
        self.create_stat_widget(dashboard, "Monthly Revenue", "$0.00", 1, 1)
        self.create_stat_widget(dashboard, "Pending Orders", "0", 1, 2)
        
        # Update statistics immediately
        self.after(100, self.update_statistics)  # Schedule update after widgets are created
    
    def create_stat_widget(self, parent, title, value, row, column):
        """Create a statistics widget"""
        widget = ctk.CTkFrame(parent)
        widget.grid(row=row, column=column, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="nsew")
        widget.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            widget, 
            text=title, 
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        title_label.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, 0), sticky="w")
        
        value_label = ctk.CTkLabel(
            widget, 
            text=value, 
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="center"
        )
        value_label.grid(row=1, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Store reference to value label
        self.stat_widgets[title] = value_label
        
        return widget
    
    def update_statistics(self):
        """Update dashboard statistics"""
        try:
            # Get statistics
            stats = self.stats_service.get_today_stats()
            
            # Update widgets
            self.stat_widgets["Today's Sales"].configure(text=f"${stats['today_sales']:.2f}")
            self.stat_widgets["Items Sold Today"].configure(text=str(stats['items_sold']))
            self.stat_widgets["Low Stock Items"].configure(text=str(stats['low_stock']))
            self.stat_widgets["Total Customers"].configure(text=str(stats['total_customers']))
            self.stat_widgets["Monthly Revenue"].configure(text=f"${stats['monthly_revenue']:.2f}")
            self.stat_widgets["Pending Orders"].configure(text=str(stats['pending_orders']))
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def receive_data(self, data: Dict[str, Any]):
        """Receive data from another screen"""
        if "user" in data:
            self.user_data = data["user"]
            self.update_user_info()
    
    def update_user_info(self):
        """Update user information in the sidebar"""
        if self.user_data:
            self.user_name_label.configure(text=f"User: {self.user_data.get('full_name', self.user_data.get('username', 'Unknown'))}")
            self.user_role_label.configure(text=f"Role: {self.user_data.get('role', 'Unknown')}")
            self.welcome_label.configure(text=f"Welcome, {self.user_data.get('full_name', self.user_data.get('username', 'User'))}!")
    
    def on_screen_shown(self):
        """Called when the screen is shown"""
        # If we don't have user data yet, get it from the auth service
        if not self.user_data:
            self.user_data = self.auth_service.get_current_user()
            self.update_user_info()
        
        # Update statistics
        self.update_statistics()
    
    def logout(self):
        """Log out the current user"""
        try:
            # Clear user data
            self.user_data = None
            
            # Clear session
            self.session_manager.clear_session()
            
            # Navigate to login screen
            self.navigate_to("login")
        except Exception as e:
            print(f"Error during logout: {e}")
            self.show_message(
                "Error",
                "An unexpected error occurred during logout. Please try again."
            )
    
    def on_settings_click(self):
        """Handle settings button click"""
        # Navigate to user management screen
        self.navigate_to(SCREEN_USER_MANAGEMENT)