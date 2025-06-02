import customtkinter as ctk
from tkinter import ttk
from typing import Dict, Any, Optional

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    CATEGORIES
)
from ui.base.base_frame import BaseFrame
from services.inventory_service import InventoryService

class ProductDialog(ctk.CTkToplevel):
    """Dialog for adding/editing products"""
    
    def __init__(self, parent, product: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        
        self.title("Edit Product" if product else "Add Product")
        self.geometry("400x500")
        
        self.product = product
        self.result = None
        
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
        ctk.CTkLabel(self, text="Price:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.price_entry = ctk.CTkEntry(self)
        self.price_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Stock
        row += 1
        ctk.CTkLabel(self, text="Stock:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.stock_entry = ctk.CTkEntry(self)
        self.stock_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Buttons
        row += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=PADDING_MEDIUM)
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save
        ).pack(side="left", padx=PADDING_SMALL)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side="left", padx=PADDING_SMALL)
    
    def populate_fields(self):
        """Populate form fields with product data"""
        self.name_entry.insert(0, self.product["name"])
        self.desc_entry.insert(0, self.product.get("description", ""))
        self.category_var.set(self.product["category"])
        self.barcode_entry.insert(0, self.product.get("barcode", ""))
        self.price_entry.insert(0, str(self.product["price"]))
        self.stock_entry.insert(0, str(self.product["stock"]))
    
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
            
            return True
            
        except ValueError as e:
            self.show_error(str(e))
            return False
    
    def show_error(self, message: str):
        """Show error message"""
        ctk.messagebox.showerror("Error", message)
    
    def save(self):
        """Save the product data"""
        if self.validate():
            self.result = {
                "name": self.name_entry.get().strip(),
                "description": self.desc_entry.get().strip(),
                "category": self.category_var.get(),
                "barcode": self.barcode_entry.get().strip(),
                "price": float(self.price_entry.get()),
                "stock": int(self.stock_entry.get())
            }
            self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.destroy()

class StockAdjustmentDialog(ctk.CTkToplevel):
    """Dialog for adjusting stock"""
    
    def __init__(self, parent, product_name: str):
        super().__init__(parent)
        
        self.title(f"Adjust Stock - {product_name}")
        self.geometry("300x200")
        
        self.result = None
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Quantity
        row = 0
        ctk.CTkLabel(self, text="Quantity:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Note: Positive for additions, negative for removals
        row += 1
        ctk.CTkLabel(
            self,
            text="(Use positive numbers to add stock, negative to remove)",
            font=("", 10)
        ).grid(row=row, column=1, padx=PADDING_SMALL, sticky="w")
        
        # Buttons
        row += 1
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=PADDING_MEDIUM)
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save
        ).pack(side="left", padx=PADDING_SMALL)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel
        ).pack(side="left", padx=PADDING_SMALL)
    
    def validate(self) -> bool:
        """Validate form inputs"""
        try:
            quantity = int(self.quantity_entry.get())
            if quantity == 0:
                raise ValueError("Quantity cannot be zero")
            return True
        except ValueError as e:
            ctk.messagebox.showerror("Error", str(e))
            return False
    
    def save(self):
        """Save the adjustment"""
        if self.validate():
            self.result = int(self.quantity_entry.get())
            self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.destroy()

