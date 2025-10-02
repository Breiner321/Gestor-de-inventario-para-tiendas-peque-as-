from database import InventoryDatabase

def main():
    # Función principal que inicializa la base de datos y muestra productos en consola.
    db = InventoryDatabase()
    try:
        products = db.load()
        print(f"Total products: {len(products)}")
        for prod in products:
            print(f"{prod.code} | {prod.name} | Qty: {prod.quantity} | ${prod.unit_price}")
    except Exception as e:
        print(" Error al cargar productos:", e)

if __name__ == "__main__":
    main()
