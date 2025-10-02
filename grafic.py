import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import datetime
from database import InventoryDatabase
from product import Product
import re

class InventoryApp(tk.Tk):
    def __init__(self):
        
        #Inicializa la ventana principal y los widgets de la aplicación.
        
        super().__init__()
        self.title("Gestor de inventarios")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")
        self.minsize(800, 400)
        self.db = InventoryDatabase()
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        
        #Crea los widgets de la interfaz: logo, barra de búsqueda, tabla, botones y suma total.
        
        self.logo_img = Image.open("Logo.png")
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS
        self.logo_img = self.logo_img.resize((70, 70), resample)
        self.logo_photo = ImageTk.PhotoImage(self.logo_img)
        label_logo = tk.Label(self, image=self.logo_photo)
        label_logo.grid(row=0, column=0, padx=15, pady=6, sticky="nw", rowspan=2)
        label_title = tk.Label(self, text="Gestor de inventarios", font=("Arial", 22, "bold"))
        label_title.grid(row=0, column=1, pady=10, sticky="w", columnspan=5)

        self.search_var = tk.StringVar()
        entry_search = tk.Entry(self, textvariable=self.search_var, font=("Arial", 12))
        entry_search.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        entry_search.bind("<KeyRelease>", self.filter_table)

        btn_search = tk.Button(self, text="Buscar", command=self.filter_table, font=("Arial", 11))
        btn_search.grid(row=1, column=2, padx=5, pady=5)
        btn_add = tk.Button(self, text="Agregar Producto", command=self.add_product_window, font=("Arial", 11, "bold"))
        btn_add.grid(row=1, column=3, padx=10, pady=5)
        btn_export = tk.Button(self, text="Exportar CSV", command=self.export_csv, font=("Arial", 11))
        btn_export.grid(row=1, column=4, padx=5, pady=5)

        columns = (
            "last_update", "code", "name", "description", "unit_price",
            "quantity", "warehouse", "edit", "delete"
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, minwidth=80, width=130, anchor="center")
        self.tree.column("edit", width=50, minwidth=30, anchor="center")
        self.tree.column("delete", width=50, minwidth=30, anchor="center")
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.grid(row=2, column=0, columnspan=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=5, sticky="ns")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.label_total = tk.Label(self, text="Valor total inventario: $0.00", font=("Arial", 14, "bold"))
        self.label_total.grid(row=3, column=0, columnspan=6, pady=10, sticky="e")

        self.products_cache = []

    def refresh_table(self):
        
        #Carga y refresca la tabla con todos los productos.
        
        self.products_cache = self.db.load()
        self.filter_table()
        total = sum(p.unit_price * p.quantity for p in self.products_cache)
        self.label_total.config(text=f"Valor total inventario: ${total:,.2f}")

    def filter_table(self, event=None):
        
        #Filtra los productos de la tabla por texto (ID, nombre, descripción, etc.)
        
        search_text = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for p in self.products_cache:
            if (search_text in str(p.code).lower() or
                search_text in str(p.name).lower() or
                search_text in str(p.description).lower() or
                search_text in str(p.warehouse).lower()):
                self.tree.insert(
                    "", "end", values=(
                        p.last_update,
                        str(p.code),  # usar siempre como string
                        p.name,
                        p.description,
                        f"${p.unit_price:.2f}",
                        p.quantity,
                        p.warehouse,
                        "🖉",
                        "✖"
                    )
                )

    def add_product_window(self):
        
        #Ventana para agregar un producto nuevo. Valida que el precio no sea negativo y el id sea string.
        
        win = tk.Toplevel(self)
        win.title("Agregar Producto")
        labels = ["ID", "Nombre", "Descripción", "Cantidad", "Precio Unitario", "Almacén"]
        entries = []
        warehouse_options = ['B1', 'B2', 'B3', 'B4']
        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=2)
            if label == "Cantidad":
                spinbox = tk.Spinbox(win, from_=0, to=1000)
                spinbox.grid(row=i, column=1, padx=5, pady=2)
                entries.append(spinbox)
            elif label == "Almacén":
                combo = ttk.Combobox(win, values=warehouse_options, state="readonly")
                combo.current(0)
                combo.grid(row=i, column=1, padx=5, pady=2)
                entries.append(combo)
            else:
                entry = tk.Entry(win)
                entry.grid(row=i, column=1, padx=5, pady=2)
                entries.append(entry)
        def save():
            try:
                id_value = entries[0].get()
                if not re.match(r"^[A-Za-z0-9]+$", id_value) or len(id_value) < 1:
                    raise ValueError("El ID debe ser una cadena alfanumérica válida, sin símbolos ni espacios.")
                ids_db = [str(p.code) for p in self.db.load()]
                if id_value in ids_db:
                    raise ValueError(f"El ID '{id_value}' ya existe. Debe ser único.")
                qty = int(entries[3].get())
                if qty < 0:
                    raise ValueError("La cantidad no puede ser negativa.")
                price = float(entries[4].get())
                if price < 0:
                    raise ValueError("El precio unitario no puede ser negativo.")
                product = Product(
                    str(id_value),
                    entries[1].get(),
                    entries[2].get(),
                    qty,
                    price,
                    entries[5].get(),
                    datetime.datetime.now().strftime("%d/%m/%Y"),
                )
                self.db.add_product(product)
                self.refresh_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error al guardar", str(e))
        tk.Button(win, text="Guardar", command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def on_double_click(self, event):
        
        #Maneja doble clic para edición o eliminado, detecta la columna y pasa los valores crudos de la fila.
        
        item_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item_id:
            return
        item = self.tree.item(item_id)
        values = item['values']
        col_index = int(column.replace('#', '')) - 1
        if col_index == 7:
            self.edit_product_window(values)
        elif col_index == 8:
            self.delete_product(values)

    def edit_product_window(self, product_values):
        
        #Ventana para editar datos de un producto existente, dejando el ID fijo y como string.
        
        win = tk.Toplevel(self)
        win.title("Editar Producto")
        labels = ["ID", "Nombre", "Descripción", "Cantidad", "Precio Unitario", "Almacén"]
        entries = []
        warehouse_options = ['B1', 'B2', 'B3', 'B4']
        original_code = str(product_values[1])
        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=5, pady=2)
            if label == "Cantidad":
                spinbox = tk.Spinbox(win, from_=0, to=1000000)
                spinbox.grid(row=i, column=1, padx=5, pady=2)
                try:
                    spinbox.delete(0, "end")
                    spinbox.insert(0, int(product_values[5]))
                except Exception:
                    spinbox.insert(0, "0")
                entries.append(spinbox)
            elif label == "Almacén":
                combo = ttk.Combobox(win, values=warehouse_options, state="readonly")
                combo.grid(row=i, column=1, padx=5, pady=2)
                try:
                    combo.current(warehouse_options.index(product_values[6]))
                except ValueError:
                    combo.current(0)
                entries.append(combo)
            else:
                entry = tk.Entry(win)
                entry.grid(row=i, column=1, padx=5, pady=2)
                entries.append(entry)
        entries[0].insert(0, original_code)
        entries[0].config(state="readonly")  # ID solo lectura
        entries[1].insert(0, product_values[2])
        entries[2].insert(0, product_values[3])
        unit_price = product_values[4]
        if isinstance(unit_price, str) and unit_price.startswith("$"):
            unit_price = unit_price[1:]
        entries[4].insert(0, unit_price)
        entries[5].insert(0, product_values[6])
        def save():
            try:
                qty = int(entries[3].get())
                if qty < 0:
                    raise ValueError("La cantidad no puede ser negativa.")
                price = float(entries[4].get())
                if price < 0:
                    raise ValueError("El precio unitario no puede ser negativo.")
                updated_product = Product(
                    original_code,
                    entries[1].get(),
                    entries[2].get(),
                    qty,
                    price,
                    entries[5].get(),
                    datetime.datetime.now().strftime("%d/%m/%Y"),
                )
                self.db.update_product(updated_product)
                self.refresh_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        tk.Button(win, text="Guardar Cambios", command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_product(self, product_values):
        
        #Elimina el producto, usando el ID exactamente como string, sin modificar.
        
        answer = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Seguro que deseas eliminar el producto '{product_values[2]}' (ID: {product_values[1]})?"
        )
        if answer:
            try:
                self.db.delete_product(str(product_values[1]))
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_csv(self):
        
        #Exporta la base de datos a archivo CSV.
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Guardar archivo CSV"
        )
        if file_path:
            try:
                self.db.export_to_csv(file_path)
                messagebox.showinfo("Exportar CSV", "Exportación exitosa.")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando CSV: {e}")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
