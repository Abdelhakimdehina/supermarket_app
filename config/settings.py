# Application settings

import os
from pathlib import Path

# Application info
APP_NAME = "Supermarket Management System"
APP_VERSION = "1.0.0"

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_MIN_WIDTH = 1024
SCREEN_MIN_HEIGHT = 768

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
ASSETS_DIR = BASE_DIR / 'assets'
LOGO_PATH = ASSETS_DIR / 'logo.png'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / 'supermarket.db'

# Default admin credentials
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Currency settings
CURRENCY_SYMBOL = "$"
DECIMAL_PLACES = 2

# Date format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Image settings
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# Product settings
DEFAULT_REORDER_LEVEL = 10
LOW_STOCK_THRESHOLD = 5

# Security settings
PASSWORD_MIN_LENGTH = 8
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Logging settings
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
LOG_LEVEL = 'INFO'

# Theme settings
THEME = "dark"  # or "light"
PRIMARY_COLOR = "#2980b9"
SECONDARY_COLOR = "#3498db"
SUCCESS_COLOR = "#27ae60"
ERROR_COLOR = "#e74c3c"
WARNING_COLOR = "#f1c40f"
INFO_COLOR = "#3498db"