import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from database import InventoryDatabase
from product import Product

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Manager")
        self.geometry("750x400")
        self.db = InventoryDatabase()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        columns = ("last_update", "code", "name", "description", "unit_price", "quantity", "warehouse", "edit")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("last_update", text="Last Update")
        self.tree.heading("code", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("description", text="Description")
        self.tree.heading("unit_price", text="Unit Price")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("warehouse", text="Warehouse")
        self.tree.heading("edit", text="Edit")
        self.tree.column("edit", width=50, anchor="center")

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
                    p.last_update,  
                    p.code,
                    p.name,
                    p.description,
                    f"${p.unit_price:.2f}",
                    p.quantity,
                    p.warehouse,
                    "Edit"
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
        
        if column == '#7':  
            item = self.tree.item(item_id)
            self.edit_product_window(item['values'])

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id:
            return
        print("DEBUG: clicked column:", column)  
        item = self.tree.item(item_id)
        values = item['values']
        print("DEBUG: item values on double click:", values)
      
        if column == f"#{len(values)}":  
           
            self.edit_product_window(values)

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

        entries[0].insert(0, product_values[1])  
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
                    entries[0].get(),
                    entries[1].get(),
                    entries[2].get(),  # ahora sí la descripción
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



if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()