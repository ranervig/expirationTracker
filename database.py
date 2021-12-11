#
# Name : database.py
# Author: Robby Nervig
# Created : 12/10/2021
# Course: CIS 152 - Data Structure
# Version: 1.0
# OS: Windows 10
# IDE: PyCharm 2021.2.1 (Community Edition)
# Copyright : This is my own original work
#   based on specifications issued by our instructor
# Description : This is the database Layer of the expiration tracker program.
# Academic Honesty: I attest that this is my original work.
#   I have not used unauthorized source code, either modified or
#   unmodified. I have not given other fellow student(s) access
#   to my program.
#
import sqlite3 as sq3
from datetime import timedelta


def get_data_from_file(filename):
    """Pulls data from the selected file."""
    connection = sq3.connect(filename)
    cur = connection.cursor()
    cur.execute("SELECT * FROM products")
    results = cur.fetchall()
    connection.close()
    return results


class DataBase:
    def __init__(self):
        self.connection = sq3.connect('dated_products.db', detect_types=sq3.PARSE_DECLTYPES | sq3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
        # Create db if it doesn't exist
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS products(
            p_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            aisle TEXT,
            shelf TEXT,
            date DATE)
            """)

    def __del__(self):
        self.connection.close()

    def insert_new_dated_products(self, records):
        for record in records:
            self.cursor.execute("INSERT INTO products values(:id, :product_name, :quantity, :aisle, :shelf, :date)",
                                {'id': record.p_id,
                                 'product_name': record.name,
                                 'quantity': record.quantity,
                                 'aisle': record.aisle,
                                 'shelf': record.shelf,
                                 'date': record.date
                                 }
                                )
        self.connection.commit()

    def remove_products(self, products_oid):
        for oid in products_oid:
            self.cursor.execute("DELETE FROM products WHERE oid = ?", (oid,))
        self.connection.commit()

    def get_all_products(self):
        self.cursor.execute("SELECT oid, * FROM products")
        return self.cursor.fetchall()

    def get_products_one_week(self, today):
        week_out = today + timedelta(weeks=1)
        self.cursor.execute("SELECT oid, * FROM products WHERE date <= ?", (str(week_out),))
        return self.cursor.fetchall()


''' invoice1.db
(0, 'Hot Salsa', 12, '2', 'A'), 
(1, 'Mild Salsa', 12, '2', 'B'), 
(2, 'Chunky Guacamole', 16, '1', 'A'), 
(3, 'Hot Guacamole', 16, '1', 'A'), 
(4, 'Sour Cream', 8, '2', 'B'), 
(5, 'Jalapeno Dip', 6, '2', 'B'), 
(6, 'Red Pepper Hummus', 12, '1', 'C'), 
(7, 'Original Hummus', 12, '1', 'C'), 
(8, 'Garlic Hummus', 12, '1', 'C'), 
(9, 'Spicy Hummus', 12, '1', 'C')
'''
''' invoice2.db
(35, 'Strawberry Smoothie', 8, '1', 'D'), 
(36, 'Strawberry Banana Smoothie', 8, '1', 'D'), 
(37, 'Vanilla Chai Tea', 8, '1', 'D'), 
(38, 'Berry Blue', 8, '1', 'D'), 
(39, 'Berry Blast', 8, '1', 'D'), 
(40, 'Banana Honey Almond Butter Shake', 8, '1', 'E'), 
(41, 'Daily Greens with Fruit Juice', 8, '1', 'E'), 
(42, 'Red Goodness Juice', 8, '1', 'E'), 
(43, 'Green Immunity Juice', 8, '1', 'E')
'''
''' invoice3.db
(0, 'Hot Salsa', 12, '2', 'A'), 
(2, 'Chunky Guacamole', 16, '1', 'A'), 
(3, 'Hot Guacamole', 16, '1', 'A'), 
(3, 'Hot Guacamole', 16, '1', 'A'), 
(4, 'Sour Cream', 8, '2', 'B'), 
(6, 'Red Pepper Hummus', 12, '1', 'C'), 
(6, 'Red Pepper Hummus', 12, '1', 'C'), 
(7, 'Original Hummus', 12, '1', 'C'), 
(8, 'Garlic Hummus', 12, '1', 'C'), 
(35, 'Strawberry Smoothie', 8, '1', 'D'), 
(36, 'Strawberry Banana Smoothie', 8, '1', 'D'), 
(42, 'Red Goodness Juice', 8, '1', 'E'), 
(40, 'Banana Honey Almond Butter Shake', 8, '1', 'E'), 
(41, 'Daily Greens with Fruit Juice', 8, '1', 'E'), 
(42, 'Red Goodness Juice', 8, '1', 'E'), 
(43, 'Green Immunity Juice', 8, '1', 'E')
'''
