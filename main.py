#
# Name : main.py
# Author: Robby Nervig
# Created : 12/10/2021
# Course: CIS 152 - Data Structure
# Version: 1.0
# OS: Windows 10
# IDE: PyCharm 2021.2.1 (Community Edition)
# Copyright : This is my own original work
#   based on specifications issued by our instructor
# Description : This program uses a GUI to create an expiration tracker for stores.
# Academic Honesty: I attest that this is my original work.
#   I have not used unauthorized source code, either modified or
#   unmodified. I have not given other fellow student(s) access
#   to my program.
#
import heapq
import tkinter as tk
from tkinter import ttk, messagebox
import tkcalendar as tkc
import database as db
from tkinter import filedialog as fd
from datetime import date, timedelta
from products import Product

# Number of days ahead of expiration date product should be pulled.
MINIMUM_DAYS_TO_PULL_PRODUCT = 1
MAXIMUM_DAYS_TO_PULL_PRODUCT = 7


def selection_sort(sorting_list):
    for index in range(0, len(sorting_list)):
        minimum_index = index
        # find minimum in unsorted section
        for place in range(index + 1, len(sorting_list)):
            if sorting_list[place][2] < sorting_list[minimum_index][2]:
                minimum_index = place
        # swap minimum with first in unsorted section
        sorting_list[index], sorting_list[minimum_index] = sorting_list[minimum_index], sorting_list[index]


