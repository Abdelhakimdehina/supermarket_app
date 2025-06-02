import os
import sys
import customtkinter as ctk

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from app import SupermarketApp

# Configure customtkinter
ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
ctk.set_widget_scaling(1.0)  # widget dimensions and text size
ctk.set_window_scaling(1.0)  # window dimensions

# Create application instance
app = SupermarketApp()

if __name__ == "__main__":
    app.mainloop()