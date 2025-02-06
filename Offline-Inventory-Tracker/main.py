import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv
import shutil

# --- Translation Setup ---
translations = {
    "en": {
        "dashboard": "Dashboard: Total Items: {total_items} | Low Stock Items: {low_stock} | Total Value: {total_value:.2f}",
        "add_update_item": "Add or Update Item",
        "item_name": "Item Name:",
        "quantity": "Quantity:",
        "threshold": "Threshold:",
        "price": "Price:",
        "unit": "Unit:",
        "save_item": "Save Item",
        "update_item": "Update Item",
        "inventory": "Inventory",
        "search": "Search:",
        "search_button": "Search",
        "delete_item": "Delete Item",
        "export_csv": "Export to CSV",
        "backup": "Backup Database",
        "restore": "Restore Database",
        "print_inventory": "Print Inventory",
        "help_about": "Offline Inventory Management\nVersion 1.0\nDesigned for small business use.",
    },
    "sw": {
        "dashboard": "Dashibodi: Jumla ya Vitu: {total_items} | Vifaa vya chini: {low_stock} | Thamani ya Jumla: {total_value:.2f}",
        "add_update_item": "Ongeza au Sasisha Bidhaa",
        "item_name": "Jina la Bidhaa:",
        "quantity": "Kiasi:",
        "threshold": "Kiwango:",
        "price": "Bei:",
        "unit": "Kitengo:",
        "save_item": "Hifadhi Bidhaa",
        "update_item": "Sasisha Bidhaa",
        "inventory": "Hifadhidata",
        "search": "Tafuta:",
        "search_button": "Tafuta",
        "delete_item": "Futa Bidhaa",
        "export_csv": "Hamisha kwa CSV",
        "backup": "Hifadhi Nakala ya Hifadhidata",
        "restore": "Rejesha Hifadhidata",
        "print_inventory": "Chapisha Hifadhidata",
        "help_about": "Usimamizi wa Hifadhidata Nje ya Mtandaoni\nToleo 1.0\nKwa matumizi ya biashara ndogo.",
    }
}
current_lang = "en"


def t(key):
    return translations[current_lang].get(key, key)


# --- Database Functions ---
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


