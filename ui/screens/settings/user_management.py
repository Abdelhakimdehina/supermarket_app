import customtkinter as ctk
from typing import Dict, Any, Optional, List
import tkinter as tk
from tkinter import messagebox

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    ROLES, SCREEN_SETTINGS
)
from ui.base.base_frame import BaseFrame
# Fix the import path
from services.auth_service import AuthService

class UserManagementScreen(BaseFrame):
    """User management screen for the application"""
    
    def __init__(self, master, **kwargs):
        # Initialize services before calling super().__init__
        self.auth_service = AuthService()
        
        super().__init__(master, **kwargs)
        
        # User data
        self.users = []
        self.selected_user = None
        
        # Set background color
        self.configure(fg_color=("#f0f0f0", "#2c3e50"))
    
    def init_ui(self):
        """Initialize UI components"""
        # Create main container with 2 columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_LARGE, pady=PADDING_LARGE)
        
        # Configure content frame grid
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Header
        self.content_frame.grid_rowconfigure(1, weight=1)  # Content
        
        # Create header
        self.create_header()
        
        # Create two-panel layout
        self.create_user_list_panel()
        self.create_user_form_panel()
        
        # Load users
        self.load_users()
    
    def create_header(self):
        """Create header with title and back button"""
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        back_button = ctk.CTkButton(
            header_frame,
            text="← Back to Dashboard",
            command=lambda: self.navigate_to(SCREEN_SETTINGS),
            width=150
        )
        back_button.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM, sticky="w")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="User Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=1, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM, sticky="w")
    
    def create_user_list_panel(self):
        """Create panel with user list"""
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=0)  # Search bar
        list_frame.grid_rowconfigure(1, weight=1)  # User list
        list_frame.grid_rowconfigure(2, weight=0)  # Buttons
        
        # Search bar
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_users)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search users...",
            textvariable=self.search_var,
            width=200
        )
        search_entry.pack(side="left", fill="x", expand=True)
        
        # User list
        list_container = ctk.CTkFrame(list_frame)
        list_container.grid(row=1, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame for user list
        self.users_frame = ctk.CTkScrollableFrame(list_container)
        self.users_frame.grid(row=0, column=0, sticky="nsew")
        self.users_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        add_button = ctk.CTkButton(
            buttons_frame,
            text="Add New User",
            command=self.create_new_user
        )
        add_button.pack(side="left", padx=PADDING_SMALL)
        
        refresh_button = ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            command=self.load_users
        )
        refresh_button.pack(side="left", padx=PADDING_SMALL)
    
    def create_user_form_panel(self):
        """Create panel with user form"""
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.grid(row=1, column=1, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form title
        self.form_title = ctk.CTkLabel(
            form_frame,
            text="User Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Username
        username_label = ctk.CTkLabel(form_frame, text="Username:")
        username_label.grid(row=1, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.username_var = ctk.StringVar()
        self.username_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.username_var,
            width=200
        )
        self.username_entry.grid(row=1, column=1, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Password
        password_label = ctk.CTkLabel(form_frame, text="Password:")
        password_label.grid(row=2, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.password_var,
            show="*",
            width=200
        )
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Full Name
        fullname_label = ctk.CTkLabel(form_frame, text="Full Name:")
        fullname_label.grid(row=3, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.fullname_var = ctk.StringVar()
        self.fullname_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.fullname_var,
            width=200
        )
        self.fullname_entry.grid(row=3, column=1, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Email
        email_label = ctk.CTkLabel(form_frame, text="Email:")
        email_label.grid(row=4, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.email_var = ctk.StringVar()
        self.email_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.email_var,
            width=200
        )
        self.email_entry.grid(row=4, column=1, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Role
        role_label = ctk.CTkLabel(form_frame, text="Role:")
        role_label.grid(row=5, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.role_var = ctk.StringVar()
        self.role_combobox = ctk.CTkComboBox(
            form_frame,
            values=ROLES,
            variable=self.role_var,
            width=200
        )
        self.role_combobox.grid(row=5, column=1, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Active status
        active_label = ctk.CTkLabel(form_frame, text="Active:")
        active_label.grid(row=6, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        self.active_var = ctk.BooleanVar(value=True)
        self.active_switch = ctk.CTkSwitch(
            form_frame,
            text="",
            variable=self.active_var)
        self.active_switch.grid(row=6, column=1, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=self.save_user
        )
        self.save_button.pack(side="left", padx=PADDING_SMALL)
        
        self.delete_button = ctk.CTkButton(
            buttons_frame,
            text="Delete",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.delete_user
        )
        self.delete_button.pack(side="left", padx=PADDING_SMALL)
        
        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.clear_form
        )
        self.cancel_button.pack(side="left", padx=PADDING_SMALL)
        
        # Initially disable form
        self.set_form_state(False)
    
    def set_form_state(self, enabled: bool):
        """Enable or disable form fields"""
        state = "normal" if enabled else "disabled"
        
        self.username_entry.configure(state=state)
        self.password_entry.configure(state=state)
        self.fullname_entry.configure(state=state)
        self.email_entry.configure(state=state)
        self.role_combobox.configure(state=state)
        self.active_switch.configure(state=state)
        
        if enabled:
            self.save_button.configure(state="normal")
            self.cancel_button.configure(state="normal")
            # Only enable delete button if editing an existing user
            if self.selected_user:
                self.delete_button.configure(state="normal")
            else:
                self.delete_button.configure(state="disabled")
        else:
            self.save_button.configure(state="disabled")
            self.cancel_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
    
    def load_users(self):
        """Load users from database"""
        # Clear existing user list
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Get users from service
        self.users = self.auth_service.get_all_users()
        
        # Display users
        self.display_users(self.users)
    
    def display_users(self, users: List[Dict[str, Any]]):
        """Display users in the list"""
        # Clear existing user list
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Add users to list
        for i, user in enumerate(users):
            user_frame = ctk.CTkFrame(self.users_frame)
            user_frame.grid(row=i, column=0, sticky="ew", padx=PADDING_SMALL, pady=PADDING_SMALL)
            user_frame.grid_columnconfigure(1, weight=1)
            
            # Username and role
            username_label = ctk.CTkLabel(
                user_frame,
                text=user["username"],
                font=ctk.CTkFont(weight="bold")
            )
            username_label.grid(row=0, column=0, sticky="w", padx=PADDING_SMALL)
            
            role_label = ctk.CTkLabel(
                user_frame,
                text=f"({user['role']})",
                font=ctk.CTkFont(size=12)
            )
            role_label.grid(row=0, column=1, sticky="w", padx=PADDING_SMALL)
            
            # Full name and email
            info_label = ctk.CTkLabel(
                user_frame,
                text=f"{user['full_name']} - {user['email']}",
                font=ctk.CTkFont(size=12)
            )
            info_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=PADDING_SMALL)
            
            # Active status indicator
            status_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
            status_frame.grid(row=0, column=2, rowspan=2, padx=PADDING_SMALL)
            
            status_color = "#2ecc71" if user["is_active"] else "#e74c3c"
            status_indicator = ctk.CTkLabel(
                status_frame,
                text="●",
                font=ctk.CTkFont(size=16),
                text_color=status_color
            )
            status_indicator.pack()
            
            # Make the entire frame clickable
            user_frame.bind("<Button-1>", lambda event, u=user: self.select_user(u))
            username_label.bind("<Button-1>", lambda event, u=user: self.select_user(u))
    
    def filter_users(self, *args):
        """Filter users based on search text"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            self.display_users(self.users)
            return
        
        filtered_users = [
            user for user in self.users
            if search_text in user["username"].lower() or
               search_text in user["full_name"].lower() or
               search_text in user["email"].lower() or
               search_text in user["role"].lower()
        ]
        
        self.display_users(filtered_users)
    
    def select_user(self, user: Dict[str, Any]):
        """Select a user and populate the form"""
        self.selected_user = user
        
        # Update form title
        self.form_title.configure(text=f"Edit User: {user['username']}")
        
        # Populate form fields
        self.username_var.set(user["username"])
        self.password_var.set("")  # Don't show password
        self.fullname_var.set(user["full_name"] or "")
        self.email_var.set(user["email"] or "")
        self.role_var.set(user["role"])
        self.active_var.set(bool(user["is_active"]))
        
        # Enable form
        self.set_form_state(True)
        
        # Disable username field for existing users
        self.username_entry.configure(state="disabled")
    
    def create_new_user(self):
        """Create a new user"""
        self.selected_user = None
        
        # Update form title
        self.form_title.configure(text="Create New User")
        
        # Clear form fields
        self.clear_form_fields()
        
        # Enable form
        self.set_form_state(True)
        
        # Enable username field for new users
        self.username_entry.configure(state="normal")
    
    def clear_form_fields(self):
        """Clear all form fields"""
        self.username_var.set("")
        self.password_var.set("")
        self.fullname_var.set("")
        self.email_var.set("")
        self.role_var.set(ROLES[0] if ROLES else "")
        self.active_var.set(True)
    
    def clear_form(self):
        """Clear the form and deselect user"""
        self.selected_user = None
        self.clear_form_fields()
        self.form_title.configure(text="User Details")
        self.set_form_state(False)
    
    def save_user(self):
        """Save user (create or update)"""
        # Get form data
        username = self.username_var.get()
        password = self.password_var.get()
        full_name = self.fullname_var.get()
        email = self.email_var.get()
        role = self.role_var.get()
        is_active = self.active_var.get()
        
        # Validate required fields
        if not username:
            messagebox.showerror("Error", "Username is required")
            return
        
        if not self.selected_user and not password:
            messagebox.showerror("Error", "Password is required for new users")
            return
        
        if not role:
            messagebox.showerror("Error", "Role is required")
            return
        
        try:
            if self.selected_user:
                # Update existing user
                result = self.auth_service.update_user(
                    user_id=self.selected_user["id"],
                    password=password if password else None,
                    full_name=full_name,
                    email=email,
                    role=role,
                    is_active=is_active
                )
                
                if result:
                    messagebox.showinfo("Success", f"User {username} updated successfully")
                    self.load_users()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "Failed to update user")
            else:
                # Create new user
                result = self.auth_service.create_user(
                    username=username,
                    password=password,
                    full_name=full_name,
                    email=email,
                    role=role,
                    is_active=is_active
                )
                
                if result:
                    messagebox.showinfo("Success", f"User {username} created successfully")
                    self.load_users()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "Username already exists or other error occurred")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_user(self):
        """Delete the selected user"""
        if not self.selected_user:
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {self.selected_user['username']}?"):
            return
        
        try:
            # Delete user
            result = self.auth_service.delete_user(self.selected_user["id"])
            
            if result:
                messagebox.showinfo("Success", f"User {self.selected_user['username']} deleted successfully")
                self.load_users()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to delete user")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def on_screen_shown(self):
        """Called when the screen is shown"""
        # Load users
        self.load_users()
        
        # Clear form
        self.clear_form()