def format_date(in_date):
    """
    Formats the date as MM/DD/YYYY
    :param in_date: date to format
    :return: formatted date string
    """
    if in_date is None:
        return "No Date"
    return in_date.strftime("%m/%d/%Y")


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expiration Tracker")
        self.geometry("850x350")
        # Capture date
        self.today = date.today()
        style = ttk.Style(self)
        style.theme_use('clam')

        # List to hold Products as data layer for the display
        self.product_list = []
        self.product_display = ProductDisplay(master=self)
        self.product_display.grid(row=0, column=2, rowspan=6, padx=5, pady=5)

        self.config(menu=MenuBar(master=self))

        self.date_label = tk.Label(self, text=f'Today: {self.today.strftime("%m/%d/%Y")}')
        self.date_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)

        self.date_picker = tk.Frame(self)
        self.calendar = tkc.Calendar(self.date_picker, mindate=self.today, showweeknumbers=False,
                                     selectbackground='#ADD8E6', selectforeground='#000000')
        self.calendar.pack()
        self.date_button = tk.Button(self.date_picker, text="Set Date", command=self.set_date)
        self.date_button.pack()
        self.date_picker.grid(row=1, column=3)
        self.date_picker.grid_remove()

        self.pull_day_options = range(MINIMUM_DAYS_TO_PULL_PRODUCT, MAXIMUM_DAYS_TO_PULL_PRODUCT + 1)
        self.pull_day_str = tk.StringVar()
        self.pull_day_str.set(self.pull_day_options[1])
        self.pull_day_menu = tk.OptionMenu(self, self.pull_day_str, *self.pull_day_options, command=self.pull_selected)
        self.pull_days = int(self.pull_day_str.get())
        self.pull_day_menu.grid(row=1, column=1)

        self.pull_day_label = tk.Label(self, text='Pull Days:')
        self.pull_day_label.grid(row=1, column=0)

        self.submit_button = tk.Button(self, text='Submit Dates', command=self.update_db)
        self.submit_button.grid(row=2, column=0, padx=5, pady=10)
        self.submit_button.grid_forget()
        self.outdated_button = tk.Button(self, text=f'Get Outdated Products\nfor next {self.pull_days} days',
                                         command=self.get_outdated)
        self.outdated_button.grid(row=3, column=0, padx=5, pady=10)

    def update_today(self, new_date):
        """
        Sets a new date for expiration calculations.
        :param new_date: date to set
        """
        self.today = new_date
        self.date_label.configure(text=f'Today: {format_date(self.today)}')

    def get_new_products(self, filename):
        """
        Calls the database functions to get products from chosen database file.
        Then clears the product list and product display before filling them amd showing on the date controls.
        :param filename: Database file to pull data from
        """
        records = db.get_data_from_file(filename)
        self.product_list.clear()
        self.product_display.clear_display()
        for record in records:
            self.product_list.append(Product(*record))
        self.product_display.insert_rows(self.product_list)
        self.product_display.set_first_selection()
        self.date_picker.grid()
        self.submit_button.grid()

    def set_date(self):
        selected = self.product_display.get_selected()
        for index in selected:
            self.product_list[int(index[0])].date = self.calendar.selection_get()
        self.product_display.clear_display()
        self.product_display.insert_rows(self.product_list)

    def check_no_date(self):
        count = sum(prod.date is None for prod in self.product_list)
        if count > 0:
            choice = messagebox.askokcancel(title='Warning', message=f'There are: {count} items without a date set!\n '
                                                                     f'Press OK to set items to default 7 day dating.')
            if not choice:
                return
            for prod in self.product_list:
                if prod.date is None:
                    prod.date = self.today + timedelta(weeks=1)

    def update_db(self):
        self.check_no_date()
        database = db.DataBase()
        database.insert_new_dated_products(self.product_list)
        database.__del__()  # Ensure that the database connection is closed
        self.date_picker.grid_remove()
        self.submit_button.grid_remove()
        self.product_display.clear_display()
        self.product_list.clear()

    def get_outdated(self):
        database = db.DataBase()
        tup_products = database.get_products_one_week(self.today)
        next_week_products = []
        for prod in tup_products:
            temp_prod = Product(prod[1], prod[2], prod[3], prod[4], prod[5], prod[6])
            # create tuple for sorting (days until expiration, unique oid from database, product)
            next_week_products.append((temp_prod.date - self.today, prod[0], temp_prod))
        # Priority Queue sorting by days until expiration with fallback of oid
        heapq.heapify(next_week_products)
        outdated = []
        while next_week_products and next_week_products[0][0] <= timedelta(days=self.pull_days):
            # Only gets the products that have <= the number of days to pull product early
            outdated.append(heapq.heappop(next_week_products))
        if not outdated:
            messagebox.showerror(title="Not Found", message='No outdated product found!')
        else:
            self.product_list = outdated
            ExpiredWindow(master=self)

    def pull_selected(self, event):
        self.pull_days = int(self.pull_day_str.get())
        self.outdated_button.config(text=f'Get Outdated Products\nfor next {self.pull_days} days')


