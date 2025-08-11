import customtkinter as ctk

from config.constants import PADDING_MEDIUM, SCREEN_LOGIN, SCREEN_POS
from utils.session import SessionManager
from ui.base.base_frame import BaseFrame
from ui.screens.pos.pos_screen import POSScreen

class CashierMainScreen(BaseFrame):
    """Main screen for cashier, only showing the POS."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.session_manager = SessionManager()

        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # POS Screen
        self.grid_columnconfigure(0, weight=1)

        # Header Frame
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(header_frame, text="Cashier Point of Sale", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)

        logout_button = ctk.CTkButton(header_frame, text="Logout", command=self.logout)
        logout_button.grid(row=0, column=1, sticky="e", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)

        # Embed the POS screen
        self.pos_screen = POSScreen(self, **kwargs)
        self.pos_screen.grid(row=1, column=0, sticky="nsew")

    def logout(self):
        """Logs the user out and returns to the login screen."""
        self.session_manager.clear_session()
        self.navigate_to(SCREEN_LOGIN)

    def on_screen_shown(self):
        """
        Called when the screen is shown.
        """
        self.pos_screen.on_screen_shown()
