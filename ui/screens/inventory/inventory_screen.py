import customtkinter as ctk
from tkinter import ttk
from typing import Dict, Any, Optional, List
from CTkTable import CTkTable
from datetime import datetime

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    CATEGORIES,
    SCREEN_DASHBOARD,
    CURRENCY_SYMBOL
)
from ui.base.base_frame import BaseFrame
from services.inventory_service import InventoryService
from services.auth_service import AuthService
from utils.session import SessionManager
from ui.components.dialogs.product_dialog import ProductDialog
from ui.components.dialogs.stock_adjustment_dialog import StockAdjustmentDialog

class InventoryScreen(BaseFrame):
    """Inventory management screen"""
    
    def __init__(self, master, **kwargs):
        self.inventory_service = InventoryService()
        self.auth_service = AuthService()
        self.session_manager = SessionManager()
        self.current_sort_column = None
        self.sort_ascending = True
        self.products = []
        self.selected_product = None
        
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
        
        # Create main content
        self.create_content()
    
    def create_header(self):
        """Create page header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, PADDING_SMALL))
        header.grid_columnconfigure(1, weight=1)
        
        # Back button with icon
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
            text="📦 Inventory Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.grid(row=0, column=1, sticky="w")
        
        # Stats summary
        stats_frame = ctk.CTkFrame(header, fg_color=("gray90", "gray20"))
        stats_frame.grid(row=0, column=2, padx=(PADDING_MEDIUM, 0))
        
        total_products = ctk.CTkLabel(
            stats_frame,
            text="Total Products: 0",
            font=ctk.CTkFont(size=12),
            padx=PADDING_MEDIUM,
            pady=PADDING_SMALL
        )
        total_products.grid(row=0, column=0)
        
        ctk.CTkLabel(
            stats_frame,
            text="•",
            font=ctk.CTkFont(size=12),
            padx=PADDING_SMALL
        ).grid(row=0, column=1)
        
        low_stock = ctk.CTkLabel(
            stats_frame,
            text="Low Stock: 0",
            font=ctk.CTkFont(size=12),
            text_color=("#e74c3c", "#ff6b6b"),
            padx=PADDING_MEDIUM,
            pady=PADDING_SMALL
        )
        low_stock.grid(row=0, column=2)
        
        self.stat_labels = {
            'total_products': total_products,
            'low_stock': low_stock
        }
    
    def create_toolbar(self):
        """Create toolbar with actions and search"""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        toolbar.grid_columnconfigure(1, weight=1)
        
        # Left side - Action buttons
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.grid(row=0, column=0, sticky="w")
        
        # Add Product button
        add_button = ctk.CTkButton(
            actions_frame,
            text="+ Add Product",
            command=self.add_product,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=32
        )
        add_button.grid(row=0, column=0, padx=(0, PADDING_SMALL))
        
        # Stock Adjustment button
        adjust_button = ctk.CTkButton(
            actions_frame,
            text="⚖️ Adjust Stock",
            command=self.adjust_stock,
            fg_color="#3498db",
            hover_color="#2980b9",
            height=32,
            state="disabled"
        )
        adjust_button.grid(row=0, column=1, padx=PADDING_SMALL)
        
        # Delete button
        delete_button = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete",
            command=self.delete_product,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=32,
            state="disabled"
        )
        delete_button.grid(row=0, column=2, padx=PADDING_SMALL)
        
        self.action_buttons = {
            'adjust': adjust_button,
            'delete': delete_button
        }
        
        # Right side - Search and filter
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="e")
        
        # Search box
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search products...",
            textvariable=self.search_var,
            width=200,
            height=32
        )
        search_entry.grid(row=0, column=0, padx=PADDING_SMALL)
        
        # Filter dropdown
        filter_values = ["All Products", "Low Stock", "Out of Stock"]
        self.filter_var = ctk.StringVar(value=filter_values[0])
        
        filter_menu = ctk.CTkOptionMenu(
            search_frame,
            values=filter_values,
            variable=self.filter_var,
            command=self.on_filter_change,
            width=120,
            height=32,
            dynamic_resizing=False
        )
        filter_menu.grid(row=0, column=1, padx=(PADDING_SMALL, 0))
    
    def create_content(self):
        """Create main content area with product table"""
        # Table container with border
        container = ctk.CTkFrame(self)
        container.grid(row=2, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Table headers
        headers = [
            "Product ID",
            "Name",
            "Category",
            f"Price ({CURRENCY_SYMBOL})",
            "Stock",
            "Last Updated"
        ]
        
        # Header row with sort buttons
        header_frame = ctk.CTkFrame(container, fg_color=("gray85", "gray25"))
        header_frame.grid(row=0, column=0, sticky="ew")
        
        for col, text in enumerate(headers):
            frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            frame.grid(row=0, column=col, sticky="ew", padx=1)
            frame.grid_columnconfigure(0, weight=1)
            
            btn = ctk.CTkButton(
                frame,
                text=text + " ↕",
                command=lambda c=col: self.sort_table(c),
                fg_color="transparent",
                text_color=("gray20", "gray80"),
                hover_color=("gray75", "gray30"),
                height=32,
                anchor="w"
            )
            btn.grid(row=0, column=0, sticky="ew")
        
        # Table frame
        table_frame = ctk.CTkFrame(container, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create table
        self.table = CTkTable(
            table_frame,
            values=[["" for _ in headers]],
            header_color=("gray85", "gray25"),
            colors=[("white", "gray20"), ("gray95", "gray15")],
            hover_color=("gray90", "gray30"),
            command=self.on_row_select
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        
        # Load initial data
        self.load_products()
    
    def load_products(self):
        """Load products from database"""
        try:
            # Get products
            self.products = self.inventory_service.get_all_products()
            
            # Update stats
            self.update_stats()
            
            # Apply current filter
            self.apply_filter()
            
        except Exception as e:
            self.show_message("Error", f"Failed to load products: {str(e)}")
    
    def update_stats(self):
        """Update statistics labels"""
        low_stock_count = sum(1 for p in self.products if p['stock'] <= p.get('low_stock_threshold', 10))
        
        self.stat_labels['total_products'].configure(text=f"Total Products: {len(self.products)}")
        self.stat_labels['low_stock'].configure(text=f"Low Stock: {low_stock_count}")
    
    def update_table(self, products: List[Dict]):
        """Update table with filtered/sorted products"""
        # Clear selection
        self.selected_product = None
        self.update_button_states()
        
        # Format data for table
        table_data = []
        for product in products:
            # Get last updated time with fallback
            try:
                last_updated = datetime.fromisoformat(product.get('last_updated', '')).strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                last_updated = "N/A"
            
            table_data.append([
                str(product['id']),
                product['name'],
                product['category'],
                f"{product['price']:.2f}",
                str(product['stock']),
                last_updated
            ])
        
        # Update table
        if not table_data:
            table_data = [["No products found"] + ["" for _ in range(5)]]
        
        self.table.update_values(table_data)
    
    def apply_filter(self):
        """Apply current filter and search to products"""
        filtered_products = self.products.copy()
        
        # Apply search
        if self.search_var.get():
            search_term = self.search_var.get().lower()
            filtered_products = [
                p for p in filtered_products
                if search_term in p['name'].lower() or
                search_term in p['category'].lower() or
                search_term in str(p['id'])
            ]
        
        # Apply filter
        filter_type = self.filter_var.get()
        if filter_type == "Low Stock":
            filtered_products = [
                p for p in filtered_products
                if p['stock'] <= p.get('low_stock_threshold', 10) and p['stock'] > 0
            ]
        elif filter_type == "Out of Stock":
            filtered_products = [p for p in filtered_products if p['stock'] == 0]
        
        # Apply sort
        if self.current_sort_column is not None:
            reverse = not self.sort_ascending
            key_map = {
                0: lambda x: x['id'],
                1: lambda x: x['name'].lower(),
                2: lambda x: x['category'].lower(),
                3: lambda x: x['price'],
                4: lambda x: x['stock'],
                5: lambda x: x['last_updated']
            }
            filtered_products.sort(key=key_map[self.current_sort_column], reverse=reverse)
        
        self.update_table(filtered_products)
    
    def sort_table(self, column: int):
        """Sort table by column"""
        if self.current_sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.current_sort_column = column
            self.sort_ascending = True
        
        self.apply_filter()
    
    def on_search(self):
        """Handle search input change"""
        self.apply_filter()
    
    def on_filter_change(self, value: str):
        """Handle filter change"""
        self.apply_filter()
    
    def on_row_select(self, row: int):
        """Handle row selection"""
        if not isinstance(row, int) or row == 0 or not self.products:  # Header row or no products
            return
        
        # Get selected product
        try:
            row_data = self.table.get_row(row)
            if not row_data:
                return
                
            product_id = int(row_data[0])
            self.selected_product = next(p for p in self.products if p['id'] == product_id)
            self.update_button_states()
        except (ValueError, StopIteration, IndexError):
            self.selected_product = None
            self.update_button_states()
    
    def update_button_states(self):
        """Update action button states based on selection"""
        state = "normal" if self.selected_product else "disabled"
        for button in self.action_buttons.values():
            button.configure(state=state)
    
    def add_product(self):
        """Show dialog to add new product"""
        dialog = ProductDialog(self)
        if dialog.result:
            try:
                self.inventory_service.add_product(dialog.result)
                self.load_products()
                self.show_message("Success", "Product added successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to add product: {str(e)}")
    
    def edit_product(self):
        """Show dialog to edit selected product"""
        if not self.selected_product:
            return
        
        dialog = ProductDialog(self, self.selected_product)
        if dialog.result:
            try:
                self.inventory_service.update_product(dialog.result)
                self.load_products()
                self.show_message("Success", "Product updated successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to update product: {str(e)}")
    
    def delete_product(self):
        """Delete selected product"""
        if not self.selected_product:
            return
        
        if self.show_confirmation("Delete Product", f"Are you sure you want to delete {self.selected_product['name']}?"):
            try:
                self.inventory_service.delete_product(self.selected_product['id'])
                self.load_products()
                self.show_message("Success", "Product deleted successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to delete product: {str(e)}")
    
    def adjust_stock(self):
        """Show dialog to adjust stock"""
        if not self.selected_product:
            return
        
        dialog = StockAdjustmentDialog(self, self.selected_product)
        if dialog.result:
            try:
                self.inventory_service.adjust_stock(
                    self.selected_product['id'],
                    dialog.result['quantity'],
                    dialog.result['reason']
                )
                self.load_products()
                self.show_message("Success", "Stock adjusted successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to adjust stock: {str(e)}")
    
    def on_screen_shown(self):
        """Called when screen is shown"""
        self.load_products()

    def navigate_to(self, screen_name: str, data: Optional[Dict] = None):
        """Override navigate_to to include user data"""
        if not data:
            data = {}
        # Include current user data when navigating
        user_data = self.auth_service.get_current_user()
        if user_data:
            data["user"] = user_data
        super().navigate_to(screen_name, data) 