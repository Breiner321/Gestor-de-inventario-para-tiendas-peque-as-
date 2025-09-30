class Product:
    def __init__(self, code, name, description, quantity, unit_price, warehouse, last_update):
        self.code = code
        self.name = name
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.warehouse = warehouse
        self.last_update = last_update

    def total_value(self):
        return self.quantity * self.unit_price

    def to_tuple(self):
        return (
            self.code, self.name, self.description,
            self.quantity, self.unit_price,
            self.warehouse, self.last_update
        )

    @staticmethod
    def from_tuple(data):
        return Product(*data)
