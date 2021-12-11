#
# Name : Product.py
# Author: Robby Nervig
# Created : 12/10/2021
# Course: CIS 152 - Data Structure
# Version: 1.0
# OS: Windows 10
# IDE: PyCharm 2021.2.1 (Community Edition)
# Copyright : This is my own original work
#   based on specifications issued by our instructor
# Description : This is the class used to manage products in the expiration tracker.
# Academic Honesty: I attest that this is my original work.
#   I have not used unauthorized source code, either modified or
#   unmodified. I have not given other fellow student(s) access
#   to my program.
#
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
