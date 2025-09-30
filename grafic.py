import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from database import InventoryDatabase
from product import Product
#Hola 

class InventoryApp(tk.Tk):
    def _init_(self):
        super()._init_()
        self.title("Inventory Manager")
        self.geometry("900x500")
        self.db = InventoryDatabase()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        columns = ("code", "name", "unit_price", "last_update", "quantity", "warehouse", "edit", "delete")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("code", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("unit_price", text="Unit Price")
        self.tree.heading("last_update", text="Last Update")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("warehouse", text="Warehouse")
        self.tree.heading("edit", text="Edit")
        self.tree.heading("delete", text="Delete")
        self.tree.column("edit", width=50, anchor="center")
        self.tree.column("delete", width=50, anchor="center")

        self.tree.bind("<Double-1>", self.on_double_click)
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
                    p.last_update, p.quantity, p.warehouse, "Edit", "Delete"
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

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id:
            return
        item = self.tree.item(item_id)
        if column == '#7':  # Edit column
            self.edit_product_window(item['values'])
        elif column == '#8':  # Delete column
            self.delete_product(item['values'])

    def edit_product_window(self, product_values):
        win = tk.Toplevel(self)
        win.title("Edit Product")
        labels = ["ID", "Name", "Description", "Quantity", "Unit Price", "Warehouse"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(win)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries.append(entry)

        for i, value in enumerate(product_values[:-2]):  # Excluding Edit and Delete columns
            if labels[i] == "Unit Price" and isinstance(value, str) and value.startswith("$"):
                value = value[1:]
            entries[i].insert(0, value)
            if i == 0:
                entries[i].config(state="readonly")

        def save():
            try:
                updated_product = Product(
                    entries[0].get(),
                    entries[1].get(),
                    "",  # Description placeholder
                    int(entries[3].get()),
                    float(entries[4].get()),
                    entries[5].get(),
                    datetime.datetime.now().strftime("%d/%m/%Y"),
                )
                self.db.update_product(updated_product)
                self.refresh_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save Changes", command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_product(self, product_values):
        answer = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete product {product_values[1]}?")
        if answer:
            try:
                self.db.delete_product(product_values[0])
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))


if _name_ == "_main_":
    app = InventoryApp()
    app.mainloop()