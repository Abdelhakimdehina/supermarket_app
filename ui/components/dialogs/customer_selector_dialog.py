import customtkinter as ctk
from typing import Optional, Callable, Dict, Any

from config.constants import PADDING_SMALL, PADDING_MEDIUM
from services.customer_service import CustomerService

class CustomerSelectorDialog(ctk.CTkToplevel):
    """Dialog for selecting a customer"""
    
    def __init__(self, parent, callback: Callable[[Optional[Dict[str, Any]]], None]):
        super().__init__(parent)
        
        # Initialize service
        self.customer_service = CustomerService()
        
        # Store callback
        self.callback = callback
        
        # Configure window
        self.title("Select Customer")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Make dialog modal
        self.grab_set()
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Initialize UI
        self.init_ui()
        
        # Load customers
        self.load_customers()
    
    def init_ui(self):
        """Initialize the UI components"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Search frame
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.search_customers())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search customers by name, phone, or email...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=PADDING_SMALL)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_customers
        )
        search_button.grid(row=0, column=1, padx=PADDING_SMALL)
        
        
        # Customer list
        columns = ("Name", "Phone", "Email", "Address")
        
        self.customer_tree = ctk.CTkScrollableFrame(self)
        self.customer_tree.grid(row=2, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        self.customer_tree.grid_columnconfigure(0, weight=3)
        self.customer_tree.grid_columnconfigure(1, weight=2)
        self.customer_tree.grid_columnconfigure(2, weight=3)
        self.customer_tree.grid_columnconfigure(3, weight=4)
        
        # Add headers
        for i, col in enumerate(columns):
            header = ctk.CTkLabel(
                self.customer_tree,
                text=col,
                font=ctk.CTkFont(weight="bold")
            )
            header.grid(row=0, column=i, sticky="w", padx=PADDING_SMALL)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel
        )
        cancel_button.grid(row=0, column=0, padx=PADDING_SMALL)
        
        select_button = ctk.CTkButton(
            button_frame,
            text="Select",
            command=self.select_customer
        )
        select_button.grid(row=0, column=1, padx=PADDING_SMALL)
    
    def load_customers(self):
        """Load all customers"""
        # Clear existing items
        for widget in self.customer_tree.winfo_children()[4:]:  # Skip headers
            widget.destroy()
        
        # Get customers
        customers = self.customer_service.get_customers()
        
        # Add customers to tree
        for i, customer in enumerate(customers):
            row = i + 1  # Skip header row
            
            name_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.name,
                cursor="hand2"
            )
            name_label.grid(row=row, column=0, sticky="w", padx=PADDING_SMALL, pady=2)
            name_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
            
            phone_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.phone or "",
                cursor="hand2"
            )
            phone_label.grid(row=row, column=1, sticky="w", padx=PADDING_SMALL, pady=2)
            phone_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
            
            email_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.email or "",
                cursor="hand2"
            )
            email_label.grid(row=row, column=2, sticky="w", padx=PADDING_SMALL, pady=2)
            email_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
            
            address_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.address or "",
                cursor="hand2"
            )
            address_label.grid(row=row, column=3, sticky="w", padx=PADDING_SMALL, pady=2)
            address_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
    
    def search_customers(self):
        """Search customers"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self.load_customers()
            return
        
        # Clear existing items
        for widget in self.customer_tree.winfo_children()[4:]:  # Skip headers
            widget.destroy()
        
        # Search customers
        customers = self.customer_service.search_customers(search_term)
        
        # Add customers to tree
        for i, customer in enumerate(customers):
            row = i + 1  # Skip header row
            
            name_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.name,
                cursor="hand2"
            )
            name_label.grid(row=row, column=0, sticky="w", padx=PADDING_SMALL, pady=2)
            name_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
            
            phone_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.phone or "",
                cursor="hand2"
            )
            phone_label.grid(row=row, column=1, sticky="w", padx=PADDING_SMALL, pady=2)
            phone_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
            
            email_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.email or "",
                cursor="hand2"
            )
            email_label.grid(row=row, column=2, sticky="w", padx=PADDING_SMALL, pady=2)
            email_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
            
            address_label = ctk.CTkLabel(
                self.customer_tree,
                text=customer.address or "",
                cursor="hand2"
            )
            address_label.grid(row=row, column=3, sticky="w", padx=PADDING_SMALL, pady=2)
            address_label.bind("<Button-1>", lambda e, c=customer: self.on_customer_click(c))
    
    
    def on_customer_click(self, customer: Any):
        """Handle customer selection"""
        self.selected_customer = customer
        self.select_customer()
    
    def select_customer(self):
        """Select the current customer and close dialog"""
        if hasattr(self, 'selected_customer'):
            self.callback(self.selected_customer.to_dict())
        self.destroy()
    
    def cancel(self):
        """Cancel selection and close dialog"""
        self.callback(None)
        self.destroy() 