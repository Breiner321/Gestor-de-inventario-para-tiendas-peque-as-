import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from database import InventoryDatabase
from product import Product
import re

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestos de inventarios")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")
        self.minsize(800, 400)
        self.db = InventoryDatabase()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        columns = (
            "last_update", "code", "name", "description", "unit_price",
            "quantity", "warehouse", "edit", "delete"
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, minwidth=80, width=130, anchor="center")
        self.tree.column("edit", width=70, minwidth=50, anchor="center")
        self.tree.column("delete", width=70, minwidth=50, anchor="center")
        self.tree.bind("<Double-1>", self.on_double_click)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        btn_add = tk.Button(self, text="Add Product", command=self.add_product_window)
        btn_add.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            products = self.db.load()
            for p in products:
                self.tree.insert("", "end", values=(
                    p.last_update,
                    p.code,
                    p.name,
                    p.description,
                    f"${p.unit_price:.2f}",
                    p.quantity,
                    p.warehouse,
                    "Edit",
                    "Delete"
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
                id_value = entries[0].get()
                if not re.match(r"^[A-Za-z0-9]+$", id_value) or len(id_value) < 1:
                    raise ValueError("El ID debe ser una cadena alfanumérica válida, sin símbolos ni espacios.")
                ids_db = [p.code for p in self.db.load()]
                if id_value in ids_db:
                    raise ValueError(f"El ID '{id_value}' ya existe. Debe ser único.")
                product = Product(
                    id_value,
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
                messagebox.showerror("Error al guardar", str(e))
        tk.Button(win, text="Save", command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id:
            return
        item = self.tree.item(item_id)
        values = item['values']
        col_index = int(column.replace('#','')) - 1
        if col_index == 7:  # Edit
            self.edit_product_window(values)
        elif col_index == 8:  # Delete
            self.delete_product(values)

    def edit_product_window(self, product_values):
        win = tk.Toplevel(self)
        win.title("Edit Product")
        labels = ["ID", "Name", "Description", "Quantity", "Unit Price", "Warehouse"]
        entries = []
        original_code = product_values[1]  # Guarda código original
        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(win)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries.append(entry)
        entries[0].insert(0, original_code)
        entries[0].config(state="readonly")
        entries[1].insert(0, product_values[2])
        entries[2].insert(0, product_values[3])
        entries[3].insert(0, product_values[5])
        unit_price = product_values[4]
        if isinstance(unit_price, str) and unit_price.startswith("$"):
            unit_price = unit_price[1:]
        entries[4].insert(0, unit_price)
        entries[5].insert(0, product_values[6])
        def save():
            try:
                updated_product = Product(
                    original_code,
                    entries[1].get(),
                    entries[2].get(),
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
        answer = messagebox.askyesno(
            "Confirm Delete",
            f"¿Seguro que deseas eliminar el producto '{product_values[2]}' (ID: {product_values[1]})?"
        )
        if answer:
            try:
                self.db.delete_product(product_values[1])
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()