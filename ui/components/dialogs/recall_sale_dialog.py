import customtkinter as ctk
import tkinter
from typing import List, Dict, Any, Callable

class RecallSaleDialog(ctk.CTkToplevel):
    def __init__(self, master, held_sales: List[Dict[str, Any]], on_recall: Callable, on_delete: Callable):
        super().__init__(master)
        self.title("Recall Held Sale")
        self.geometry("600x400")
        self.grab_set()

        self.held_sales = held_sales
        self.on_recall = on_recall
        self.on_delete = on_delete
        self.selected_index = None

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Frame for the list of held sales
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        list_frame.grid_columnconfigure(0, weight=1)

        # Held sales listbox
        self.sales_listbox = ctk.CTkTextbox(list_frame, state="disabled", height=200)
        self.sales_listbox.pack(expand=True, fill="both")

        self.populate_sales_list()

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, pady=10)

        recall_button = ctk.CTkButton(buttons_frame, text="Recall Selected Sale", command=self.recall_selected)
        recall_button.pack(side="left", padx=10)

        delete_button = ctk.CTkButton(buttons_frame, text="Delete Selected Sale", command=self.delete_selected, fg_color="#e74c3c", hover_color="#c0392b")
        delete_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=10)

    def populate_sales_list(self):
        self.sales_listbox.configure(state="normal")
        self.sales_listbox.delete("1.0", "end")
        for i, sale in enumerate(self.held_sales):
            customer_name = sale['customer']['full_name'] if sale.get('customer') else 'N/A'
            item_count = len(sale['items'])
            total_amount = sum(item['quantity'] * item['product']['price'] for item in sale['items'])
            hold_time = sale['hold_time'].strftime("%Y-%m-%d %H:%M:%S")
            self.sales_listbox.insert("end", f"{i+1}. Time: {hold_time}, Customer: {customer_name}, Items: {item_count}, Total: {total_amount:.2f}\n")
        self.sales_listbox.configure(state="disabled")

    def recall_selected(self):
        # Check if any text is selected
        if not self.sales_listbox.tag_ranges("sel"):
            return  # No selection, do nothing

        selected_text = self.sales_listbox.get("sel.first", "sel.last")
        if not selected_text.strip():
            return # Selection is empty

        self.selected_index = int(selected_text.split('.')[0]) - 1
        self.on_recall(self.selected_index)
        self.destroy()

    def delete_selected(self):
        # Check if any text is selected
        if not self.sales_listbox.tag_ranges("sel"):
            return  # No selection, do nothing

        selected_text = self.sales_listbox.get("sel.first", "sel.last")
        if not selected_text.strip():
            return # Selection is empty

        self.selected_index = int(selected_text.split('.')[0]) - 1
        self.on_delete(self.selected_index)
        self.populate_sales_list()
