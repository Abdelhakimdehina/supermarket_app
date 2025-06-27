# 🛒 Supermarket App Documentation

## Overview
A modern desktop supermarket management system built with Python and CustomTkinter. It provides inventory, sales, and reporting features for small to medium businesses.

## ✨ Features
- 📦 Product and inventory management (add, edit, delete, low stock alerts)
- 🧾 POS (Point of Sale) with cart, checkout, and ticket printing
- 👤 User authentication and roles
- 📊 Sales history and reporting
- 🎨 Configurable settings and themes
- 🗄️ SQLite database for persistent storage

## 📁 Directory Structure
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

## 📦 Product Inventory Logic
- Each product has a `stock_quantity` and a `reorder_level` (low stock threshold).
- The UI highlights products as low stock if `stock_quantity` is less than or equal to `reorder_level`.
- When editing/adding a product, set a reasonable "Low Stock Alert" value (e.g., 10).

## 🧾 POS (Point of Sale)
- ➕ Add products to the cart from the product list.
- 🔄 Adjust quantities, remove items, or clear the cart.
- 💸 Enter discounts and tax if needed.
- 💳 Select payment method (cash, card, mobile).
- ✅ Checkout processes the sale, updates inventory, and prints a ticket.
- 🖨️ "Print Ticket" button prints a formatted receipt for the current cart.
- ⏸️ "Hold Sale" prints a ticket for the current cart (demo; not saved).

### 🖨️ Ticket Printing
- Tickets include sale ID, date, cashier, itemized list, totals, and a thank you message.
- Tickets are printed to the console for easy integration with real printers.

## ✏️ Editing a Product
1. Select a product in the inventory screen and click Edit.
2. The product dialog opens. Change fields as needed.
3. Click Save. The dialog validates input and updates the database.
4. The UI reloads and reflects the changes.

## ⚠️ Common Issues
- If a product is always marked as low stock, check the "Low Stock Alert" value. It should be less than the current stock for normal status.
- All debug prints have been removed for production.
- If ticket printing fails, ensure product data is structured as expected (see POS cart logic).

## 🛠️ Customization
- 🎨 Change appearance and theme in `main.py` or `config/themes.py`.
- 🏷️ Add new categories in `config/constants.py`.
- 🖨️ Extend ticket printing for real hardware by replacing the print function.

## 📝 Requirements
- Python 3.10+
- See `requirements.txt` for dependencies

---
For further help, see code comments or contact the developer. 😊