class MenuBar(tk.Menu):
    def __init__(self, **kw):
        super().__init__(**kw)

        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Load file", command=self.get_file)
        file_menu.add_separator()
        file_menu.add_command(label="Unload File", command=self.unload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        self.add_cascade(label="File", menu=file_menu)
        tools_menu = tk.Menu(self, tearoff=0)
        tools_menu.add_command(label="Change Today's Date", command=lambda: DateWindow(master=self.master))
        self.add_cascade(label="Tools", menu=tools_menu)

    def get_file(self):
        """Gets the location of the invoice files"""
        filetypes = (
            ("Database files", "*.db"),
        )
        filename = fd.askopenfilename(filetypes=filetypes)
        if filename:
            self.master.get_new_products(filename)

    def unload_file(self):
        """Clear the tree if it contains anything"""
        if not self.master.product_display.is_empty():
            self.master.date_picker.grid_remove()
            self.master.product_display.clear_display()
            self.master.product_list.clear()
            self.master.submit_button.grid_remove()


class ProductDisplay(tk.Frame):
    def __init__(self, **kw):
        super().__init__(**kw)

        scroll = tk.Scrollbar(self)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_tree = ttk.Treeview(self, yscrollcommand=scroll.set)
        scroll.config(command=self.product_tree.yview)
        # Styling the Treeview
        style = ttk.Style()
        self.product_tree.tag_configure('odd', background="#FFFFFF")
        self.product_tree.tag_configure('even', background="#F3F3F3")
        # Workaround for tkinter 8.6.9
        actual_theme = style.theme_use()
        style.theme_create('zebra', parent=actual_theme)
        style.theme_use('zebra')
        style.map('Treeview', background=[('selected', '#ADD8E6')])
        # Define Columns
        self.product_tree['columns'] = ('PID', 'Product Name', 'Quantity', 'Aisle', 'Shelf', 'Date')
        self.product_tree.column('#0', width=0, stretch=tk.NO)
        self.product_tree.column('PID', width=30, anchor=tk.W)
        self.product_tree.column('Product Name', width=120, anchor=tk.W)
        self.product_tree.column('Quantity', width=55)
        self.product_tree.column('Aisle', width=35)
        self.product_tree.column('Shelf', width=35)
        self.product_tree.column('Date', width=80)
        # Define Headings
        self.product_tree.heading('#0', text='', anchor=tk.W)
        self.product_tree.heading('PID', text='PID', anchor=tk.W)
        self.product_tree.heading('Product Name', text='Product Name', anchor=tk.W)
        self.product_tree.heading('Quantity', text='Quantity', anchor=tk.W)
        self.product_tree.heading('Aisle', text='Aisle', anchor=tk.W)
        self.product_tree.heading('Shelf', text='Shelf', anchor=tk.W)
        self.product_tree.heading('Date', text='Date', anchor=tk.W)
        self.product_tree.pack()

    def insert_rows(self, records):
        for index, record in enumerate(records):
            tag = ('even',) if index % 2 == 0 else ('odd',)
            self.product_tree.insert(parent='', index='end', iid=index, values=(
                record.p_id, record.name, record.quantity, record.aisle, record.shelf,
                format_date(record.date)), tag=tag)

    def set_first_selection(self):
        self.product_tree.selection_set(0)

    def clear_display(self):
        """Clears the product_tree by deleting all of it's children."""
        self.product_tree.delete(*self.product_tree.get_children())

    def is_empty(self):
        """Checks if the product_tree is empty"""
        if not self.product_tree.get_children():
            return True
        return False

    def get_selected(self):
        return self.product_tree.selection()


class DateWindow(tk.Toplevel):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title("Change Date")
        self.grab_set()
        self.cal = tkc.Calendar(self, mindate=self.master.today, showweeknumbers=False, selectbackground='#ADD8E6',
                                selectforeground='#000000')
        self.cal.pack()
        select_button = tk.Button(self, text="Set Today's Date", command=self.set_today)
        select_button.pack()

    def set_today(self):
        self.master.update_today(self.cal.selection_get())
        self.destroy()


class ExpiredWindow(tk.Toplevel):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title("Outdated Product")
        self.grab_set()
        self.outdated = self.master.product_list
        selection_sort(self.outdated)
        self.checked = {}  # holds oid and checked status
        for index, prod in enumerate(self.outdated):
            self.checked[prod[1]] = tk.IntVar()
            # tk.Label(self, text=f'{prod[2]}').grid(row=index, column=0)
            check = tk.Checkbutton(self, text=f'{prod[2]}', variable=self.checked[prod[1]], anchor=tk.W)
            check.pack(fill='both')
        button = tk.Button(self, text="Remove Checked Items", command=self.removed_checked_products, anchor=tk.CENTER)
        button.pack(fill='both')

    def removed_checked_products(self):
        """The products that have been checked as pulled are removed from the database"""
        product_to_remove = [oid for oid, v in self.checked.items() if v.get() == 1]
        database = db.DataBase()
        database.remove_products(product_to_remove)
        self.destroy()


def main():
    my_gui = MainWindow()
    my_gui.mainloop()


if __name__ == '__main__':
    main()
