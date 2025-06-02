import customtkinter as ctk
from typing import Dict, Any, Optional
import datetime

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    SCREEN_INVENTORY, SCREEN_POS, SCREEN_CUSTOMERS, 
    SCREEN_REPORTS, SCREEN_SETTINGS,
    CURRENCY_SYMBOL
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
    
    def create_sidebar(self):
        """Create sidebar with navigation menu"""
        # Sidebar frame
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=("#e0e0e0", "#1e2a3a"))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)  # Push everything up
        
        # Logo and title frame
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=(PADDING_LARGE, PADDING_MEDIUM), sticky="ew")
        
        # App logo (you can replace this with an actual logo image)
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🏪",  # Store emoji as placeholder
            font=ctk.CTkFont(size=32)
        )
        logo_label.grid(row=0, column=0, padx=(PADDING_MEDIUM, PADDING_SMALL))
        
        # App title
        title_label = ctk.CTkLabel(
            title_frame,
            text="Supermarket",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w")
        
        # Separator
        separator = ctk.CTkFrame(sidebar, height=2, fg_color=("gray70", "gray30"))
        separator.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Navigation buttons with icons (using emoji as placeholders)
        nav_buttons = [
            ("🏠 Dashboard", lambda: None, True),
            ("💰 Point of Sale", lambda: self.navigate_to(SCREEN_POS), True),
            ("📦 Inventory", lambda: self.navigate_to(SCREEN_INVENTORY), True),
            ("👥 Customers", lambda: self.navigate_to(SCREEN_CUSTOMERS), True),
            ("📊 Reports", lambda: self.navigate_to(SCREEN_REPORTS), True),
            ("⚙️ Settings", lambda: self.on_settings_click(), False)
        ]
        
        for idx, (text, command, enabled) in enumerate(nav_buttons, start=2):
            button = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                anchor="w",
                height=40,
                fg_color="transparent" if text != "🏠 Dashboard" else ("gray80", "#2c3e50"),
                text_color=("black", "white"),
                hover_color=("gray75", "#4a6885"),
                font=ctk.CTkFont(size=14),
                state="normal" if enabled else "disabled"
            )
            button.grid(row=idx, column=0, padx=PADDING_MEDIUM, pady=(PADDING_SMALL, 0), sticky="ew")
        
        # User info frame at bottom
        self.user_frame = ctk.CTkFrame(sidebar, fg_color=("gray85", "#253444"))
        self.user_frame.grid(row=11, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # User icon and name in same row
        user_header = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        user_header.grid(row=0, column=0, sticky="ew", padx=PADDING_SMALL, pady=(PADDING_SMALL, 0))
        
        ctk.CTkLabel(
            user_header,
            text="👤",  # User icon
            font=ctk.CTkFont(size=20)
        ).grid(row=0, column=0, padx=(PADDING_SMALL, PADDING_SMALL))
        
        self.user_name_label = ctk.CTkLabel(
            user_header,
            text="Not logged in",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.user_name_label.grid(row=0, column=1, sticky="w")
        
        # Role in new row
        self.user_role_label = ctk.CTkLabel(
            self.user_frame,
            text="Role: None",
            font=ctk.CTkFont(size=12)
        )
        self.user_role_label.grid(row=1, column=0, sticky="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        
        # Logout button
        logout_button = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            command=self.logout,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=36
        )
        logout_button.grid(row=12, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM, sticky="ew")
    
    def create_content_area(self):
        """Create main content area"""
        # Content frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)
        
        # Header with welcome message and date
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
        header.grid_columnconfigure(0, weight=1)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            header,
            text="Welcome to the Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w"
        )
        self.welcome_label.grid(row=0, column=0, sticky="w")
        
        # Date and time
        date_frame = ctk.CTkFrame(header, fg_color="transparent")
        date_frame.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(
            date_frame,
            text="📅",  # Calendar emoji
            font=ctk.CTkFont(size=20)
        ).grid(row=0, column=0, padx=(0, PADDING_SMALL))
        
        date_label = ctk.CTkLabel(
            date_frame,
            text=datetime.datetime.now().strftime("%A, %B %d, %Y"),
            font=ctk.CTkFont(size=14),
            anchor="e"
        )
        date_label.grid(row=0, column=1, sticky="e")
        
        # Quick action buttons
        action_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", pady=PADDING_MEDIUM)
        
        quick_actions = [
            ("🛍️ New Sale", lambda: self.navigate_to(SCREEN_POS), "#2ecc71", "#27ae60"),
            ("📦 Add Product", lambda: self.navigate_to(SCREEN_INVENTORY), "#3498db", "#2980b9"),
            ("👥 Add Customer", lambda: self.navigate_to(SCREEN_CUSTOMERS), "#9b59b6", "#8e44ad")
        ]
        
        for idx, (text, command, color, hover) in enumerate(quick_actions):
            ctk.CTkButton(
                action_frame,
                text=text,
                command=command,
                fg_color=color,
                hover_color=hover,
                height=40,
                font=ctk.CTkFont(size=14)
            ).grid(row=0, column=idx, padx=PADDING_SMALL)
        
        # Stats grid
        stats_frame = ctk.CTkFrame(self.content)
        stats_frame.grid(row=2, column=0, sticky="nsew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        stats_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Stats widgets with icons
        stats_config = [
            ("💰 Today's Sales", f"{CURRENCY_SYMBOL}0.00", 0, 0, "#2ecc71"),
            ("📦 Items Sold Today", "0", 0, 1, "#3498db"),
            ("⚠️ Low Stock Items", "0", 0, 2, "#e74c3c"),
            ("👥 Total Customers", "0", 1, 0, "#9b59b6"),
            ("📈 Monthly Revenue", f"{CURRENCY_SYMBOL}0.00", 1, 1, "#f1c40f"),
            ("📋 Pending Orders", "0", 1, 2, "#e67e22")
        ]
        
        for title, value, row, col, color in stats_config:
            self.create_stat_widget(stats_frame, title, value, row, col, color)
        
        # Schedule stats update
        self.after(100, self.update_statistics)
    
    def create_stat_widget(self, parent, title: str, value: str, row: int, column: int, color: str):
        """Create an enhanced statistics widget"""
        widget = ctk.CTkFrame(parent)
        widget.grid(row=row, column=column, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="nsew")
        widget.grid_columnconfigure(0, weight=1)
        
        # Title with icon
        title_label = ctk.CTkLabel(
            widget,
            text=title,
            font=ctk.CTkFont(size=16),
            text_color=color,
            anchor="w"
        )
        title_label.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, 0), sticky="w")
        
        # Value
        value_label = ctk.CTkLabel(
            widget,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color,
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
            
            # Update widgets with animations (simple fade effect)
            self.stat_widgets["💰 Today's Sales"].configure(text=f"{CURRENCY_SYMBOL}{stats['today_sales']:.2f}")
            self.stat_widgets["📦 Items Sold Today"].configure(text=str(stats['items_sold']))
            self.stat_widgets["⚠️ Low Stock Items"].configure(text=str(stats['low_stock']))
            self.stat_widgets["👥 Total Customers"].configure(text=str(stats['total_customers']))
            self.stat_widgets["📈 Monthly Revenue"].configure(text=f"{CURRENCY_SYMBOL}{stats['monthly_revenue']:.2f}")
            self.stat_widgets["📋 Pending Orders"].configure(text=str(stats['pending_orders']))
            
            # Schedule next update
            self.after(5000, self.update_statistics)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
            # Retry after 30 seconds if there's an error
            self.after(30000, self.update_statistics)
    
    def receive_data(self, data: Dict[str, Any]):
        """Receive data from another screen"""
        if "user" in data:
            self.user_data = data["user"]
            self.update_user_info()
    
    def update_user_info(self):
        """Update user information in the sidebar"""
        if self.user_data:
            self.user_name_label.configure(text=self.user_data.get('full_name', self.user_data.get('username', 'Unknown')))
            self.user_role_label.configure(text=f"Role: {self.user_data.get('role', 'Unknown')}")
            self.welcome_label.configure(text=f"Welcome back, {self.user_data.get('full_name', self.user_data.get('username', 'User'))}!")
    
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
        self.navigate_to(SCREEN_SETTINGS)