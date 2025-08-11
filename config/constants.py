# Application constants

# Screen names
SCREEN_LOGIN = "login"
SCREEN_DASHBOARD = "dashboard"
SCREEN_POS = "pos"
SCREEN_INVENTORY = "inventory"
SCREEN_CUSTOMERS = "customers"
SCREEN_REPORTS = "reports"
SCREEN_CASHIER_MAIN = "cashier_main"
SCREEN_SETTINGS = "settings"
SCREEN_USER_MANAGEMENT = "user_management"

# User roles
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_CASHIER = "cashier"
ROLE_INVENTORY = "inventory"

ROLES = {
    ROLE_ADMIN: "Administrator",
    ROLE_MANAGER: "Manager",
    ROLE_CASHIER: "Cashier",
    ROLE_INVENTORY: "Inventory Clerk"
}

# UI constants
PADDING_SMALL = 5
PADDING_MEDIUM = 10
PADDING_LARGE = 20

# Product categories
CATEGORIES = [
    "Beverages",
    "Bread/Bakery",
    "Canned/Jarred Goods",
    "Dairy",
    "Dry/Baking Goods",
    "Frozen Foods",
    "Meat & Poultry",
    "Produce",
    "Cleaners",
    "Paper Goods",
    "Personal Care",
    "Other"
]

# Payment methods
PAYMENT_CASH = "cash"
PAYMENT_CARD = "card"
PAYMENT_MOBILE = "mobile"

PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "Mobile Payment"
]

# Screen settings
SCREEN_MIN_WIDTH = 1024
SCREEN_MIN_HEIGHT = 768

# Tax rate (10%)
TAX_RATE = 0.10

# Low stock threshold
LOW_STOCK_THRESHOLD = 10

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Currency symbol
CURRENCY_SYMBOL = "DA"

# Status constants
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_CANCELLED = "cancelled"

# Purchase order status
PO_STATUS_DRAFT = "draft"
PO_STATUS_PENDING = "pending"
PO_STATUS_APPROVED = "approved"
PO_STATUS_RECEIVED = "received"
PO_STATUS_CANCELLED = "cancelled"

# Sale status
SALE_STATUS_COMPLETED = "completed"
SALE_STATUS_PENDING = "pending"
SALE_STATUS_CANCELLED = "cancelled"
SALE_STATUS_REFUNDED = "refunded"

# Payment status
PAYMENT_STATUS_PAID = "paid"
PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_FAILED = "failed"
PAYMENT_STATUS_REFUNDED = "refunded"

# Error messages
ERROR_INVALID_LOGIN = "Invalid username or password"
ERROR_INSUFFICIENT_STOCK = "Insufficient stock available"
ERROR_INVALID_QUANTITY = "Invalid quantity specified"
ERROR_INVALID_PRICE = "Invalid price specified"
ERROR_INVALID_PAYMENT = "Invalid payment method"
ERROR_TRANSACTION_FAILED = "Transaction failed. Please try again."

# Color scheme
COLORS = {
    "bg_dark": "#1a1a1a",
    "bg_darker": "#2d2d2d",
    "card_bg": "#2d2d2d",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "accent_green": "#00ff88",
    "accent_blue": "#00a8ff",
    "accent_red": "#ff4757",
    "accent_purple": "#8b5cf6",
    "accent_yellow": "#ffd700",
    "accent_orange": "#ff6348"
}