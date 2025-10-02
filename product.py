class Product:
    
    #Clase que representa un producto individual del inventario.
    

    def __init__(self, code, name, description, quantity, unit_price, warehouse, last_update):
        
        #Inicializa un producto con validaciones de cantidad y precio.
        
        if quantity < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        if unit_price < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        self.code = str(code)  # SIEMPRE como string, garantiza ceros a la izquierda
        self.name = name
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.warehouse = warehouse
        self.last_update = last_update

    def total_value(self):
        
        #Calcula el valor total de este producto.
        
        return self.quantity * self.unit_price

    def to_tuple(self):
        
        #Devuelve los datos del producto como tupla, para operaciones DB.
        
        return (
            self.code, self.name, self.description,
            self.quantity, self.unit_price,
            self.warehouse, self.last_update
        )

    @staticmethod
    def from_tuple(data):
        
        #Crea un producto desde una tupla (útil para cargar desde DB).
        
        return Product(*data)


