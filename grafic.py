import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import datetime
from database import InventoryDatabase
from product import Product
import re

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de inventarios")
        self.config(bg="#f0f4f8")
        self.geometry("950x600")
        self.minsize(800, 400)

        self.db = InventoryDatabase()
        self.products_cache = []

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        # Estilos Treeview
        self.style.configure("Treeview",
                             background="#ffffff",
                             foreground="#333333",
                             rowheight=28,
                             fieldbackground="#f9f9f9",
                             font=("Segoe UI", 10))
        self.style.map('Treeview', background=[('selected', '#4a7aaf')], foreground=[('selected', 'white')])

        self.style.configure("Treeview.Heading",
                             background="#4a7aaf",
                             foreground="white",
                             font=("Segoe UI", 11, "bold"))

        self.style.configure("TButton",
                             font=("Segoe UI", 11),
                             padding=6,
                             borderwidth=0)
        self.style.map("TButton",
                       background=[('active', '#3a5d8f')],
                       foreground=[('active', 'white')])

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # Logo y título
        try:
            logo_img = Image.open("Logo.png")
            logo_img = logo_img.resize((70, 70), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            label_logo = tk.Label(self, image=self.logo_photo, bg="#f0f4f8")
            label_logo.grid(row=0, column=0, padx=15, pady=8, sticky='nw', rowspan=2)
        except Exception:
            pass  # Si no existe logo.png no pasa nada

        label_title = tk.Label(self, text="Gestor de inventarios", font=("Segoe UI", 24, "bold"), bg="#f0f4f8", fg="#2c3e50")
        label_title.grid(row=0, column=1, columnspan=5, pady=15, sticky='w')

        # Barra de búsqueda y botones
        self.search_var = tk.StringVar()
        entry_search = tk.Entry(self, textvariable=self.search_var, font=("Segoe UI", 13), bd=2, relief='groove', width=40)
        entry_search.grid(row=1, column=1, padx=5, pady=7, sticky='ew')
        entry_search.bind("<KeyRelease>", self.filter_table)

        btn_search = ttk.Button(self, text="Buscar", command=self.filter_table, width=12)
        btn_search.grid(row=1, column=2, padx=10, pady=7)

        btn_add = ttk.Button(self, text="Agregar Producto", command=self.add_product_window, width=16)
        btn_add.grid(row=1, column=3, padx=10, pady=7)

        btn_export = ttk.Button(self, text="Exportar CSV", command=self.export_csv, width=12)
        btn_export.grid(row=1, column=4, padx=10, pady=7)

        # Tabla
        columns = ("Ultima_modificación", "ID", "Nombre", "Descripción", "Precio Unitario", "Cantidad", "Almacén", "Editar", "Eliminar")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            if col in ['Editar', 'Eliminar']:
                self.tree.column(col, width=60, anchor='center')
            else:
                self.tree.column(col, width=130, anchor='center')

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=15, pady=10)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=5, sticky="ns", pady=10)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Etiqueta total inventario
        self.label_total = tk.Label(self, text="Valor total inventario: 0.00", font=("Segoe UI", 16, "bold"), bg="#f0f4f8", fg="#34495e")
        self.label_total.grid(row=3, column=0, columnspan=6, pady=15, sticky='w', padx=15)

    def refresh_table(self):
        self.products_cache = self.db.load()
        self.filter_table()

    def filter_table(self, event=None):
        search_text = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        total = 0.0
        for p in self.products_cache:
            if (search_text in str(p.code).lower() or search_text in p.name.lower() or
                search_text in p.description.lower() or search_text in p.warehouse.lower()):
                self.tree.insert("", "end", values=(
                    p.last_update, str(p.code), p.name, p.description,
                    f"{p.unit_price:.2f}", p.quantity, p.warehouse, "✏️", "🗑️"
                ))
                total += p.unit_price * p.quantity

        self.label_total.config(text=f"Valor total inventario: {total:,.2f}")

    def add_product_window(self):
        self._product_window(title="Agregar Producto")

    def _product_window(self, title, product_values=None):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("400x300")
        win.config(bg="#ecf0f1")
        labels = ["ID", "Nombre", "Descripción", "Cantidad", "Precio Unitario", "Almacén"]
        entries = []
        warehouse_options = ["B1", "B2", "B3", "B4"]

        for i, label in enumerate(labels):
            lbl = tk.Label(win, text=label, bg="#ecf0f1", font=("Segoe UI", 11))
            lbl.grid(row=i, column=0, padx=10, pady=6, sticky='w')

            if label == "Cantidad":
                spin = tk.Spinbox(win, from_=0, to=1000000, width=15, font=("Segoe UI", 11))
                spin.grid(row=i, column=1, padx=10, pady=6, sticky='ew')
                entries.append(spin)
            elif label == "Almacén":
                combo = ttk.Combobox(win, values=warehouse_options, state="readonly", width=13, font=("Segoe UI", 11))
                combo.current(0)
                combo.grid(row=i, column=1, padx=10, pady=6, sticky='ew')
                entries.append(combo)
            else:
                entry = tk.Entry(win, font=("Segoe UI", 11), width=20)
                entry.grid(row=i, column=1, padx=10, pady=6, sticky='ew')
                entries.append(entry)

        if product_values:
            # Llenar campos para edición
            entries[0].insert(0, product_values[1])
            entries[0].config(state='readonly')
            entries[1].insert(0, product_values[2])
            entries[2].insert(0, product_values[3])
            entries[3].delete(0, 'end')
            entries[3].insert(0, product_values[5])
            unit_price = product_values[4]
            if isinstance(unit_price, str) and unit_price.startswith("$"):
                unit_price = unit_price[1:]
            entries[4].insert(0, unit_price)
            try:
                idx = warehouse_options.index(product_values[6])
            except ValueError:
                idx = 0
            entries[5].current(idx)

        def save():
            try:
                code = entries[0].get().strip()
                if not re.match(r'^[A-Za-z0-9]+$', code):
                    raise ValueError("El ID debe ser alfanumérico sin espacios ni símbolos.")
                if not product_values and code in [p.code for p in self.products_cache]:
                    raise ValueError(f"El ID {code} ya existe. Debe ser único.")
                qty = int(entries[3].get())
                if qty < 0:
                    raise ValueError("La cantidad no puede ser negativa.")
                price = float(entries[4].get())
                if price < 0:
                    raise ValueError("El precio unitario no puede ser negativo.")
                new_product = Product(
                    code,
                    entries[1].get().strip(),
                    entries[2].get().strip(),
                    qty,
                    price,
                    entries[5].get(),
                    datetime.datetime.now().strftime("%d/%m/%Y")
                )
                if product_values:
                    self.db.update_product(new_product)
                else:
                    self.db.add_product(new_product)
                self.refresh_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error al guardar", str(e))

        btn_save = ttk.Button(win, text="Guardar", command=save)
        btn_save.grid(row=len(labels), column=0, columnspan=2, pady=15)

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id:
            return
        item = self.tree.item(item_id)
        col_index = int(column.replace('#', '')) - 1
        values = item['values']
        if col_index == 7:
            self._product_window(title="Editar Producto", product_values=values)
        elif col_index == 8:
            self.delete_product(values)

    def delete_product(self, product_values):
        answer = messagebox.askyesno("Confirmar Eliminación",
                                     f"Seguro que deseas eliminar el producto {product_values[2]} (ID: {product_values[1]})?")
        if answer:
            try:
                self.db.delete_product(str(product_values[1]))
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                title="Guardar archivo CSV")
        if filepath:
            try:
                self.db.export_to_csv(filepath)
                messagebox.showinfo("Exportar CSV", "Exportación exitosa.")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando CSV:\n{e}")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