class InventoryScreen(BaseFrame):
    """Inventory management screen"""
    
    def __init__(self, master, **kwargs):
        self.inventory_service = InventoryService()
        super().__init__(master, **kwargs)
    
    def init_ui(self):
        """Initialize the UI components"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Create header
        self.create_header()
        
        # Create search bar
        self.create_search_bar()
        
        # Create product table
        self.create_product_table()
        
        # Load products
        self.load_products()
    
    def create_header(self):
        """Create the header section"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        header.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            header,
            text="Inventory Management",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Add Product button
        ctk.CTkButton(
            header,
            text="Add Product",
            command=self.add_product
        ).grid(row=0, column=2, padx=PADDING_SMALL)
    
    def create_search_bar(self):
        """Create the search bar"""
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM)
        search_frame.grid_columnconfigure(0, weight=1)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search products..."
        )
        self.search_entry.grid(row=0, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        self.search_entry.bind("<Return>", lambda e: self.search_products())
        
        # Search button
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_products
        ).grid(row=0, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL)
    
    def create_product_table(self):
        """Create the product table"""
        # Create frame for treeview
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("name", "category", "price", "stock", "barcode"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("name", text="Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("price", text="Price")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("barcode", text="Barcode")
        
        self.tree.column("name", width=200)
        self.tree.column("category", width=150)
        self.tree.column("price", width=100)
        self.tree.column("stock", width=100)
        self.tree.column("barcode", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind double-click
        self.tree.bind("<Double-1>", self.edit_selected_product)
        
        # Create context menu
        self.context_menu = self.create_context_menu()
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def create_context_menu(self) -> ctk.CTkFrame:
        """Create the context menu"""
        menu = ctk.CTkFrame(self)
        
        ctk.CTkButton(
            menu,
            text="Edit",
            command=lambda: self.edit_selected_product()
        ).pack(fill="x", padx=1, pady=1)
        
        ctk.CTkButton(
            menu,
            text="Adjust Stock",
            command=self.adjust_selected_stock
        ).pack(fill="x", padx=1, pady=1)
        
        ctk.CTkButton(
            menu,
            text="Delete",
            command=self.delete_selected_product,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(fill="x", padx=1, pady=1)
        
        return menu
    
    def show_context_menu(self, event):
        """Show the context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.place(x=event.x_root, y=event.y_root)
            self.bind("<Button-1>", self.hide_context_menu)
    
    def hide_context_menu(self, event=None):
        """Hide the context menu"""
        self.context_menu.place_forget()
        if event:
            self.unbind("<Button-1>")
    
    def load_products(self):
        """Load all products into the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load products
        products = self.inventory_service.get_all_products()
        
        # Add to table
        for product in products:
            self.tree.insert("", "end",
                values=(
                    product["name"],
                    product["category"],
                    f"${product['price']:.2f}",
                    product["stock"],
                    product.get("barcode", "")
                ),
                tags=(str(product["id"]),)
            )
    
    def search_products(self):
        """Search products"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_products()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search products
        products = self.inventory_service.search_products(search_term)
        
        # Add to table
        for product in products:
            self.tree.insert("", "end",
                values=(
                    product["name"],
                    product["category"],
                    f"${product['price']:.2f}",
                    product["stock"],
                    product.get("barcode", "")
                ),
                tags=(str(product["id"]),)
            )
    
    def get_selected_product(self) -> Optional[Dict[str, Any]]:
        """Get the selected product"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        product_id = int(self.tree.item(selection[0])["tags"][0])
        return self.inventory_service.get_product(product_id)
    
    def add_product(self):
        """Add a new product"""
        dialog = ProductDialog(self)
        self.wait_window(dialog)
        
        if dialog.result:
            if self.inventory_service.add_product(dialog.result):
                self.load_products()
            else:
                self.show_error("Failed to add product")
    
    def edit_selected_product(self, event=None):
        """Edit the selected product"""
        product = self.get_selected_product()
        if not product:
            return
        
        dialog = ProductDialog(self, product)
        self.wait_window(dialog)
        
        if dialog.result:
            if self.inventory_service.update_product(product["id"], dialog.result):
                self.load_products()
            else:
                self.show_error("Failed to update product")
    
    def adjust_selected_stock(self):
        """Adjust stock for selected product"""
        product = self.get_selected_product()
        if not product:
            return
        
        dialog = StockAdjustmentDialog(self, product["name"])
        self.wait_window(dialog)
        
        if dialog.result is not None:
            if self.inventory_service.adjust_stock(product["id"], dialog.result):
                self.load_products()
            else:
                self.show_error("Failed to adjust stock")
    
    def delete_selected_product(self):
        """Delete the selected product"""
        product = self.get_selected_product()
        if not product:
            return
        
        if ctk.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {product['name']}?"
        ):
            if self.inventory_service.delete_product(product["id"]):
                self.load_products()
            else:
                self.show_error("Failed to delete product")
    
    def show_error(self, message: str):
        """Show error message"""
        ctk.messagebox.showerror("Error", message)
    
    def on_screen_shown(self):
        """Called when screen is shown"""
        self.load_products() 