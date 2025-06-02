import customtkinter as ctk
from typing import Dict, Any, Optional

from config.constants import PADDING_SMALL, PADDING_MEDIUM

class CustomerDialog(ctk.CTkToplevel):
    """Dialog for adding/editing customers"""
    
    def __init__(self, parent, customer_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        
        # Store customer data
        self.customer_data = customer_data
        self.result = None
        
        # Configure window
        self.title("Edit Customer" if customer_data else "Add Customer")
        self.geometry("400x500")
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
        
        # Wait for dialog to close
        self.wait_window()
    
    def init_ui(self):
        """Initialize UI components"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Create form
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        form.grid_columnconfigure(1, weight=1)
        
        # Name field
        ctk.CTkLabel(form, text="Name*").grid(row=0, column=0, sticky="w", pady=(0, PADDING_SMALL))
        self.name_var = ctk.StringVar(value=self.customer_data.get('name', '') if self.customer_data else '')
        name_entry = ctk.CTkEntry(form, textvariable=self.name_var)
        name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, PADDING_MEDIUM))
        
        # Phone field
        ctk.CTkLabel(form, text="Phone").grid(row=2, column=0, sticky="w", pady=(0, PADDING_SMALL))
        self.phone_var = ctk.StringVar(value=self.customer_data.get('phone', '') if self.customer_data else '')
        phone_entry = ctk.CTkEntry(form, textvariable=self.phone_var)
        phone_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, PADDING_MEDIUM))
        
        # Email field
        ctk.CTkLabel(form, text="Email").grid(row=4, column=0, sticky="w", pady=(0, PADDING_SMALL))
        self.email_var = ctk.StringVar(value=self.customer_data.get('email', '') if self.customer_data else '')
        email_entry = ctk.CTkEntry(form, textvariable=self.email_var)
        email_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, PADDING_MEDIUM))
        
        # Address field
        ctk.CTkLabel(form, text="Address").grid(row=6, column=0, sticky="w", pady=(0, PADDING_SMALL))
        self.address_var = ctk.StringVar(value=self.customer_data.get('address', '') if self.customer_data else '')
        address_entry = ctk.CTkEntry(form, textvariable=self.address_var)
        address_entry.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, PADDING_MEDIUM))
        
        # Loyalty points field
        ctk.CTkLabel(form, text="Loyalty Points").grid(row=8, column=0, sticky="w", pady=(0, PADDING_SMALL))
        self.loyalty_points_var = ctk.StringVar(value=str(self.customer_data.get('loyalty_points', 0)) if self.customer_data else '0')
        loyalty_points_entry = ctk.CTkEntry(form, textvariable=self.loyalty_points_var)
        loyalty_points_entry.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, PADDING_MEDIUM))
        
        # Required fields note
        note = ctk.CTkLabel(
            form,
            text="* Required fields",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        note.grid(row=10, column=0, columnspan=2, sticky="w", pady=(0, PADDING_MEDIUM))
        
        # Buttons
        button_frame = ctk.CTkFrame(form, fg_color="transparent")
        button_frame.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(PADDING_MEDIUM, 0))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            fg_color="transparent",
            text_color=("gray20", "gray80"),
            hover_color=("gray70", "gray30")
        )
        cancel_button.grid(row=0, column=0, padx=PADDING_SMALL)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save
        )
        save_button.grid(row=0, column=1, padx=PADDING_SMALL)
    
    def validate(self) -> bool:
        """Validate form data"""
        # Name is required
        if not self.name_var.get().strip():
            self.show_error("Name is required")
            return False
        
        # Phone must be numeric if provided
        phone = self.phone_var.get().strip()
        if phone and not phone.isdigit():
            self.show_error("Phone must contain only digits")
            return False
        
        # Loyalty points must be numeric
        try:
            loyalty_points = int(self.loyalty_points_var.get().strip() or '0')
            if loyalty_points < 0:
                self.show_error("Loyalty points cannot be negative")
                return False
        except ValueError:
            self.show_error("Loyalty points must be a number")
            return False
        
        return True
    
    def show_error(self, message: str):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("300x100")
        error_dialog.resizable(False, False)
        error_dialog.grab_set()
        
        # Center the dialog
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() - error_dialog.winfo_width()) // 2
        y = (error_dialog.winfo_screenheight() - error_dialog.winfo_height()) // 2
        error_dialog.geometry(f"+{x}+{y}")
        
        # Add message
        ctk.CTkLabel(
            error_dialog,
            text=message,
            wraplength=250
        ).grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Add OK button
        ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy
        ).grid(row=1, column=0, pady=(0, PADDING_MEDIUM))
    
    def save(self):
        """Save customer data and close dialog"""
        if not self.validate():
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'email': self.email_var.get().strip(),
            'address': self.address_var.get().strip(),
            'loyalty_points': int(self.loyalty_points_var.get().strip() or '0')
        }
        
        self.destroy()
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.destroy() 