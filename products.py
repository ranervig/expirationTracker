
class Product:
    def __init__(self, p_id, name, quantity, aisle, shelf, date=None ):
        self.p_id = p_id
        self.name = name
        self.quantity = quantity
        self.aisle = aisle
        self.shelf = shelf
        self.date = date

    def __repr__(self):
        return f'{self.p_id}, {self.name}, {self.quantity}, {self.aisle}, {self.shelf}, {self.date}'

    # only used for sorting
    def __lt__(self, other):
        if self.aisle == other.aisle:
            if self.shelf == other.shelf:
                if self.date == other.date:
                    return True
                return self.date < other.date
            return self.shelf < other.shelf
        return self.aisle < other.aisle
