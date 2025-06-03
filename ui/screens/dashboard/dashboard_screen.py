import customtkinter as ctk
from typing import Dict, Any, Optional
import datetime

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    SCREEN_INVENTORY, SCREEN_POS, SCREEN_CUSTOMERS, 
    SCREEN_REPORTS, SCREEN_SETTINGS,
    CURRENCY_SYMBOL, COLORS
)
from ui.base.base_frame import BaseFrame
from services.auth_service import AuthService
from services.statistics_service import StatisticsService
from utils.session import SessionManager

class ModernCard(ctk.CTkFrame):
    """A modern, glassmorphic card widget"""
    
    def __init__(
        self, 
        master, 
        title: str,
        value: str,
        icon: str,
        accent_color: str,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=accent_color,
            **kwargs
        )

        self.accent_color = accent_color
        self.configure(cursor="hand2")  # Pointer cursor on hover
        
        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        
        # Icon and title in same row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, 0))
        
        # Icon
        icon_label = ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(size=24),
            text_color=accent_color
        )
        icon_label.grid(row=0, column=0, sticky="w")
        
        # Title
        title_label = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=(PADDING_SMALL, 0), sticky="w")
        
        # Value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.value_label.grid(row=1, column=0, padx=PADDING_MEDIUM, pady=(PADDING_SMALL, PADDING_MEDIUM))
        
        # Loading indicator
        self.loading_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.loading_label.grid(row=2, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter event"""
        self.configure(fg_color=COLORS["bg_darker"])
    
    def _on_leave(self, event):
        """Handle mouse leave event"""
        self.configure(fg_color=COLORS["card_bg"])
    
    def set_value(self, value: str):
        """Update the card's value"""
        self.value_label.configure(text=value)
    
    def set_loading(self, is_loading: bool):
        """Update loading state"""
        self.loading_label.configure(
            text="Loading..." if is_loading else ""
        )
    
    def set_error(self, has_error: bool):
        """Show error state"""
        if has_error:
            self.loading_label.configure(text="Failed to update")
        else:
            self.loading_label.configure(text="")

class DashboardScreen(BaseFrame):
    """Modern dashboard screen for the application"""
    
    def __init__(self, master, **kwargs):
        # Initialize services
        self.auth_service = AuthService()
        self.stats_service = StatisticsService()
        self.session_manager = SessionManager()
        
        # Initialize UI elements that need to be accessed later
        self.welcome_label = None
        self.user_name_label = None
        self.user_role_label = None
        self.user_frame = None
        
        # Initialize stat widgets dictionary before super().__init__
        self.stat_widgets = {}
        
        # Add loading state
        self.is_loading_stats = False
        
        super().__init__(master, **kwargs)
        
        # User data
        self.user_data = None
        
        # Set dark theme background
        self.configure(fg_color=COLORS["bg_dark"])
    
    def create_sidebar(self):
        """Create sidebar with navigation menu"""
        # Sidebar frame with dark theme
        sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=COLORS["bg_darker"]
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)  # Push everything up
        
        # Logo and title frame
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=(PADDING_LARGE, PADDING_MEDIUM), sticky="ew")
        
        # App logo
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🏪",
            font=ctk.CTkFont(size=32)
        )
        logo_label.grid(row=0, column=0, padx=(PADDING_MEDIUM, PADDING_SMALL))
        
        # App title with modern font
        title_label = ctk.CTkLabel(
            title_frame,
            text="Supermarket",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title_label.grid(row=0, column=1, sticky="w")
        
        # Modern separator
        separator = ctk.CTkFrame(
            sidebar,
            height=2,
            fg_color=COLORS["text_secondary"]
        )
        separator.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Navigation buttons with modern styling
        nav_buttons = [
            ("🏠 Dashboard", lambda: None, True, COLORS["accent_purple"]),
            ("💰 Point of Sale", lambda: self.navigate_to(SCREEN_POS), True, None),
            ("📦 Inventory", lambda: self.navigate_to(SCREEN_INVENTORY), True, None),
            ("👥 Customers", lambda: self.navigate_to(SCREEN_CUSTOMERS), True, None),
            ("📊 Reports", lambda: self.navigate_to(SCREEN_REPORTS), True, None),
            ("⚙️ Settings", lambda: self.navigate_to(SCREEN_SETTINGS), True, None)
        ]
        
        for idx, (text, command, enabled, active_color) in enumerate(nav_buttons, start=2):
            button = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                anchor="w",
                height=40,
                fg_color=active_color if active_color else "transparent",
                text_color=COLORS["text_primary"],
                hover_color=COLORS["bg_dark"],
                font=ctk.CTkFont(size=14),
                state="normal" if enabled else "disabled"
            )
            button.grid(row=idx, column=0, padx=PADDING_MEDIUM, pady=(PADDING_SMALL, 0), sticky="ew")
        
        # User info frame with glassmorphism effect
        self.user_frame = ctk.CTkFrame(
            sidebar,
            fg_color=COLORS["bg_dark"],
            corner_radius=12
        )
        self.user_frame.grid(row=11, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # User icon and name in same row
        user_header = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        user_header.grid(row=0, column=0, sticky="ew", padx=PADDING_SMALL, pady=(PADDING_SMALL, 0))
        
        ctk.CTkLabel(
            user_header,
            text="👤",
            font=ctk.CTkFont(size=20)
        ).grid(row=0, column=0, padx=(PADDING_SMALL, PADDING_SMALL))
        
        self.user_name_label = ctk.CTkLabel(
            user_header,
            text="Not logged in",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.user_name_label.grid(row=0, column=1, sticky="w")
        
        # Role with muted color
        self.user_role_label = ctk.CTkLabel(
            self.user_frame,
            text="Role: None",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.user_role_label.grid(row=1, column=0, sticky="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        
        # Modern logout button
        logout_button = ctk.CTkButton(
            sidebar,
            text="🚪 Logout",
            command=self.logout,
            fg_color=COLORS["accent_red"],
            hover_color=COLORS["bg_dark"],
            height=36,
            corner_radius=8
        )
        logout_button.grid(row=12, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM, sticky="ew")
    
    def create_content_area(self):
        """Create main content area with modern design"""
        # Content frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Header with welcome message and date
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_LARGE))
        header.grid_columnconfigure(0, weight=1)
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            header,
            text="Welcome to the Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.welcome_label.grid(row=0, column=0, sticky="w")
        
        # Date and refresh frame
        date_frame = ctk.CTkFrame(header, fg_color="transparent")
        date_frame.grid(row=0, column=1, sticky="e")
        
        # Refresh button with modern style
        refresh_button = ctk.CTkButton(
            date_frame,
            text="🔄",
            width=40,
            height=40,
            command=self.refresh_statistics,
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["bg_dark"],
            corner_radius=12
        )
        refresh_button.grid(row=0, column=0, padx=(0, PADDING_MEDIUM))
        
        # Date display
        date_label = ctk.CTkLabel(
            date_frame,
            text=datetime.datetime.now().strftime("%A, %B %d, %Y"),
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_secondary"]
        )
        date_label.grid(row=0, column=1, sticky="e")
        
        # Stats grid with modern cards
        stats_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="nsew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        stats_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Stats configuration with modern styling
        stats_config = [
            ("Today's Sales", f"{CURRENCY_SYMBOL}0.00", "💰", 0, 0, COLORS["accent_green"]),
            ("Items Sold Today", "0", "📦", 0, 1, COLORS["accent_blue"]),
            ("Low Stock Items", "0", "⚠️", 0, 2, COLORS["accent_red"]),
            ("Total Customers", "0", "👥", 1, 0, COLORS["accent_purple"]),
            ("Monthly Revenue", f"{CURRENCY_SYMBOL}0.00", "📈", 1, 1, COLORS["accent_yellow"]),
            ("Pending Orders", "0", "📋", 1, 2, COLORS["accent_orange"])
        ]
        
        # Create modern cards
        for title, value, icon, row, col, color in stats_config:
            card = ModernCard(
                stats_frame,
                title=title,
                value=value,
                icon=icon,
                accent_color=color
            )
            card.grid(
                row=row, 
                column=col, 
                padx=PADDING_SMALL, 
                pady=PADDING_SMALL, 
                sticky="nsew"
            )
            self.stat_widgets[title] = card
        
        # Schedule initial statistics update
        self.after(100, self.update_statistics)
    
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
    
    def update_statistics(self):
        """Update dashboard statistics with modern loading states"""
        if self.is_loading_stats:
            return
            
        try:
            self.is_loading_stats = True
            
            # Show loading state
            for widget in self.stat_widgets.values():
                widget.set_loading(True)
            
            # Get statistics
            stats = self.stats_service.get_today_stats()
            
            # Update widgets
            stat_updates = [
                ("Today's Sales", f"{CURRENCY_SYMBOL}{stats['today_sales']:.2f}"),
                ("Items Sold Today", str(stats['items_sold'])),
                ("Low Stock Items", str(stats['low_stock'])),
                ("Total Customers", str(stats['total_customers'])),
                ("Monthly Revenue", f"{CURRENCY_SYMBOL}{stats['monthly_revenue']:.2f}"),
                ("Pending Orders", str(stats['pending_orders']))
            ]
            
            for title, value in stat_updates:
                if title in self.stat_widgets:
                    self.stat_widgets[title].set_value(value)
                    self.stat_widgets[title].set_loading(False)
            
            # Schedule next update
            self.after(5000, self.update_statistics)
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
            # Show error state
            for widget in self.stat_widgets.values():
                widget.set_error(True)
            # Retry after 30 seconds
            self.after(30000, self.update_statistics)
        
        finally:
            self.is_loading_stats = False
    
    def refresh_statistics(self):
        """Manually refresh statistics"""
        if not self.is_loading_stats:
            self.update_statistics()
    
    def update_user_info(self):
        """Update user information with modern styling"""
        if self.user_data and self.welcome_label:
            name = self.user_data.get('full_name', self.user_data.get('username', 'User'))
            self.welcome_label.configure(
                text=f"Welcome back, {name}! 👋"
            )
            if self.user_name_label:
                self.user_name_label.configure(
                    text=self.user_data.get('full_name', self.user_data.get('username', 'Unknown'))
                )
            if self.user_role_label:
                self.user_role_label.configure(
                    text=f"Role: {self.user_data.get('role', 'Unknown')}"
                )
    
    def receive_data(self, data: Dict[str, Any]):
        """Receive data from another screen"""
        if "user" in data:
            self.user_data = data["user"]
            self.update_user_info()
    
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