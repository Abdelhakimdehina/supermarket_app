import customtkinter as ctk
from typing import Dict, Any, Optional
from datetime import datetime

from config.constants import PADDING_SMALL, PADDING_MEDIUM

class StockAdjustmentDialog(ctk.CTkToplevel):
    """Dialog for adjusting product stock"""
    
    def __init__(self, parent, product: Dict[str, Any]):
        super().__init__(parent)
        
        self.title(f"Adjust Stock - {product['name']}")
        self.geometry("400x300")
        
        self.product = product
        self.result = None
        
        # Create form fields
        self.create_form()
    
    def create_form(self):
        """Create the form fields"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Current stock display
        row = 0
        ctk.CTkLabel(
            self,
            text="Current Stock:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        
        ctk.CTkLabel(
            self,
            text=str(self.product['stock']),
            font=ctk.CTkFont(size=16)
        ).grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="w")
        
        # Adjustment quantity
        row += 1
        ctk.CTkLabel(self, text="Quantity:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.quantity_entry = ctk.CTkEntry(self)
        self.quantity_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Note about positive/negative values
        row += 1
        ctk.CTkLabel(
            self,
            text="(Use positive numbers to add stock, negative to remove)",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        ).grid(row=row, column=1, padx=PADDING_SMALL, sticky="w")
        
        # Reason for adjustment
        row += 1
        ctk.CTkLabel(self, text="Reason:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.reason_var = ctk.StringVar(value="Manual Adjustment")
        self.reason_menu = ctk.CTkOptionMenu(
            self,
            variable=self.reason_var,
            values=[
                "Manual Adjustment",
                "Stock Count",
                "Damaged/Lost",
                "Returned Items",
                "Other"
            ]
        )
        self.reason_menu.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Notes
        row += 1
        ctk.CTkLabel(self, text="Notes:").grid(row=row, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="e")
        self.notes_entry = ctk.CTkTextbox(self, height=60)
        self.notes_entry.grid(row=row, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Preview new stock
        row += 1
        preview_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        preview_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        preview_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            preview_frame,
            text="New Stock Level:",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text=str(self.product['stock']),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.preview_label.grid(row=0, column=1, padx=PADDING_MEDIUM, pady=PADDING_SMALL, sticky="w")
        
        # Bind quantity entry to update preview
        self.quantity_entry.bind('<KeyRelease>', self.update_preview)
        
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
    
    def update_preview(self, event=None):
        """Update the preview of new stock level"""
        try:
            adjustment = int(self.quantity_entry.get() or 0)
            new_stock = self.product['stock'] + adjustment
            self.preview_label.configure(
                text=str(new_stock),
                text_color="#2ecc71" if new_stock > self.product['stock'] else 
                          "#e74c3c" if new_stock < self.product['stock'] else
                          None
            )
        except ValueError:
            self.preview_label.configure(
                text=str(self.product['stock']),
                text_color=None
            )
    
    def validate(self) -> bool:
        """Validate form inputs"""
        try:
            quantity = int(self.quantity_entry.get())
            if quantity == 0:
                raise ValueError("Quantity cannot be zero")
            
            new_stock = self.product['stock'] + quantity
            if new_stock < 0:
                raise ValueError("Cannot reduce stock below zero")
            
            return True
            
        except ValueError as e:
            self.show_error(str(e))
            return False
    
    def show_error(self, message: str):
        """Show error message"""
        ctk.messagebox.showerror("Error", message, parent=self)
    
    def save(self):
        """Save the stock adjustment"""
        if self.validate():
            self.result = {
                'quantity': int(self.quantity_entry.get()),
                'reason': self.reason_var.get(),
                'notes': self.notes_entry.get("1.0", "end-1c"),
                'timestamp': datetime.now().isoformat()
            }
            self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.destroy() 