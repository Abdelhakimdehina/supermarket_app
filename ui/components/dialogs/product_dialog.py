import customtkinter as ctk
from typing import Dict, Any, Optional

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM,
    CATEGORIES,
    CURRENCY_SYMBOL
)

class ProductDialog(ctk.CTkToplevel):
    """Dialog for adding/editing products"""
    
    def __init__(self, parent, product: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        
        self.title("Edit Product" if product else "Add Product")
        self.geometry("400x500")
        
        self.product = product
        self.result = None
        
        self.protocol("WM_DELETE_WINDOW", self.cancel)  # Ensure cancel logic on window close
        
        # Create form fields
        self.create_form()
        
        # Populate fields if editing
        if product:
            self.populate_fields()
    
    def create_form(self):
        """Create the form fields"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Name
        row = 0
        ctk.CTkLabel(self, text="Name:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Description
        row += 1
        ctk.CTkLabel(self, text="Description:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.desc_entry = ctk.CTkEntry(self)
        self.desc_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Category
        row += 1
        ctk.CTkLabel(self, text="Category:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(self, variable=self.category_var, values=CATEGORIES)
        self.category_menu.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Barcode
        row += 1
        ctk.CTkLabel(self, text="Barcode:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.barcode_entry = ctk.CTkEntry(self)
        self.barcode_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Price
        row += 1
        ctk.CTkLabel(self, text=f"Price ({CURRENCY_SYMBOL}):").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.price_entry = ctk.CTkEntry(self)
        self.price_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Cost Price
        row += 1
        ctk.CTkLabel(self, text="Cost Price:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.cost_price_entry = ctk.CTkEntry(self)
        self.cost_price_entry.insert(0, "0.0")
        self.cost_price_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Stock
        row += 1
        ctk.CTkLabel(self, text="Stock:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.stock_entry = ctk.CTkEntry(self)
        self.stock_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Low Stock Threshold
        row += 1
        ctk.CTkLabel(self, text="Low Stock Alert:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.threshold_entry = ctk.CTkEntry(self)
        self.threshold_entry.insert(0, "10")  # Default value
        self.threshold_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Buttons
        row += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=PADDING_MEDIUM)
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).pack(side="left", padx=PADDING_SMALL)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        ).pack(side="left", padx=PADDING_SMALL)
    
    def populate_fields(self):
        """Populate form fields with product data"""
        self.name_entry.insert(0, self.product["name"])
        self.desc_entry.insert(0, self.product.get("description", ""))
        self.category_var.set(self.product["category"])
        self.barcode_entry.insert(0, self.product.get("barcode", ""))
        self.price_entry.insert(0, str(self.product["price"]))
        self.stock_entry.insert(0, str(self.product["stock"]))
        self.threshold_entry.insert(0, str(self.product.get("low_stock_threshold", 10)))
    
    def validate(self) -> bool:
        """Validate form inputs"""
        try:
            if not self.name_entry.get().strip():
                raise ValueError("Name is required")
            
            price = float(self.price_entry.get())
            if price < 0:
                raise ValueError("Price must be non-negative")
            
            stock = int(self.stock_entry.get())
            if stock < 0:
                raise ValueError("Stock must be non-negative")
            
            threshold = int(self.threshold_entry.get())
            if threshold < 0:
                raise ValueError("Low stock threshold must be non-negative")
            
            return True
            
        except ValueError as e:
            self.show_error(str(e))
            return False
    
    def show_error(self, message: str):
        """Show error message"""
        ctk.messagebox.showerror("Error", message, parent=self)
    
    def save(self):
        """Save the product data"""
        if self.validate():
            self.result = {
                "name": self.name_entry.get().strip(),
                "description": self.desc_entry.get().strip(),
                "category": self.category_var.get(),
                "barcode": self.barcode_entry.get().strip(),
                "price": float(self.price_entry.get()),
                "stock_quantity": int(self.stock_entry.get()),
                "cost_price": float(self.cost_price_entry.get()),
                "reorder_level": int(self.threshold_entry.get()),
                "image_path": ""
            }
            
            # If editing, preserve the ID
            if self.product:
                self.result["id"] = self.product["id"]
            
            print("[DEBUG] ProductDialog save called, result will be:", self.result)
            self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.destroy()