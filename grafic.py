import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from database import InventoryDatabase
from product import Product

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Manager")
        self.geometry("800x500")
        self.db = InventoryDatabase()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        columns = ("code", "name", "unit_price", "last_update", "quantity", "warehouse")

        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("code", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("unit_price", text="Unit Price")
        self.tree.heading("last_update", text="Last Update")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("warehouse", text="Warehouse")
        self.tree.pack(fill="both", expand=True)

        btn_add = tk.Button(self, text="Add Product", command=self.add_product_window)
        btn_add.pack(pady=10)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            products = self.db.load()
            for p in products:
                self.tree.insert("", "end", values=(
                    p.code, p.name, f"${p.unit_price:.2f}", 
                    p.last_update, p.quantity, p.warehouse
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")

    def add_product_window(self):
        win = tk.Toplevel(self)
        win.title("Add Product")

        labels = ["ID", "Name", "Description", "Quantity", "Unit Price", "Warehouse"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(win)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries.append(entry)

        def save():
            try:
                product = Product(
                    entries[0].get(),
                    entries[1].get(),
                    entries[2].get(),
                    int(entries[3].get()),
                    float(entries[4].get()),
                    entries[5].get(),
                    datetime.datetime.now().strftime("%d/%m/%Y"),
                )
                self.db.add_product(product)
                self.refresh_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save", command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
