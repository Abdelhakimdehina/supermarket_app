import os
import customtkinter as ctk
from PIL import Image
from typing import Optional, Tuple, Dict, Any
from tkinter import messagebox

from config.settings import LOGO_PATH, APP_NAME
from config.constants import PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE, SCREEN_DASHBOARD, SCREEN_CASHIER_MAIN, ROLES
from ui.base.base_frame import BaseFrame
from services.auth_service import AuthService
from utils.session import SessionManager

class LoginScreen(BaseFrame):
    """Login screen for the application"""
    
    def __init__(self, master, **kwargs):
        """Initialize the login screen"""
        super().__init__(master, **kwargs)
        
        # Initialize services
        self.auth_service = AuthService()
        self.session_manager = SessionManager()
        
        # Set background color
        self.configure(fg_color=("#f0f0f0", "#2c3e50"))
    
    def init_ui(self):
        """Initialize UI components"""
        # Create main container frame
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=PADDING_LARGE, pady=PADDING_LARGE)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create login form frame
        self.login_frame = ctk.CTkFrame(self.container)
        self.login_frame.grid(row=0, column=0, padx=PADDING_LARGE, pady=PADDING_LARGE)
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        # Add logo if exists
        self.logo_image = None
        if os.path.exists(LOGO_PATH):
            try:
                image = Image.open(LOGO_PATH)
                self.logo_image = ctk.CTkImage(light_image=image, dark_image=image, size=(100, 100))
                logo_label = ctk.CTkLabel(self.login_frame, image=self.logo_image, text="")
                logo_label.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Add title
        title_label = ctk.CTkLabel(
            self.login_frame, 
            text=APP_NAME, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=1, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Add welcome message
        welcome_label = ctk.CTkLabel(
            self.login_frame, 
            text="Welcome! Please log in to continue.", 
            font=ctk.CTkFont(size=14)
        )
        welcome_label.grid(row=2, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Username field
        self.username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Username",
            width=300,
            textvariable=self.username_var
        )
        username_entry.grid(row=3, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Password field
        self.password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Password",
            width=300, 
            show="*",
            textvariable=self.password_var
        )
        password_entry.grid(row=4, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Remember me checkbox
        self.remember_var = ctk.BooleanVar(value=False)
        remember_checkbox = ctk.CTkCheckBox(
            self.login_frame, 
            text="Remember me", 
            variable=self.remember_var
        )
        remember_checkbox.grid(row=5, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL, sticky="w")
        
        # Forgot password link
        forgot_button = ctk.CTkButton(
            self.login_frame, 
            text="Forgot Password?", 
            font=ctk.CTkFont(size=12, underline=True),
            fg_color="transparent", 
            hover=False,
            command=self.forgot_password
        )
        forgot_button.grid(row=6, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Login button
        login_button = ctk.CTkButton(
            self.login_frame, 
            text="Login",
            width=300,
            command=self.login
        )
        login_button.grid(row=7, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Create account button
        create_account_button = ctk.CTkButton(
            self.login_frame,
            text="Create New Account",
            width=300,
            fg_color="#2980b9",
            hover_color="#3498db",
            command=self.show_create_account_dialog
        )
        create_account_button.grid(row=8, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Error message label
        self.error_label = ctk.CTkLabel(
            self.login_frame, 
            text="",
            text_color="#e74c3c",
            font=ctk.CTkFont(size=12)
        )
        self.error_label.grid(row=9, column=0, padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Set focus to username entry
        username_entry.focus()
        
        # Bind Enter key to login
        username_entry.bind("<Return>", lambda e: self.login())
        password_entry.bind("<Return>", lambda e: self.login())
    
    def login(self):
        """Handle login button click"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return
        
        # Authenticate user
        user = self.auth_service.authenticate(username, password)
        
        if user:
            # Clear error message
            self.error_label.configure(text="")
            
            # Save session if remember me is checked
            self.session_manager.set_user(user, remember=self.remember_var.get())
            
            # Navigate based on role
            if user.get('role') == 'admin':
                self.navigate_to(SCREEN_DASHBOARD, {"user": user})
            elif user.get('role') == 'cashier':
                self.navigate_to(SCREEN_CASHIER_MAIN, {"user": user})
            else:
                # Default navigation or error
                messagebox.showerror("Login Error", "Invalid user role.")
        else:
            self.error_label.configure(text="Invalid username or password")
    
    def forgot_password(self):
        """Handle forgot password link click"""
        # For now, just show a message
        self.error_label.configure(
            text="Please contact your administrator to reset your password",
            text_color="#3498db"
        )
    
    def show_create_account_dialog(self):
        """Show dialog to create a new user account"""
        # Create a toplevel window for the registration form
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Account")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.grab_set()  # Make the dialog modal
        
        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create form frame
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Title
        title_label = ctk.CTkLabel(
            form_frame,
            text="Create New Account",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=PADDING_MEDIUM)
        
        # Form fields
        # Username
        username_label = ctk.CTkLabel(form_frame, text="Username:")
        username_label.pack(anchor="w", padx=PADDING_MEDIUM, pady=(PADDING_MEDIUM, PADDING_SMALL))
        username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(form_frame, width=400, textvariable=username_var)
        username_entry.pack(padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Password
        password_label = ctk.CTkLabel(form_frame, text="Password:")
        password_label.pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(form_frame, width=400, textvariable=password_var, show="*")
        password_entry.pack(padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Confirm Password
        confirm_password_label = ctk.CTkLabel(form_frame, text="Confirm Password:")
        confirm_password_label.pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        confirm_password_var = ctk.StringVar()
        confirm_password_entry = ctk.CTkEntry(form_frame, width=400, textvariable=confirm_password_var, show="*")
        confirm_password_entry.pack(padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Full Name
        full_name_label = ctk.CTkLabel(form_frame, text="Full Name:")
        full_name_label.pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        full_name_var = ctk.StringVar()
        full_name_entry = ctk.CTkEntry(form_frame, width=400, textvariable=full_name_var)
        full_name_entry.pack(padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Email
        email_label = ctk.CTkLabel(form_frame, text="Email:")
        email_label.pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        email_var = ctk.StringVar()
        email_entry = ctk.CTkEntry(form_frame, width=400, textvariable=email_var)
        email_entry.pack(padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Role
        role_label = ctk.CTkLabel(form_frame, text="Role:")
        role_label.pack(anchor="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))
        role_var = ctk.StringVar(value="user")
        role_combobox = ctk.CTkComboBox(form_frame, width=400, values=list(ROLES.keys()), variable=role_var)
        role_combobox.pack(padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Error message label
        error_var = ctk.StringVar()
        error_label = ctk.CTkLabel(form_frame, textvariable=error_var, text_color="#e74c3c")
        error_label.pack(pady=PADDING_SMALL)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(pady=PADDING_MEDIUM)
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=180,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=dialog.destroy
        )
        cancel_button.grid(row=0, column=0, padx=PADDING_SMALL)
        
        # Create button
        def create_user():
            # Get form values
            username = username_var.get().strip()
            password = password_var.get()
            confirm_password = confirm_password_var.get()
            full_name = full_name_var.get().strip()
            email = email_var.get().strip()
            role = role_var.get()
            
            # Validate form
            if not username or not password or not confirm_password or not full_name or not email:
                error_var.set("All fields are required")
                return
            
            if password != confirm_password:
                error_var.set("Passwords do not match")
                return
            
            # Create user
            user_data = {
                'username': username,
                'password': password,
                'full_name': full_name,
                'email': email,
                'role': role
            }
            
            result = self.auth_service.create_user(user_data)
            
            if result:
                messagebox.showinfo("Success", "Account created successfully! You can now log in.")
                dialog.destroy()
            else:
                error_var.set("Username already exists or there was an error creating the account")
        
        create_button = ctk.CTkButton(
            buttons_frame,
            text="Create Account",
            width=180,
            fg_color="#27ae60",
            hover_color="#2ecc71",
            command=create_user
        )
        create_button.grid(row=0, column=1, padx=PADDING_SMALL)
    
    def on_screen_shown(self):
        """Called when screen is shown"""
        # Check for saved session
        self.check_saved_session()
    
    def check_saved_session(self):
        """Check for saved session and auto-login if found"""
        # Get current user from session
        user = self.session_manager.get_user()
        if user:
            # User is already logged in, navigate based on role
            role = user.get('role')
            if role == 'admin':
                self.navigate_to(SCREEN_DASHBOARD, {"user": user})
            elif role == 'cashier':
                self.navigate_to(SCREEN_CASHIER_MAIN, {"user": user})
            else:
                # Invalid role in session, clear it
                self.session_manager.clear_session()