def update_item_db(item_id, name, quantity, threshold, price, unit):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE inventory
        SET item_name = ?, quantity = ?, threshold = ?, price = ?, unit = ?
        WHERE id = ?
    """, (name, quantity, threshold, price, unit, item_id))
    connection.commit()
    connection.close()


def delete_item(item_id):
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    connection.commit()
    connection.close()


def fetch_inventory():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()
    connection.close()
    return rows


def export_to_csv():
    inventory = fetch_inventory()
    with open("inventory.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Item Name", "Quantity", "Threshold", "Price", "Unit"])
        writer.writerows(inventory)
    messagebox.showinfo("Export Successful", "Inventory exported to inventory.csv")


def backup_database():
    try:
        shutil.copy("inventory.db", "inventory_backup.db")
        messagebox.showinfo("Backup Successful", "Database backed up as inventory_backup.db")
    except Exception as e:
        messagebox.showerror("Backup Error", f"Failed to backup: {e}")


def restore_database():
    try:
        shutil.copy("inventory_backup.db", "inventory.db")
        messagebox.showinfo("Restore Successful", "Database restored from inventory_backup.db")
    except Exception as e:
        messagebox.showerror("Restore Error", f"Failed to restore: {e}")


def print_inventory():
    try:
        inventory = fetch_inventory()
        with open("inventory_report.txt", "w") as f:
            f.write(f"{'ID':<5} {'Item Name':<20} {'Quantity':<10} {'Threshold':<10} {'Price':<10} {'Unit':<10}\n")
            for item in inventory:
                f.write(f"{item[0]:<5} {item[1]:<20} {item[2]:<10} {item[3]:<10} {item[4]:<10} {item[5]:<10}\n")
        messagebox.showinfo("Print Inventory", "Inventory report generated as inventory_report.txt")
    except Exception as e:
        messagebox.showerror("Print Error", f"Failed to generate report: {e}")


# --- Main GUI ---
def main():
    global current_lang
    initialize_db()
    root = tk.Tk()
    root.title("Offline Inventory Tracker")

    # --- Menu Bar ---
    menu_bar = tk.Menu(root)
    language_menu = tk.Menu(menu_bar, tearoff=0)

    def set_language(lang):
        global current_lang
        current_lang = lang
        update_language()  # update all UI texts

    language_menu.add_command(label="English", command=lambda: set_language("en"))
    language_menu.add_command(label="Swahili", command=lambda: set_language("sw"))
    menu_bar.add_cascade(label="Language", menu=language_menu)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", t("help_about")))
    menu_bar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menu_bar)

    # --- Dashboard ---
    dashboard_label = tk.Label(root, text="", font=("Arial", 12), fg="blue")
    dashboard_label.grid(row=0, column=0, columnspan=3, pady=10)

    # --- Add/Update Section ---
    add_update_label = tk.Label(root, text=t("add_update_item"), font=("Arial", 14, "bold"))
    add_update_label.grid(row=1, column=0, columnspan=3, pady=10)

    item_name_label = tk.Label(root, text=t("item_name"))
    item_name_label.grid(row=2, column=0, sticky=tk.W, padx=5)
    name_entry = tk.Entry(root)
    name_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

    quantity_label = tk.Label(root, text=t("quantity"))
    quantity_label.grid(row=3, column=0, sticky=tk.W, padx=5)
    quantity_entry = tk.Entry(root)
    quantity_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

    threshold_label = tk.Label(root, text=t("threshold"))
    threshold_label.grid(row=4, column=0, sticky=tk.W, padx=5)
    threshold_entry = tk.Entry(root)
    threshold_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

    price_label = tk.Label(root, text=t("price"))
    price_label.grid(row=5, column=0, sticky=tk.W, padx=5)
    price_entry = tk.Entry(root)
    price_entry.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

    unit_label = tk.Label(root, text=t("unit"))
    unit_label.grid(row=6, column=0, sticky=tk.W, padx=5)
    unit_entry = tk.Entry(root)
    unit_entry.grid(row=6, column=1, columnspan=2, padx=5, pady=5)

    save_button = tk.Button(root, text=t("save_item"), command=lambda: on_save_item())
    save_button.grid(row=7, column=0, columnspan=3, pady=10)

    # --- Inventory & Search Section ---
    inventory_label = tk.Label(root, text=t("inventory"), font=("Arial", 14, "bold"))
    inventory_label.grid(row=8, column=0, columnspan=3, pady=10)

    search_label = tk.Label(root, text=t("search"))
    search_label.grid(row=9, column=0, sticky=tk.W, padx=5)
    search_entry = tk.Entry(root)
    search_entry.grid(row=9, column=1, padx=5, pady=5)
    search_button = tk.Button(root, text=t("search_button"), command=lambda: search_items())
    search_button.grid(row=9, column=2, padx=5, pady=5)

    columns = ("ID", "Item Name", "Quantity", "Threshold", "Price", "Unit")
    inventory_table = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        inventory_table.heading(col, text=col)
    inventory_table.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

    # Bind table selection to auto-populate input fields
    def on_inventory_select(event):
        selected = inventory_table.selection()
        if selected:
            item = inventory_table.item(selected[0], "values")
            name_entry.delete(0, tk.END)
            name_entry.insert(0, item[1])
            quantity_entry.delete(0, tk.END)
            quantity_entry.insert(0, item[2])
            threshold_entry.delete(0, tk.END)
            threshold_entry.insert(0, item[3])
            price_entry.delete(0, tk.END)
            price_entry.insert(0, item[4])
            unit_entry.delete(0, tk.END)
            unit_entry.insert(0, item[5])

    inventory_table.bind("<<TreeviewSelect>>", on_inventory_select)

    # --- Action Buttons Frame ---
    button_frame = tk.Frame(root)
    button_frame.grid(row=11, column=0, columnspan=3, pady=10)

    # Update Item Button
    update_button = tk.Button(button_frame, text=t("update_item"), command=lambda: on_update_item())
    update_button.grid(row=0, column=0, padx=5)

    delete_button = tk.Button(button_frame, text=t("delete_item"), command=lambda: on_delete_item())
    delete_button.grid(row=0, column=1, padx=5)

    export_button = tk.Button(button_frame, text=t("export_csv"), command=export_to_csv)
    export_button.grid(row=0, column=2, padx=5)

    backup_button = tk.Button(button_frame, text=t("backup"), command=backup_database)
    backup_button.grid(row=0, column=3, padx=5)

    restore_button = tk.Button(button_frame, text=t("restore"),
                               command=lambda: [restore_database(), update_inventory_table()])
    restore_button.grid(row=0, column=4, padx=5)

    print_button = tk.Button(button_frame, text=t("print_inventory"), command=print_inventory)
    print_button.grid(row=0, column=5, padx=5)

    # --- Functions with Access to Widgets ---
    def update_dashboard():
        inventory = fetch_inventory()
        total_items = len(inventory)
        low_stock = sum(1 for item in inventory if item[2] < item[3])
        total_value = sum(item[2] * (item[4] if item[4] is not None else 0) for item in inventory)
        dashboard_label.config(
            text=t("dashboard").format(total_items=total_items, low_stock=low_stock, total_value=total_value))

    def update_inventory_table():
        for row in inventory_table.get_children():
            inventory_table.delete(row)
        for item in fetch_inventory():
            if item[2] < item[3]:
                color = "red"
            elif item[2] == item[3]:
                color = "orange"
            else:
                color = "green"
            inventory_table.insert("", tk.END, values=item, tags=(color,))
        inventory_table.tag_configure("red", foreground="red")
        inventory_table.tag_configure("orange", foreground="orange")
        inventory_table.tag_configure("green", foreground="green")
        update_dashboard()

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
            quantity_int = int(quantity)
            threshold_int = int(threshold)
            price_float = float(price)
            save_item(name, quantity_int, threshold_int, price_float, unit)
            update_inventory_table()
            name_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)
            threshold_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            unit_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Item saved successfully!")
        except ValueError:
            messagebox.showerror("Input Error", "Quantity, threshold, and price must be numeric.")

    def on_update_item():
        selected = inventory_table.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an item to update.")
            return
        item_id = inventory_table.item(selected[0], "values")[0]
        name = name_entry.get()
        quantity = quantity_entry.get()
        threshold = threshold_entry.get()
        price = price_entry.get()
        unit = unit_entry.get()
        if not name or not quantity or not threshold or not price or not unit:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return
        try:
            quantity_int = int(quantity)
            threshold_int = int(threshold)
            price_float = float(price)
            update_item_db(item_id, name, quantity_int, threshold_int, price_float, unit)
            update_inventory_table()
            messagebox.showinfo("Success", "Item updated successfully!")
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

    def search_items():
        term = search_entry.get().lower()
        for row in inventory_table.get_children():
            inventory_table.delete(row)
        for item in fetch_inventory():
            if term in item[1].lower():
                inventory_table.insert("", tk.END, values=item)

    def update_language():
        add_update_label.config(text=t("add_update_item"))
        item_name_label.config(text=t("item_name"))
        quantity_label.config(text=t("quantity"))
        threshold_label.config(text=t("threshold"))
        price_label.config(text=t("price"))
        unit_label.config(text=t("unit"))
        save_button.config(text=t("save_item"))
        update_button.config(text=t("update_item"))
        inventory_label.config(text=t("inventory"))
        search_label.config(text=t("search"))
        search_button.config(text=t("search_button"))
        delete_button.config(text=t("delete_item"))
        export_button.config(text=t("export_csv"))
        backup_button.config(text=t("backup"))
        restore_button.config(text=t("restore"))
        print_button.config(text=t("print_inventory"))
        update_dashboard()

    update_inventory_table()
    root.mainloop()


if __name__ == "__main__":
    main()