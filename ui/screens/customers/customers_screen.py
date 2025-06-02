import customtkinter as ctk
from typing import Dict, Any, Optional, List
from CTkTable import CTkTable

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    SCREEN_DASHBOARD
)
from ui.base.base_frame import BaseFrame
from services.customer_service import CustomerService
from services.auth_service import AuthService
from ui.components.dialogs.customer_dialog import CustomerDialog
from database.models.customer import Customer

class CustomersScreen(BaseFrame):
    """Customers management screen"""
    
    def __init__(self, master, **kwargs):
        # Initialize services
        self.customer_service = CustomerService()
        self.auth_service = AuthService()
        
        # Initialize state
        self.customers = []
        self.selected_customer = None
        self.current_sort_column = None
        self.sort_ascending = True
        
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
        
        # Create customer table
        self.create_table()
        
        # Load initial data
        self.load_customers()
    
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
            text="👥 Customer Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.grid(row=0, column=1, sticky="w")
        
        # Stats summary
        stats_frame = ctk.CTkFrame(header, fg_color=("gray90", "gray20"))
        stats_frame.grid(row=0, column=2, padx=(PADDING_MEDIUM, 0))
        
        self.total_customers_label = ctk.CTkLabel(
            stats_frame,
            text="Total Customers: 0",
            font=ctk.CTkFont(size=12),
            padx=PADDING_MEDIUM,
            pady=PADDING_SMALL
        )
        self.total_customers_label.grid(row=0, column=0)
    
    def create_toolbar(self):
        """Create toolbar with actions and search"""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        toolbar.grid_columnconfigure(1, weight=1)
        
        # Left side - Action buttons
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.grid(row=0, column=0, sticky="w")
        
        # Add Customer button
        add_button = ctk.CTkButton(
            actions_frame,
            text="+ Add Customer",
            command=self.add_customer,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=32
        )
        add_button.grid(row=0, column=0, padx=(0, PADDING_SMALL))
        
        # Edit button
        self.edit_button = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            command=self.edit_customer,
            fg_color="#3498db",
            hover_color="#2980b9",
            height=32,
            state="disabled"
        )
        self.edit_button.grid(row=0, column=1, padx=PADDING_SMALL)
        
        # Delete button
        self.delete_button = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete",
            command=self.delete_customer,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=32,
            state="disabled"
        )
        self.delete_button.grid(row=0, column=2, padx=PADDING_SMALL)
        
        # Right side - Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="e")
        
        # Search box
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search customers...",
            textvariable=self.search_var,
            width=200,
            height=32
        )
        search_entry.grid(row=0, column=0, padx=PADDING_SMALL)
    
    def create_table(self):
        """Create customer table"""
        # Table container with border
        container = ctk.CTkFrame(self)
        container.grid(row=2, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Table headers
        headers = [
            "ID",
            "Name",
            "Phone",
            "Email",
            "Address",
            "Loyalty Points",
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
    
    def load_customers(self):
        """Load customers from database"""
        try:
            # Get customers
            self.customers = self.customer_service.get_customers()
            
            # Update stats
            self.total_customers_label.configure(text=f"Total Customers: {len(self.customers)}")
            
            # Apply current filter
            self.apply_filter()
            
        except Exception as e:
            self.show_message("Error", f"Failed to load customers: {str(e)}")
    
    def update_table(self, customers: List[Customer]):
        """Update table with filtered/sorted customers"""
        # Clear selection
        self.selected_customer = None
        self.update_button_states()
        
        # Format data for table
        table_data = []
        for customer in customers:
            table_data.append([
                str(customer.id),
                customer.name,
                customer.phone,
                customer.email,
                customer.address,
                str(customer.loyalty_points),
                customer.updated_at
            ])
        
        # Update table
        if not table_data:
            table_data = [["No customers found"] + ["" for _ in range(6)]]
        
        self.table.update_values(table_data)
    
    def apply_filter(self):
        """Apply current filter and search to customers"""
        filtered_customers = self.customers.copy()
        
        # Apply search
        if self.search_var.get():
            search_term = self.search_var.get().lower()
            filtered_customers = [
                c for c in filtered_customers
                if search_term in c.name.lower() or
                search_term in str(c.phone).lower() or
                search_term in str(c.email).lower()
            ]
        
        # Apply sort
        if self.current_sort_column is not None:
            reverse = not self.sort_ascending
            key_map = {
                0: lambda x: x.id,
                1: lambda x: x.name.lower(),
                2: lambda x: str(x.phone).lower(),
                3: lambda x: str(x.email).lower(),
                4: lambda x: str(x.address).lower(),
                5: lambda x: x.loyalty_points,
                6: lambda x: x.updated_at
            }
            filtered_customers.sort(key=key_map[self.current_sort_column], reverse=reverse)
        
        self.update_table(filtered_customers)
    
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
    
    def on_row_select(self, row: int):
        """Handle row selection"""
        if not isinstance(row, int) or row == 0 or not self.customers:  # Header row or no customers
            return
        
        # Get selected customer
        try:
            row_data = self.table.get_row(row)
            if not row_data:
                return
                
            customer_id = int(row_data[0])
            self.selected_customer = next(c for c in self.customers if c.id == customer_id)
            self.update_button_states()
        except (ValueError, StopIteration, IndexError):
            self.selected_customer = None
            self.update_button_states()
    
    def update_button_states(self):
        """Update action button states based on selection"""
        state = "normal" if self.selected_customer else "disabled"
        self.edit_button.configure(state=state)
        self.delete_button.configure(state=state)
    
    def add_customer(self):
        """Show dialog to add new customer"""
        dialog = CustomerDialog(self)
        if dialog.result:
            try:
                self.customer_service.create_customer(dialog.result)
                self.load_customers()
                self.show_message("Success", "Customer added successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to add customer: {str(e)}")
    
    def edit_customer(self):
        """Show dialog to edit selected customer"""
        if not self.selected_customer:
            return
        
        dialog = CustomerDialog(self, self.selected_customer.to_dict())
        if dialog.result:
            try:
                self.customer_service.update_customer(self.selected_customer.id, dialog.result)
                self.load_customers()
                self.show_message("Success", "Customer updated successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to update customer: {str(e)}")
    
    def delete_customer(self):
        """Delete selected customer"""
        if not self.selected_customer:
            return
        
        if self.show_confirmation("Delete Customer", f"Are you sure you want to delete {self.selected_customer.name}?"):
            try:
                self.customer_service.delete_customer(self.selected_customer.id)
                self.load_customers()
                self.show_message("Success", "Customer deleted successfully!")
            except Exception as e:
                self.show_message("Error", f"Failed to delete customer: {str(e)}")
    
    def on_screen_shown(self):
        """Called when screen is shown"""
        self.load_customers() 