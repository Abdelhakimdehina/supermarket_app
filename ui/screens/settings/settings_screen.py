import customtkinter as ctk
from typing import Dict, Any
import json
import os

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    SCREEN_DASHBOARD
)
from ui.base.base_frame import BaseFrame
from services.auth_service import AuthService

class SettingsScreen(BaseFrame):
    """Settings screen for the application"""
    
    def __init__(self, master, **kwargs):
        # Initialize services
        self.auth_service = AuthService()
        
        # Load settings
        self.settings = self.load_settings()
        
        super().__init__(master, **kwargs)
        
        # Set background color
        self.configure(fg_color=("#f0f0f0", "#2c3e50"))
    
    def init_ui(self):
        """Initialize UI components"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.create_header()
        
        # Create main content
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        content.grid_columnconfigure(0, weight=1)
        
        # Appearance section
        self.create_appearance_section(content)
        
        # Add more sections here as needed
        
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
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        title.grid(row=0, column=1, sticky="w")
    
    def create_appearance_section(self, parent):
        """Create appearance settings section"""
        # Section frame
        section = ctk.CTkFrame(parent)
        section.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        section.grid_columnconfigure(1, weight=1)
        
        # Section title
        title = ctk.CTkLabel(
            section,
            text="🎨 Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Theme setting
        theme_label = ctk.CTkLabel(
            section,
            text="Theme Mode:",
            font=ctk.CTkFont(size=14)
        )
        theme_label.grid(row=1, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Theme options
        theme_var = ctk.StringVar(value=self.settings.get('theme', 'system'))
        
        themes_frame = ctk.CTkFrame(section, fg_color="transparent")
        themes_frame.grid(row=1, column=1, sticky="w", padx=PADDING_MEDIUM)
        
        themes = [
            ("System", "system"),
            ("Light", "light"),
            ("Dark", "dark")
        ]
        
        for i, (text, value) in enumerate(themes):
            radio = ctk.CTkRadioButton(
                themes_frame,
                text=text,
                value=value,
                variable=theme_var,
                command=lambda: self.change_theme(theme_var.get())
            )
            radio.grid(row=0, column=i, padx=(0 if i == 0 else PADDING_MEDIUM))
        
        # Add separator
        separator = ctk.CTkFrame(section, height=1, fg_color=("gray70", "gray30"))
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Color scheme (placeholder for future enhancement)
        color_label = ctk.CTkLabel(
            section,
            text="Color Scheme:",
            font=ctk.CTkFont(size=14)
        )
        color_label.grid(row=3, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        color_value = ctk.CTkLabel(
            section,
            text="Default (Coming Soon)",
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        )
        color_value.grid(row=3, column=1, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
    
    def change_theme(self, theme: str):
        """Change application theme"""
        # Update customtkinter appearance mode
        ctk.set_appearance_mode(theme)
        
        # Save settings
        self.settings['theme'] = theme
        self.save_settings()
    
    def load_settings(self) -> Dict:
        """Load application settings from file"""
        settings_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'settings.json')
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Return default settings
        return {'theme': 'system'}
    
    def save_settings(self):
        """Save application settings to file"""
        settings_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'settings.json')
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_screen_shown(self):
        """Called when screen is shown"""
        pass 