import customtkinter as ctk
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from tkcalendar import DateEntry

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    SCREEN_DASHBOARD, CURRENCY_SYMBOL
)
from ui.base.base_frame import BaseFrame
from services.reports_service import ReportsService

class ReportsScreen(BaseFrame):
    """Reports screen for the application"""
    
    def __init__(self, master, **kwargs):
        # Initialize services
        self.reports_service = ReportsService()
        
        # Initialize state
        self.current_report = 'sales'  # sales, inventory, customers
        self.start_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()
        
        super().__init__(master, **kwargs)
        
        # Set background color
        self.configure(fg_color=("#f0f0f0", "#2c3e50"))
    
    def init_ui(self):
        """Initialize UI components"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Create header
        self.create_header()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Load initial report
        self.load_report()
    
    def create_header(self):
        """Create page header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, PADDING_SMALL))
        header.grid_columnconfigure(1, weight=1)
        
        # Back button
        back_button = ctk.CTkButton(
            header,
            text="← Back",
            command=lambda: self.navigate_to(SCREEN_DASHBOARD),
            fg_color="transparent",
            text_color=("gray20", "gray80"),
            hover_color=("gray70", "gray30"),
            width=100,
            height=32
        )
        back_button.grid(row=0, column=0, padx=(0, PADDING_MEDIUM))
        
        # Page title
        title = ctk.CTkLabel(
            header,
            text="📊 Reports & Analytics",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.grid(row=0, column=1, sticky="w")
    
    def create_toolbar(self):
        """Create toolbar with report types and date range"""
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        toolbar.grid_columnconfigure(1, weight=1)
        
        # Report type buttons
        report_types = ctk.CTkFrame(toolbar, fg_color="transparent")
        report_types.grid(row=0, column=0, sticky="w")
        
        reports = [
            ("📈 Sales", "sales", "#2ecc71"),
            ("📦 Inventory", "inventory", "#3498db"),
            ("👥 Customers", "customers", "#9b59b6")
        ]
        
        for idx, (text, report_type, color) in enumerate(reports):
            btn = ctk.CTkButton(
                report_types,
                text=text,
                command=lambda t=report_type: self.switch_report(t),
                fg_color=color if report_type == self.current_report else "transparent",
                text_color="white" if report_type == self.current_report else ("gray20", "gray80"),
                hover_color=color,
                height=32
            )
            btn.grid(row=0, column=idx, padx=(0 if idx == 0 else PADDING_SMALL, 0))
        
        # Date range
        date_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        date_frame.grid(row=0, column=1, sticky="e")
        
        ctk.CTkLabel(
            date_frame,
            text="From:",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=(0, PADDING_SMALL))
        
        self.start_date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            firstweekday='sunday'
        )
        self.start_date_entry.grid(row=0, column=1, padx=PADDING_SMALL)
        self.start_date_entry.set_date(self.start_date)
        
        ctk.CTkLabel(
            date_frame,
            text="To:",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=2, padx=(PADDING_MEDIUM, PADDING_SMALL))
        
        self.end_date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            firstweekday='sunday'
        )
        self.end_date_entry.grid(row=0, column=3, padx=PADDING_SMALL)
        self.end_date_entry.set_date(self.end_date)
        
        # Apply button
        apply_button = ctk.CTkButton(
            date_frame,
            text="Apply",
            command=self.load_report,
            height=32
        )
        apply_button.grid(row=0, column=4, padx=(PADDING_MEDIUM, 0))
    
    def switch_report(self, report_type: str):
        """Switch to different report type"""
        self.current_report = report_type
        self.load_report()
    
    def load_report(self):
        """Load and display the current report"""
        try:
            # Clear previous content
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            # Get date range
            start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
            end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
            
            # Load report based on type
            if self.current_report == 'sales':
                self.load_sales_report(start_date, end_date)
            elif self.current_report == 'inventory':
                self.load_inventory_report()
            else:  # customers
                self.load_customer_report(start_date, end_date)
                
        except Exception as e:
            self.show_message("Error", f"Failed to load report: {str(e)}")
    
    def load_sales_report(self, start_date: str, end_date: str):
        """Load and display sales report"""
        # Get data
        data = self.reports_service.get_sales_summary(start_date, end_date)
        summary = data.get('summary', {})
        
        # Create summary cards
        summary_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
        summary_frame.grid_columnconfigure((0,1,2), weight=1)
        
        # Summary cards
        self.create_summary_card(
            summary_frame, 0,
            "Total Sales",
            f"{CURRENCY_SYMBOL}{summary.get('total_revenue', 0):.2f}",
            f"{summary.get('total_sales', 0)} transactions",
            "#2ecc71"
        )
        
        self.create_summary_card(
            summary_frame, 1,
            "Average Sale",
            f"{CURRENCY_SYMBOL}{summary.get('average_sale', 0):.2f}",
            f"{summary.get('unique_customers', 0)} unique customers",
            "#3498db"
        )
        
        self.create_summary_card(
            summary_frame, 2,
            "Total Discounts",
            f"{CURRENCY_SYMBOL}{summary.get('total_discounts', 0):.2f}",
            f"{CURRENCY_SYMBOL}{summary.get('total_tax', 0):.2f} tax collected",
            "#e74c3c"
        )
        
        # Payment methods
        if data.get('payment_methods'):
            payment_frame = ctk.CTkFrame(self.content_frame)
            payment_frame.grid(row=1, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
            
            ctk.CTkLabel(
                payment_frame,
                text="Payment Methods",
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            
            for idx, method in enumerate(data['payment_methods']):
                method_text = f"{method['payment_method']}: {method['count']} sales ({CURRENCY_SYMBOL}{method['total']:.2f})"
                ctk.CTkLabel(
                    payment_frame,
                    text=method_text
                ).grid(row=idx+1, column=0, padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
    
    def load_inventory_report(self):
        """Load and display inventory report"""
        # Get data
        data = self.reports_service.get_inventory_status()
        summary = data.get('summary', {})
        
        # Create summary cards
        summary_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
        summary_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.create_summary_card(
            summary_frame, 0,
            "Total Products",
            str(summary.get('total_products', 0)),
            f"{CURRENCY_SYMBOL}{summary.get('total_stock_value', 0):.2f} value",
            "#2ecc71"
        )
        
        self.create_summary_card(
            summary_frame, 1,
            "Total Stock",
            str(summary.get('total_stock', 0)),
            "units",
            "#3498db"
        )
        
        self.create_summary_card(
            summary_frame, 2,
            "Low Stock Items",
            str(summary.get('low_stock_count', 0)),
            "need reordering",
            "#e74c3c"
        )
        
        # Low stock warnings
        if data.get('low_stock'):
            low_stock_frame = ctk.CTkFrame(self.content_frame)
            low_stock_frame.grid(row=1, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
            
            ctk.CTkLabel(
                low_stock_frame,
                text="Low Stock Warnings",
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, columnspan=2, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            
            for idx, item in enumerate(data['low_stock']):
                text = f"{item['name']}: {item['stock_quantity']}/{item['reorder_level']} units"
                ctk.CTkLabel(
                    low_stock_frame,
                    text=text,
                    text_color="#e74c3c"
                ).grid(row=idx+1, column=0, padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
    
    def load_customer_report(self, start_date: str, end_date: str):
        """Load and display customer report"""
        # Get data
        data = self.reports_service.get_customer_analytics(start_date, end_date)
        summary = data.get('summary', {})
        
        # Create summary cards
        summary_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
        summary_frame.grid_columnconfigure((0,1,2), weight=1)
        
        self.create_summary_card(
            summary_frame, 0,
            "Active Customers",
            str(summary.get('active_customers', 0)),
            f"{summary.get('guest_transactions', 0)} guest transactions",
            "#2ecc71"
        )
        
        self.create_summary_card(
            summary_frame, 1,
            "Average Transaction",
            f"{CURRENCY_SYMBOL}{summary.get('average_transaction', 0):.2f}",
            "per customer",
            "#3498db"
        )
        
        self.create_summary_card(
            summary_frame, 2,
            "Revenue per Customer",
            f"{CURRENCY_SYMBOL}{summary.get('revenue_per_customer', 0):.2f}",
            "lifetime value",
            "#9b59b6"
        )
        
        # Customer segments
        if data.get('segments'):
            segments_frame = ctk.CTkFrame(self.content_frame)
            segments_frame.grid(row=1, column=0, sticky="ew", pady=(0, PADDING_MEDIUM))
            
            ctk.CTkLabel(
                segments_frame,
                text="Customer Segments",
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, columnspan=2, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
            
            for idx, segment in enumerate(data['segments']):
                text = f"{segment['segment']}: {segment['customer_count']} customers (avg {segment['avg_visits']:.1f} visits)"
                ctk.CTkLabel(
                    segments_frame,
                    text=text
                ).grid(row=idx+1, column=0, padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
    
    def create_summary_card(self, parent: ctk.CTkFrame, column: int, title: str, value: str, subtitle: str, color: str):
        """Create a summary card widget"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=column, sticky="nsew", padx=PADDING_SMALL)
        
        # Title
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color=color
        ).grid(row=0, column=0, padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, 0))
        
        # Value
        ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        ).grid(row=1, column=0, padx=PADDING_MEDIUM)
        
        # Subtitle
        ctk.CTkLabel(
            frame,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        ).grid(row=2, column=0, padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM)) 