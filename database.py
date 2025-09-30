import sqlite3
from product import Product

class InventoryDatabase:
    def __init__(self, db_name="inventory.db"):
        # Solo el nombre -> se crea en la carpeta actual del proyecto
        self.db_name = db_name
        print(f"Database path: {self.db_name}")
        self.create_table()

    def create_table(self):
        """Crea la tabla products si no existe"""
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
        """Agrega o actualiza un producto"""
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
        """Carga todos los productos desde la base de datos"""
        products = []
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT code, name, description, quantity, unit_price, warehouse, last_update 
                FROM products
            """)
            rows = cursor.fetchall()
            for row in rows:
                code, name, description, quantity, unit_price, warehouse, last_update = row
                products.append(Product(
                    code or "",
                    name or "",
                    description or "",
                    quantity if quantity is not None else 0,
                    unit_price if unit_price is not None else 0.0,
                    warehouse or "",
                    last_update or ""
                ))
        return products
