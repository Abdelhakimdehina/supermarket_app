import customtkinter as ctk

class ScrollableFrame(ctk.CTkScrollableFrame):
    """Enhanced scrollable frame with additional functionality"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
    
    def clear(self):
        """Remove all widgets from the frame"""
        for widget in self.winfo_children():
            widget.destroy()