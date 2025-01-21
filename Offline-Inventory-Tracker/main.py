import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv

# Database setup
def initialize_db():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            threshold INTEGER NOT NULL,
            price REAL,
            unit TEXT
        )
    """)
    connection.commit()
    connection.close()

# Add or update item in the database
def save_item(name, quantity, threshold, price, unit):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO inventory (item_name, quantity, threshold, price, unit)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_name) DO UPDATE SET
        quantity=excluded.quantity,
        threshold=excluded.threshold,
        price=excluded.price,
        unit=excluded.unit
    """, (name, quantity, threshold, price, unit))
    connection.commit()
    connection.close()

# Delete item from the database
def delete_item(item_id):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    connection.commit()
    connection.close()

# Get all inventory items
def fetch_inventory():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    connection.close()
    return rows

# Export inventory to CSV
def export_to_csv():
    inventory = fetch_inventory()
    with open("inventory.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Item Name", "Quantity", "Threshold", "Price", "Unit"])
        writer.writerows(inventory)
    messagebox.showinfo("Export Successful", "Inventory exported to inventory.csv")

# GUI setup
def main():
    initialize_db()

    def on_save_item():
        name = name_entry.get()
        quantity = quantity_entry.get()
        threshold = threshold_entry.get()
        price = price_entry.get()
        unit = unit_entry.get()

        if not name or not quantity or not threshold or not price or not unit:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return

        try:
            quantity = int(quantity)
            threshold = int(threshold)
            price = float(price)
            save_item(name, quantity, threshold, price, unit)
            update_inventory_table()
            name_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)
            threshold_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Item saved successfully!")
        except ValueError:
            messagebox.showerror("Input Error", "Quantity, threshold, and price must be numeric.")

    def on_delete_item():
        selected_item = inventory_table.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return

        item_id = inventory_table.item(selected_item[0], "values")[0]
        delete_item(item_id)
        update_inventory_table()
        messagebox.showinfo("Success", "Item deleted successfully!")

    def update_inventory_table():
        for row in inventory_table.get_children():
            inventory_table.delete(row)

        for item in fetch_inventory():
            color = "black"
            if item[2] < item[3]:  # Quantity < Threshold
                color = "red"
            elif item[2] == item[3]:  # Quantity == Threshold
                color = "yellow"
            else:  # Quantity > Threshold
                color = "green"

            inventory_table.insert("", tk.END, values=item, tags=(color,))

        inventory_table.tag_configure("red", foreground="red")
        inventory_table.tag_configure("yellow", foreground="orange")
        inventory_table.tag_configure("green", foreground="green")

    # Main window
    root = tk.Tk()
    root.title("Offline Inventory Tracker")

    # Add Item Section
    tk.Label(root, text="Add or Update Item").grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(root, text="Item Name:").grid(row=1, column=0, sticky=tk.W, padx=5)
    name_entry = tk.Entry(root)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="Quantity:").grid(row=2, column=0, sticky=tk.W, padx=5)
    quantity_entry = tk.Entry(root)
    quantity_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(root, text="Threshold:").grid(row=3, column=0, sticky=tk.W, padx=5)
    threshold_entry = tk.Entry(root)
    threshold_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(root, text="Price:").grid(row=4, column=0, sticky=tk.W, padx=5)
    price_entry = tk.Entry(root)
    price_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(root, text="Unit:").grid(row=5, column=0, sticky=tk.W, padx=5)
    unit_entry = tk.Entry(root)
    unit_entry.grid(row=5, column=1, padx=5, pady=5)

    save_button = tk.Button(root, text="Save Item", command=on_save_item)
    save_button.grid(row=6, column=0, columnspan=2, pady=10)

    # Inventory Table
    tk.Label(root, text="Inventory").grid(row=7, column=0, columnspan=2, pady=10)

    columns = ("ID", "Item Name", "Quantity", "Threshold", "Price", "Unit")
    inventory_table = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        inventory_table.heading(col, text=col)
    inventory_table.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    update_inventory_table()

    # Delete Button
    delete_button = tk.Button(root, text="Delete Item", command=on_delete_item)
    delete_button.grid(row=9, column=0, columnspan=2, pady=10)

    # Export Button
    export_button = tk.Button(root, text="Export to CSV", command=export_to_csv)
    export_button.grid(row=10, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()