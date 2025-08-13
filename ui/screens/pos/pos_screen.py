import customtkinter as ctk
from typing import Dict, Any, Optional, List
import datetime
from decimal import Decimal
from utils.product_images import ProductImageHandler

from config.constants import (
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE,
    CATEGORIES, PAYMENT_METHODS, PAYMENT_CASH, PAYMENT_CARD, PAYMENT_MOBILE, TAX_RATE,
    SCREEN_DASHBOARD, CURRENCY_SYMBOL
)
from ui.base.base_frame import BaseFrame
from ui.base.scrollable_frame import ScrollableFrame
from services.auth_service import AuthService
from services.product_service import ProductService
from services.sale_service import SaleService
from utils.session import SessionManager
from ui.components.dialogs.customer_selector_dialog import CustomerSelectorDialog
from ui.components.dialogs.recall_sale_dialog import RecallSaleDialog

class POSScreen(BaseFrame):
    """Point of Sale screen for the application"""
    
    def __init__(self, master, **kwargs):
        # Initialize services first
        self.auth_service = AuthService()
        self.product_service = ProductService()
        self.sale_service = SaleService()
        self.session_manager = SessionManager()


        super().__init__(master, **kwargs)
        
        # Current cart items
        self.cart_items: List[Dict[str, Any]] = []
        self.held_sales: List[Dict[str, Any]] = []
        
        # Selected customer
        self.selected_customer = None
        
        # Set background color
        self.configure(fg_color=("#f0f0f0", "#2c3e50"))
        
    

    def init_ui(self):
        """Initialize UI components"""
        # Create main container with 2 columns
        self.grid_columnconfigure(0, weight=3)  # Product section
        self.grid_columnconfigure(1, weight=2)  # Cart section
        self.grid_rowconfigure(0, weight=1)
        
        # Create product section
        self.create_product_section()
        
        # Create cart section
        self.create_cart_section()
    
    def create_product_section(self):
        """Create product search and display section"""
        product_frame = ctk.CTkFrame(self)
        product_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Configure grid
        product_frame.grid_columnconfigure(0, weight=1)
        product_frame.grid_rowconfigure(0, weight=0)  # Header with return button
        product_frame.grid_rowconfigure(1, weight=0)  # Search bar
        product_frame.grid_rowconfigure(2, weight=0)  # Category filter
        product_frame.grid_rowconfigure(3, weight=1)  # Product list
        
        # Header with return button
        header_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        header_frame.grid_columnconfigure(1, weight=1)  # Make title expand

        # Conditionally add the return to dashboard button for admins
        current_user = self.session_manager.get_user()
        if current_user and current_user.get('role') == 'admin':
            return_button = ctk.CTkButton(
                header_frame,
                text="← Return to Dashboard",
                command=lambda: self.navigate_to(SCREEN_DASHBOARD),
                width=150,
                fg_color="#2980b9",
                hover_color="#3498db"
            )
            return_button.grid(row=0, column=0, padx=PADDING_SMALL)
        

        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Point of Sale",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=1, padx=PADDING_MEDIUM)
        
        # Search bar
        search_frame = ctk.CTkFrame(product_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.search_products())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search products by name or barcode...",
            textvariable=self.search_var,
            width=300
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=PADDING_SMALL)
        search_entry.bind("<Return>", lambda event: self.search_products())
        
        search_button = ctk.CTkButton(search_frame, text="Search", command=self.search_products)
        search_button.grid(row=0, column=1, sticky="e", padx=PADDING_SMALL)
        
        barcode_button = ctk.CTkButton(search_frame, text="Scan Barcode", command=self.scan_barcode)
        barcode_button.grid(row=0, column=2, sticky="e", padx=PADDING_SMALL)
        
        # Category filter
        category_outer_frame = ctk.CTkFrame(product_frame)
        category_outer_frame.grid(row=2, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        category_outer_frame.grid_columnconfigure(0, weight=1)

        # Create a canvas for horizontal scrolling
        canvas = ctk.CTkCanvas(category_outer_frame, height=40, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="ew")

        # Create a frame inside the canvas to hold the category buttons
        category_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        category_frame.grid(row=0, column=0)

        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(category_outer_frame, orientation="horizontal", command=canvas.xview)
        scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure canvas
        canvas.configure(xscrollcommand=scrollbar.set)

        # Add "All" category
        all_button = ctk.CTkButton(
            category_frame, 
            text="All",
            command=lambda: self.filter_by_category(None),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )
        all_button.grid(row=0, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL)

        # Add category buttons
        for i, category in enumerate(CATEGORIES):
            category_button = ctk.CTkButton(
                category_frame, 
                text=category,
                command=lambda cat=category: self.filter_by_category(cat),
                fg_color="transparent",
                border_width=1,
                text_color=("gray10", "gray90")
            )
            category_button.grid(row=0, column=i+1, padx=PADDING_SMALL, pady=PADDING_SMALL)

        # Update canvas scroll region when category frame changes size
        category_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create window in canvas
        canvas.create_window((0, 0), window=category_frame, anchor="nw")

        # Bind mouse wheel to horizontal scroll
        def _on_mousewheel(event):
            canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Product list
        self.product_list_frame = ScrollableFrame(product_frame)
        self.product_list_frame.configure(width=800, height=600)  # Set reasonable minimum size
        self.product_list_frame.grid(row=3, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        self.product_list_frame.grid_columnconfigure(0, weight=1)
        self.product_list_frame.grid_columnconfigure(1, weight=1)
        self.product_list_frame.grid_columnconfigure(2, weight=1)
        
        # Load initial products
        self.load_products()
    
    def create_cart_section(self):
        """Create shopping cart section"""
        cart_frame = ctk.CTkFrame(self)
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        
        # Configure grid
        cart_frame.grid_columnconfigure(0, weight=1)
        cart_frame.grid_rowconfigure(0, weight=0)  # Cart header
        cart_frame.grid_rowconfigure(1, weight=1)  # Cart items
        cart_frame.grid_rowconfigure(2, weight=0)  # Cart summary
        cart_frame.grid_rowconfigure(3, weight=0)  # Payment options
        cart_frame.grid_rowconfigure(4, weight=0)  # Action buttons
        
        # Cart header
        cart_header = ctk.CTkFrame(cart_frame)
        cart_header.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
        cart_header.grid_columnconfigure(0, weight=1)
        cart_header.grid_columnconfigure(1, weight=0)
        
        cart_title = ctk.CTkLabel(
            cart_header, 
            text="Shopping Cart", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        cart_title.grid(row=0, column=0, sticky="w")
        
        clear_button = ctk.CTkButton(
            cart_header, 
            text="Clear Cart",
            command=self.clear_cart,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100
        )
        clear_button.grid(row=0, column=1, sticky="e")
        
        # Cart items
        self.cart_items_frame = ScrollableFrame(cart_frame)
        self.cart_items_frame.configure(width=400, height=400)  # Set reasonable minimum size
        self.cart_items_frame.grid(row=1, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        
        # Cart summary
        summary_frame = ctk.CTkFrame(cart_frame)
        summary_frame.grid(row=2, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        summary_frame.grid_columnconfigure(0, weight=1)  # Labels
        summary_frame.grid_columnconfigure(1, weight=1)  # Values/Inputs
        summary_frame.grid_columnconfigure(2, weight=0)  # Extra buttons
        
        # Customer info
        customer_label = ctk.CTkLabel(summary_frame, text="Customer:", anchor="w")
        customer_label.grid(row=0, column=0, sticky="w", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        self.customer_info = ctk.CTkLabel(summary_frame, text="No customer selected", anchor="e")
        self.customer_info.grid(row=0, column=1, sticky="e", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        select_customer_button = ctk.CTkButton(
            summary_frame, 
            text="Select",
            command=self.select_customer,
            fg_color="transparent",
            border_width=1,
            width=80
        )
        select_customer_button.grid(row=0, column=2, padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        # Subtotal
        subtotal_label = ctk.CTkLabel(summary_frame, text="Subtotal:", anchor="w")
        subtotal_label.grid(row=1, column=0, sticky="w", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        self.subtotal_value = ctk.CTkLabel(summary_frame, text="$0.00", anchor="e")
        self.subtotal_value.grid(row=1, column=1, sticky="e", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        # Discount
        discount_label = ctk.CTkLabel(summary_frame, text="Discount:", anchor="w")
        discount_label.grid(row=2, column=0, sticky="w", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        self.discount_entry = ctk.CTkEntry(summary_frame, width=100, placeholder_text="0.00")
        self.discount_entry.grid(row=2, column=1, sticky="e", padx=PADDING_SMALL, pady=PADDING_SMALL)
        self.discount_entry.bind("<KeyRelease>", lambda event: self.update_cart_summary())
        
        # Tax
        tax_label = ctk.CTkLabel(summary_frame, text="Tax:", anchor="w")
        tax_label.grid(row=3, column=0, sticky="w", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        self.tax_entry = ctk.CTkEntry(summary_frame, width=100, placeholder_text="0.00")
        self.tax_entry.grid(row=3, column=1, sticky="e", padx=PADDING_SMALL, pady=PADDING_SMALL)
        self.tax_entry.bind("<KeyRelease>", lambda event: self.update_cart_summary())
        
        # Total
        total_label = ctk.CTkLabel(
            summary_frame, 
            text="Total:", 
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        total_label.grid(row=4, column=0, sticky="w", padx=PADDING_SMALL, pady=PADDING_SMALL)
        
        self.total_value = ctk.CTkLabel(
            summary_frame, 
            text="$0.00", 
            font=ctk.CTkFont(weight="bold"),
            anchor="e"
        )
        self.total_value.grid(row=4, column=1, sticky="e", padx=PADDING_SMALL, pady=PADDING_MEDIUM)
        
        # Payment options
        payment_frame = ctk.CTkFrame(cart_frame)
        payment_frame.grid(row=3, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        payment_frame.grid_columnconfigure(1, weight=1)

        payment_label = ctk.CTkLabel(
            payment_frame,
            text="Payment Method:",
            font=ctk.CTkFont(weight="bold")
        )
        payment_label.grid(row=0, column=0, sticky="w", padx=PADDING_SMALL, pady=PADDING_SMALL)

        # Payment method radio buttons
        self.payment_method_var = ctk.StringVar(value=PAYMENT_CASH)
        payment_options_frame = ctk.CTkFrame(payment_frame, fg_color="transparent")
        payment_options_frame.grid(row=0, column=1, sticky="ew", padx=(PADDING_LARGE, 0))
        payment_options_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for i, method in enumerate(PAYMENT_METHODS):
            rb = ctk.CTkRadioButton(
                payment_options_frame,
                text=method,
                variable=self.payment_method_var,
                value=method,
                font=ctk.CTkFont(size=12)
            )
            rb.grid(row=0, column=i, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(cart_frame)
        action_frame.grid(row=4, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        hold_button = ctk.CTkButton(
            action_frame,
            text="Hold Sale",
            command=self.hold_sale,
            fg_color="#e67e22",
            hover_color="#d35400"
        )
        hold_button.grid(row=0, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")

        recall_button = ctk.CTkButton(
            action_frame,
            text="Recall Sale",
            command=self.recall_sale,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        recall_button.grid(row=0, column=1, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")

        checkout_button = ctk.CTkButton(
            action_frame,
            text="Checkout",
            command=self.checkout,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        checkout_button.grid(row=0, column=2, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        # Add Print Ticket button
        print_ticket_button = ctk.CTkButton(
            action_frame,
            text="Print Ticket",
            command=self.on_print_ticket,
            fg_color="#f39c12",
            hover_color="#e67e22",
            width=120
        )
        print_ticket_button.grid(row=1, column=0, columnspan=2, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")

    def on_print_ticket(self):
        """Handler for Print Ticket button. Prints a sample or last sale ticket."""
        # Example: print the current cart as a ticket (customize as needed)
        if not self.cart_items:
            print("Cart is empty. Nothing to print.")
            return
        # Build a sale dict using the correct keys from cart_items
        from datetime import datetime
        sale = {
            'sale_id': 'N/A',
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'cashier': 'Current User',
            'items': [
                {
                    'name': item['product']['name'],
                    'quantity': item['quantity'],
                    'price': item['product']['price']
                } for item in self.cart_items
            ],
            'total': sum(item['quantity'] * item['product']['price'] for item in self.cart_items),
            'payment': sum(item['quantity'] * item['product']['price'] for item in self.cart_items),
            'change': 0.0
        }
        self.print_ticket(sale)
    
    def load_products(self, category: Optional[str] = None):
        """Load products into the product list"""
        try:
            # Clear existing products
            self.product_list_frame.clear()
            
            # Get products
            products = self.product_service.get_products(category=category)
            
            if not products:
                # Show message if no products found
                no_results = ctk.CTkLabel(
                    self.product_list_frame, 
                    text="No products available", 
                    font=ctk.CTkFont(size=14)
                )
                no_results.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
                return
            
            # Display products in a grid
            row, col = 0, 0
            max_cols = 3
            
            # Configure grid weights for product list frame
            self.product_list_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            for product in products:
                product_card = self.create_product_card(self.product_list_frame, product)
                product_card.grid(row=row, column=col, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="nsew")
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        except Exception as e:
            print(f"Error loading products: {e}")
            error_label = ctk.CTkLabel(
                self.product_list_frame, 
                text="Error loading products. Please try again.", 
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
    
    def create_product_card(self, parent, product: Dict[str, Any]) -> ctk.CTkFrame:
        """Create a product card widget"""
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(0, weight=1)
        card.configure(width=200, height=250)

        # Product image using image handler utility
        image_handler = ProductImageHandler()
        product_image = image_handler.get_product_image(
            product.get('image_path', ''), 
            size=(120, 80)
        )
        
        if product_image:
            # Create label with actual product image
            image_label = ctk.CTkLabel(card, image=product_image, text="")
        else:
            # Create placeholder label
            image_label = image_handler.create_placeholder_label(card, size=(120, 80))
        
        image_label.grid(row=0, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")

        # Product name
        name_label = ctk.CTkLabel(
            card, 
            text=product['name'], 
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=180
        )
        name_label.grid(row=1, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")

        # Product price
        price_label = ctk.CTkLabel(
            card,
            text=f"{CURRENCY_SYMBOL}{product['price']:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#00adb5", "#00adb5"),
            anchor="e"
        )
        price_label.grid(row=2, column=0, padx=PADDING_SMALL, pady=(0, PADDING_SMALL), sticky="ew")

        # Product category
        category_label = ctk.CTkLabel(
            card, 
            text=product['category'], 
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        category_label.grid(row=3, column=0, padx=PADDING_SMALL, pady=(0, PADDING_SMALL), sticky="ew")
        
        # Stock status
        stock_label = ctk.CTkLabel(
            card, 
            text=f"In Stock: {product['stock']}", 
            font=ctk.CTkFont(size=10),
            text_color="green" if product['stock'] > 0 else "red"
        )
        stock_label.grid(row=4, column=0, padx=PADDING_SMALL, pady=(0, PADDING_SMALL), sticky="ew")
        
        # Add to cart button
        add_button = ctk.CTkButton(
            card, 
            text="Add to Cart",
            command=lambda p=product: self.add_to_cart(p),
            state="normal" if product['stock'] > 0 else "disabled",
            width=160  # Fixed button width
        )
        add_button.grid(row=5, column=0, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="ew")
        
        return card
    
    def search_products(self):
        """Search for products"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self.load_products()
            return
        
        # Clear existing products
        self.product_list_frame.clear()
        
        # Search products
        products = self.product_service.get_products(search_term=search_term)
        
        # Display products in a grid
        row, col = 0, 0
        max_cols = 3
        
        for product in products:
            product_card = self.create_product_card(self.product_list_frame, product)
            product_card.grid(row=row, column=col, padx=PADDING_SMALL, pady=PADDING_SMALL, sticky="nsew")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Show message if no products found
        if not products:
            no_results = ctk.CTkLabel(
                self.product_list_frame, 
                text="No products found", 
                font=ctk.CTkFont(size=14)
            )
            no_results.grid(row=0, column=0, padx=PADDING_MEDIUM, pady=PADDING_MEDIUM)
    
    def scan_barcode(self):
        """Simulate barcode scanning"""
        # In a real application, this would interface with a barcode scanner
        # For now, we'll just show a dialog to enter a barcode manually
        
        dialog = ctk.CTkInputDialog(
            text="Enter barcode:", 
            title="Scan Barcode"
        )
        barcode = dialog.get_input()
        
        if not barcode:
            return
        
        # Search for product by barcode
        products = self.product_service.get_products(search_term=barcode)
        
        if products:
            # Assume the first product with matching barcode
            self.add_to_cart(products[0])
        else:
            # Show error message
            self.show_message("Barcode Not Found", f"No product found with barcode: {barcode}")
    
    def filter_by_category(self, category: Optional[str]):
        """Filter products by category"""
        self.load_products(category)
    
    def add_to_cart(self, product: Dict[str, Any]):
        """Add a product to the cart"""
        # Check if product is already in cart
        for item in self.cart_items:
            if item['product']['id'] == product['id']:
                # Increment quantity
                item['quantity'] += 1
                item['subtotal'] = item['quantity'] * item['product']['price']
                
                # Update cart display
                self.update_cart_display()
                return
        
        # Add new item to cart
        cart_item = {
            'product': product,
            'quantity': 1,
            'price': product['price'],
            'subtotal': product['price']
        }
        
        self.cart_items.append(cart_item)
        
        # Update cart display
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update the cart display"""
        # Clear existing items
        self.cart_items_frame.clear()
        
        # Add header
        header_frame = ctk.CTkFrame(self.cart_items_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_SMALL, pady=PADDING_SMALL)
        header_frame.grid_columnconfigure(0, weight=3)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)
        
        product_header = ctk.CTkLabel(header_frame, text="Product", font=ctk.CTkFont(weight="bold"))
        product_header.grid(row=0, column=0, sticky="w")
        
        qty_header = ctk.CTkLabel(header_frame, text="Qty", font=ctk.CTkFont(weight="bold"))
        qty_header.grid(row=0, column=1, sticky="e")
        
        price_header = ctk.CTkLabel(header_frame, text="Price", font=ctk.CTkFont(weight="bold"))
        price_header.grid(row=0, column=2, sticky="e")
        
        subtotal_header = ctk.CTkLabel(header_frame, text="Subtotal", font=ctk.CTkFont(weight="bold"))
        subtotal_header.grid(row=0, column=3, sticky="e")
        
        # Add separator
        separator = ctk.CTkFrame(self.cart_items_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, sticky="ew", padx=PADDING_SMALL, pady=(0, PADDING_SMALL))
        
        # Add items
        for i, item in enumerate(self.cart_items):
            item_frame = ctk.CTkFrame(self.cart_items_frame, fg_color="transparent")
            item_frame.grid(row=i+2, column=0, sticky="ew", padx=PADDING_SMALL, pady=PADDING_SMALL)
            item_frame.grid_columnconfigure(0, weight=3)
            item_frame.grid_columnconfigure(1, weight=1)
            item_frame.grid_columnconfigure(2, weight=1)
            item_frame.grid_columnconfigure(3, weight=1)
            
            # Product name
            name_label = ctk.CTkLabel(item_frame, text=item['product']['name'], wraplength=150)
            name_label.grid(row=0, column=0, sticky="w")
            
            # Quantity with +/- buttons
            qty_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            qty_frame.grid(row=0, column=1, sticky="e")
            
            minus_button = ctk.CTkButton(
                qty_frame, 
                text="-",
                width=25,
                height=25,
                command=lambda idx=i: self.decrease_quantity(idx)
            )
            minus_button.grid(row=0, column=0)
            
            qty_label = ctk.CTkLabel(qty_frame, text=str(item['quantity']), width=30)
            qty_label.grid(row=0, column=1, padx=PADDING_SMALL)
            
            plus_button = ctk.CTkButton(
                qty_frame, 
                text="+",
                width=25,
                height=25,
                command=lambda idx=i: self.increase_quantity(idx)
            )
            plus_button.grid(row=0, column=2)
            
            # Price
            price_label = ctk.CTkLabel(item_frame, text=f"{CURRENCY_SYMBOL}{item['price']:.2f}")
            price_label.grid(row=0, column=2, sticky="e")
            
            # Subtotal
            subtotal_label = ctk.CTkLabel(item_frame, text=f"{CURRENCY_SYMBOL}{item['subtotal']:.2f}")
            subtotal_label.grid(row=0, column=3, sticky="e")
            
            # Remove button
            remove_button = ctk.CTkButton(
                item_frame, 
                text="X",
                width=25,
                height=25,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=lambda idx=i: self.remove_from_cart(idx)
            )
            remove_button.grid(row=0, column=4, padx=(PADDING_SMALL, 0))
        
        # Update summary
        self.update_cart_summary()
    
    def update_cart_summary(self):
        """Update the cart summary"""
        # Calculate subtotal
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        self.subtotal_value.configure(text=f"{CURRENCY_SYMBOL}{subtotal:.2f}")
        
        # Get discount
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0
        
        # Get tax
        try:
            tax = float(self.tax_entry.get() or 0)
        except ValueError:
            tax = subtotal * TAX_RATE
            self.tax_entry.delete(0, 'end')
            self.tax_entry.insert(0, f"{tax:.2f}")
        
        # Calculate total
        total = subtotal - discount + tax
        self.total_value.configure(text=f"{CURRENCY_SYMBOL}{total:.2f}")
    
    def increase_quantity(self, index: int):
        """Increase item quantity"""
        if 0 <= index < len(self.cart_items):
            item = self.cart_items[index]
            
            # Check stock
            if item['quantity'] >= item['product']['stock']:
                self.show_message("Stock Limit", f"Cannot add more. Only {item['product']['stock']} in stock.")
                return
            
            item['quantity'] += 1
            item['subtotal'] = item['quantity'] * item['price']
            
            # Update cart display
            self.update_cart_display()
    
    def decrease_quantity(self, index: int):
        """Decrease item quantity"""
        if 0 <= index < len(self.cart_items):
            item = self.cart_items[index]
            
            if item['quantity'] > 1:
                item['quantity'] -= 1
                item['subtotal'] = item['quantity'] * item['price']
                
                # Update cart display
                self.update_cart_display()
            else:
                # Remove item if quantity would be 0
                self.remove_from_cart(index)
    
    def remove_from_cart(self, index: int):
        """Remove an item from the cart"""
        if 0 <= index < len(self.cart_items):
            self.cart_items.pop(index)
            
            # Update cart display
            self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from the cart"""
        self.cart_items = []
        self.selected_customer = None
        self.customer_info.configure(text="No customer selected")
        self.discount_entry.delete(0, 'end')
        self.tax_entry.delete(0, 'end')
        
        # Update cart display
        self.update_cart_display()
    
    def select_customer(self):
        """Select a customer for the sale"""
        def on_customer_selected(customer_data):
            if customer_data:
                self.selected_customer = customer_data
                self.customer_info.configure(text=f"{customer_data['name']}")
        
        CustomerSelectorDialog(self, on_customer_selected)
    
    def recall_sale(self):
        """Recall a held sale"""
        if not self.held_sales:
            self.show_message("No Held Sales", "There are no sales currently on hold.")
            return

        dialog = RecallSaleDialog(self, self.held_sales, on_recall=self.on_sale_recalled, on_delete=self.on_sale_deleted)
        dialog.mainloop()

    def on_sale_recalled(self, index: int):
        """Callback function when a sale is recalled from the dialog."""
        if 0 <= index < len(self.held_sales):
            if self.cart_items:
                self.show_message("Cart Not Empty", "Please clear or complete the current sale before recalling another.")
                return

            recalled_sale = self.held_sales.pop(index)
            self.cart_items = recalled_sale["items"]
            self.selected_customer = recalled_sale["customer"]

            self.update_cart_display()
            self.update_cart_summary()
            self.show_message("Success", "Sale has been successfully recalled.")

    def on_sale_deleted(self, index: int):
        """Callback function when a sale is deleted from the dialog."""
        if 0 <= index < len(self.held_sales):
            self.held_sales.pop(index)
            self.show_message("Success", "Held sale has been deleted.")

    def hold_sale(self):
        """Hold the current sale for later"""
        if not self.cart_items:
            self.show_message("Empty Cart", "Cannot hold an empty sale.")
            return

        held_sale = {
            "items": self.cart_items,
            "customer": self.selected_customer,
            "hold_time": datetime.datetime.now()
        }
        self.held_sales.append(held_sale)
        self.clear_cart()
        self.show_message("Success", f"Sale held successfully. There are now {len(self.held_sales)} held sales.")

    def checkout(self):
        """Process checkout"""
        try:
            # Get current user
            current_user = self.auth_service.get_current_user()
            if not current_user:
                self.show_message("Error", "No user logged in")
                return
            
            # Calculate totals
            subtotal = sum(item["quantity"] * item["product"]["price"] for item in self.cart_items)
            tax = subtotal * TAX_RATE
            total = subtotal + tax
            
            # Create sale data
            sale_data = {
                "user_id": current_user["id"],
                "customer_id": self.selected_customer["id"] if self.selected_customer else None,
                "items": [
                    {
                        "product_id": item["product"]["id"],
                        "quantity": item["quantity"],
                        "price": item["product"]["price"],
                        "discount_percent": 0.0
                    }
                    for item in self.cart_items
                ],
                "payment_method": PAYMENT_CASH,
                "total": total,
                "tax": tax,
                "discount": 0.0
            }
            
            # Create sale
            sale = self.sale_service.create_sale(sale_data)
            if not sale:
                raise Exception("Failed to create sale")
            
            # Print ticket using correct keys
            ticket = {
                'sale_id': sale.get('invoice_number', sale.get('id', 'N/A')),
                'datetime': sale.get('sale_date', ''),
                'cashier': current_user.get('username', 'N/A'),
                'items': [
                    {
                        'name': item['product_name'],
                        'quantity': item['quantity'],
                        'price': item['price']
                    } for item in sale['items']
                ],
                'total': sale['total'],
                'payment': sale['total'],
                'change': 0.0
            }
            self.print_ticket(ticket)
            
            # Show success message
            self.show_success_message()
            
            # Clear cart
            self.clear_cart()
            
            # Reload products to update stock
            self.load_products()
        except Exception as e:
            self.show_message("Error", str(e))
    
    def print_ticket(self, sale):
        """
        Print a formatted sales ticket to the console.
        :param sale: dict with keys 'items' (list of dicts), 'total', 'payment', 'change', 'datetime', 'cashier', 'sale_id'
        """
        print("\n" + "="*38)
        print("         SUPERMARKET RECEIPT")
        print("="*38)
        print(f"Sale ID: {sale.get('sale_id', 'N/A')}")
        print(f"Date: {sale.get('datetime', '')}")
        print(f"Cashier: {sale.get('cashier', 'N/A')}")
        print("-"*38)
        print(f"{'Item':16} {'Qty':>3} {'Price':>7} {'Total':>8}")
        print("-"*38)
        for item in sale['items']:
            name = item['name'][:16]
            qty = item['quantity']
            price = item['price']
            total = qty * price
            print(f"{name:16} {qty:>3} {price:>7.2f} {total:>8.2f}")
        print("-"*38)
        print(f"{'TOTAL':>28}: {sale['total']:>8.2f} DA")
        print(f"{'PAYMENT':>28}: {sale['payment']:>8.2f} DA")
        print(f"{'CHANGE':>28}: {sale['change']:>8.2f} DA")
        print("="*38)
        print("  Thank you for shopping with us!  ")
        print("="*38 + "\n")
    
    def show_success_message(self):
        """Show checkout success message"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Success")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Success message
        message = ctk.CTkLabel(
            dialog,
            text="Sale completed successfully!",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        message.pack(pady=PADDING_LARGE)
        
        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        )
        close_btn.pack()
    
    def show_message(self, title: str, message: str):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("300x200")

    def on_screen_shown(self):
        """Called when POS screen is shown or needs refresh"""
        self.load_products()

    def print_cart(self):
        """Prints the current cart items to the console for debugging."""
        print("--- Current Cart ---")
        for item in self.cart_items:
            print(f"{item['name']} x{item['quantity']} @ {item['price']} each")
        print("--------------------")