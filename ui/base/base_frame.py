import customtkinter as ctk
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from ui.app import App

class BaseFrame(ctk.CTkFrame):
    """Base frame for all screens"""
    
    def __init__(self, master, **kwargs):
        """Initialize the frame"""
        super().__init__(master, **kwargs)
        
        # Store reference to main app
        self.app = master
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize UI components
        try:
            self.init_ui()
        except Exception as e:
            print(f"Error initializing UI: {e}")
            # Show error message in frame
            error_label = ctk.CTkLabel(
                self,
                text="Error initializing screen.\nPlease restart the application.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="red"
            )
            error_label.grid(row=0, column=0, padx=20, pady=20)
    
    def init_ui(self):
        """Initialize UI components - to be overridden by subclasses"""
        pass
    
    def on_screen_shown(self):
        """Called when screen is shown - to be overridden by subclasses"""
        pass
    
    def receive_data(self, data: Dict[str, Any]):
        """Receive data from another screen - to be overridden by subclasses"""
        pass
    
    def navigate_to(self, screen_name: str, data: Optional[Dict[str, Any]] = None):
        """Navigate to another screen"""
        self.app.show_screen(screen_name, data)
    
    def show_message(self, title: str, message: str):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Message
        message_label = ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=250
        )
        message_label.pack(pady=20)
        
        # OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        ok_button.pack(pady=10)