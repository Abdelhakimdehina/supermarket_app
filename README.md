# Supermarket App Documentation

## Overview
This application is a desktop supermarket management system built with Python and CustomTkinter. It allows admins to manage products, inventory, sales, and more, with a user-friendly interface and persistent SQLite database.

## Key Features
- Product and inventory management (add, edit, delete, low stock alerts)
- POS (Point of Sale) screen for sales
- User authentication and roles
- Reports and statistics
- Configurable settings and themes

## Directory Structure
- `main.py` — Application entry point
- `app.py` — Main application class
- `config/` — App settings, constants, and themes
- `data/` — Persistent data (SQLite database, session)
- `database/` — DB connection, schema, and models
- `services/` — Business logic (inventory, sales, reports, etc.)
- `ui/` — All UI code
  - `base/` — Base UI components
  - `components/` — Dialogs and reusable widgets
  - `screens/` — Main screens (inventory, POS, reports, etc.)
- `utils/` — Utility functions (security, session)

## Product Inventory Logic
- Each product has a `stock_quantity` and a `reorder_level` (low stock threshold).
- The UI highlights products as low stock if `stock_quantity` is less than or equal to `reorder_level`.
- When editing/adding a product, set a reasonable "Low Stock Alert" value (e.g., 10).

## Editing a Product
1. Select a product in the inventory screen and click Edit.
2. The product dialog opens. Change fields as needed.
3. Click Save. The dialog validates input and updates the database.
4. The UI reloads and reflects the changes.

## Common Issues
- If a product is always marked as low stock, check the "Low Stock Alert" value. It should be less than the current stock for normal status.
- All debug prints have been removed for production.

## Customization
- Change appearance and theme in `main.py` or `config/themes.py`.
- Add new categories in `config/constants.py`.

## Requirements
- Python 3.10+
- See `requirements.txt` for dependencies

---
For further help, see code comments or contact the developer.
