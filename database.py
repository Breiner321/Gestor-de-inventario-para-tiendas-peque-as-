import sqlite3
import csv
from product import Product
import datetime

class InventoryDatabase:
    
    #Clase que gestiona las operaciones de base de datos para el inventario.
    

    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        
        #Crea la tabla de productos si no existe.
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    quantity INTEGER NOT NULL CHECK (quantity >= 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0),
                    warehouse TEXT,
                    last_update TEXT
                )
            """)
            conn.commit()

    def add_product(self, product: Product):
        
        #Agrega o reemplaza un producto en la base de datos.
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO products
                (code, name, description, quantity, unit_price, warehouse, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(product.code),  # SIEMPRE como string
                product.name,
                product.description,
                product.quantity,
                product.unit_price,
                product.warehouse,
                product.last_update
            ))
            conn.commit()

    def update_product(self, product: Product):
        
        #Actualiza los datos de un producto existente.
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products
                SET name=?, description=?, quantity=?, unit_price=?, warehouse=?, last_update=?
                WHERE code=?
            """, (
                product.name,
                product.description,
                product.quantity,
                product.unit_price,
                product.warehouse,
                product.last_update,
                str(product.code)
            ))
            conn.commit()

    def delete_product(self, code):
        
        #Elimina un producto usando su código (como string).
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE code = ?", (str(code),))
            conn.commit()

    def load(self):
        
        #Carga todos los productos de la base de datos y los devuelve como objetos Product.
        
        products = []
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, description, quantity, unit_price, warehouse, last_update FROM products")
            rows = cursor.fetchall()
            for row in rows:
                products.append(Product.from_tuple(row))
        return products

    def export_to_csv(self, file_path):
        
        #Exporta toda la base de datos de productos a un archivo CSV.
        
        products = self.load()
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['code', 'name', 'description', 'quantity', 'unit_price', 'warehouse', 'last_update'])
            for p in products:
                writer.writerow([p.code, p.name, p.description, p.quantity, p.unit_price, p.warehouse, p.last_update])

