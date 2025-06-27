import customtkinter as ctk
from tkinter import ttk, filedialog
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.constants import PADDING_SMALL, PADDING_MEDIUM
from services.inventory_service import InventoryService

class TransactionHistoryDialog(ctk.CTkToplevel):
    """Dialog for viewing inventory transaction history"""
    
    def __init__(self, parent, product: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        
        self.title("Inventory Transaction History")
        self.geometry("800x600")
        
        self.product = product
        self.inventory_service = InventoryService()
        
        # Create UI
        self.create_ui()
        self.load_transactions()
        
        self.grab_set()
        self.focus_force()
        self.wait_window()
    
    def create_ui(self):
        """Create the dialog UI with enhanced features"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_MEDIUM, pady=PADDING_SMALL)
        if self.product:
            title = f"Transaction History - {self.product['name']}"
        else:
            title = "Recent Inventory Transactions"
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        # Search/filter entry
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_transactions())
        search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Search by user, reason, or type...",
            textvariable=self.search_var,
            width=220
        )
        search_entry.pack(side="right", padx=(0, 10))

        # Export button
        export_btn = ctk.CTkButton(
            header_frame,
            text="Export CSV",
            command=self.export_to_csv,
            fg_color="#16a085",
            hover_color="#138d75",
            width=100
        )
        export_btn.pack(side="right", padx=(0, 10))

        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=PADDING_MEDIUM, pady=(0, PADDING_MEDIUM))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Treeview columns
        self.columns = [
            "Date/Time",
            "Change" if self.product else "Product",
            "Previous",
            "New",
            "Type",
            "Reason",
            "User"
        ]
        tree_columns = [f"col{i}" for i in range(len(self.columns))]
        self.tree = ttk.Treeview(table_frame, columns=tree_columns, show="headings", selectmode="browse", height=18)
        for idx, col in enumerate(self.columns):
            self.tree.heading(tree_columns[idx], text=col, command=lambda c=tree_columns[idx]: self.sort_by_column(c, False))
            self.tree.column(tree_columns[idx], anchor="center", width=120)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        # Style for highlighting
        style = ttk.Style()
        style.map("Treeview", background=[('selected', '#b3d9ff')])
        style.configure("LowStock.Treeview", background="#fff3cd")
        style.configure("OutStock.Treeview", background="#ffcccc")
        style.configure("Positive.Treeview", foreground="#2ecc71")
        style.configure("Negative.Treeview", foreground="#e74c3c")

        # Transaction count label
        self.count_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.count_label.grid(row=2, column=0, sticky="w", padx=PADDING_MEDIUM, pady=(0, PADDING_SMALL))

        # Close button
        ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            width=100
        ).grid(row=3, column=0, pady=PADDING_MEDIUM)
    
    def load_transactions(self):
        """Load and display transactions in the treeview"""
        try:
            if self.product:
                self.transactions = self.inventory_service.get_product_transactions(self.product['id'])
            else:
                self.transactions = self.inventory_service.get_recent_transactions()
        except Exception as e:
            self.transactions = []
            self.count_label.configure(text=f"Error loading transactions: {str(e)}")
            return
        self.filter_transactions()

    def filter_transactions(self):
        """Filter transactions based on search entry and update the treeview"""
        search = self.search_var.get().lower()
        filtered = []
        for t in self.transactions:
            if (
                search in str(t.get('user_name', '')).lower() or
                search in str(t.get('reason', '')).lower() or
                search in str(t.get('transaction_type', '')).lower()
            ):
                filtered.append(t)
        self.update_treeview(filtered)

    def update_treeview(self, transactions):
        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in transactions:
            try:
                date_str = datetime.fromisoformat(t['created_at']).strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                date_str = "N/A"
            change = t['quantity_change']
            change_str = f"+{change}" if change > 0 else str(change)
            change_color = "Positive.Treeview" if change > 0 else "Negative.Treeview" if change < 0 else ""
            row = [
                date_str,
                change_str if self.product else t.get('product_name', ''),
                str(t['previous_quantity']),
                str(t['new_quantity']),
                t['transaction_type'].title(),
                t.get('reason', ''),
                t.get('user_name', 'System')
            ]
            tags = ()
            if self.product:
                if change > 0:
                    tags = ("positive",)
                elif change < 0:
                    tags = ("negative",)
            self.tree.insert("", "end", values=row, tags=tags)
        self.tree.tag_configure("positive", foreground="#2ecc71")
        self.tree.tag_configure("negative", foreground="#e74c3c")
        self.count_label.configure(text=f"{len(transactions)} transaction(s) found")

    def sort_by_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            l.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).replace('-', '', 1).isdigit() else t[0], reverse=reverse)
        except Exception:
            l.sort(key=lambda t: t[0], reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    def export_to_csv(self):
        import csv
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        # Get currently displayed transactions
        displayed = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.columns)
                for row in displayed:
                    writer.writerow(row)
            self.count_label.configure(text=f"Exported {len(displayed)} transactions to CSV.")
        except Exception as e:
            self.count_label.configure(text=f"Export failed: {str(e)}") 