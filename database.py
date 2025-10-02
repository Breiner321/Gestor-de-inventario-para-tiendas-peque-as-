import sqlite3
from product import Product

class InventoryDatabase:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                warehouse TEXT,
                last_update TEXT
            )
            """)
            conn.commit()

    def add_product(self, product: Product):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO products
            (code, name, description, quantity, unit_price, warehouse, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                product.code, product.name, product.description,
                product.quantity, product.unit_price,
                product.warehouse, product.last_update
            ))
            conn.commit()

    def load(self):
        products = []
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, name, description, quantity, unit_price, warehouse, last_update FROM products")
            rows = cursor.fetchall()
            for row in rows:
                code, name, description, quantity, unit_price, warehouse, last_update = row
                products.append(Product(
                    code, name, description, quantity, unit_price, warehouse, last_update
                ))
        return products

    def update_product(self, updated_product):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE products
            SET name=?, description=?, quantity=?, unit_price=?, warehouse=?, last_update=?
            WHERE code=?
            """, (
                updated_product.name,
                updated_product.description,
                updated_product.quantity,
                updated_product.unit_price,
                updated_product.warehouse,
                updated_product.last_update,
                updated_product.code
            ))
            if cursor.rowcount == 0:
                raise ValueError(f"Producto con código {updated_product.code} no encontrado")
            conn.commit()

    def delete_product(self, code):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE code=?", (code,))
            if cursor.rowcount == 0:
                raise ValueError(f"Producto con código {code} no encontrado")
            conn.commit()