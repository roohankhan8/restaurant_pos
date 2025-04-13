import tkinter as tk
from tkinter import ttk
import csv # Import the csv module

class RestaurantPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant POS System")

        self.menu_items = self.load_menu_from_csv('menu.csv') # Load menu from CSV
        self.current_category = tk.StringVar(self.root)
        if self.menu_items:
            self.current_category.set(list(self.menu_items.keys())[0]) # Set initial category
        else:
            self.current_category.set("") # Or some default if menu is empty
        self.order = {} # Dictionary to store order items with quantities
        self._order_display_list = [] # Separate list to track order for display
        self.total = tk.DoubleVar(self.root, value=0.00) # Variable to hold the order total

        self.setup_ui()
        if self.menu_items:
            self.show_menu_items(self.current_category.get())

    def load_menu_from_csv(self, filename):
        menu = {}
        try:
            with open(filename, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    category = row['Category'].strip()
                    item = row['Item'].strip()
                    try:
                        price = float(row['Price'].strip())
                        if category not in menu:
                            menu[category] = {}
                        menu[category][item] = price
                    except ValueError:
                        print(f"Warning: Invalid price '{row['Price']}' for item '{item}'. Skipping.")
        except FileNotFoundError:
            print(f"Error: Menu file '{filename}' not found.")
            return {}
        return menu

    def setup_ui(self):
        # --- Frames ---
        self.menu_frame = ttk.LabelFrame(self.root, text="Menu")
        self.menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.order_frame = ttk.LabelFrame(self.root, text="Order")
        self.order_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew", rowspan=2)

        self.action_frame = ttk.LabelFrame(self.root, text="Actions")
        self.action_frame.grid(row=1, column=0, padx=10, pady=10, sticky="sew")

        # --- Menu Category Buttons ---
        self.category_buttons = {}
        category_column = 0
        for category in self.menu_items.keys():
            button = ttk.Button(self.menu_frame, text=category,
                                command=lambda cat=category: self.show_menu_items(cat))
            button.grid(row=0, column=category_column, padx=5, pady=5, sticky="ew")
            self.category_buttons[category] = button
            category_column += 1

        # --- Menu Item Buttons Frame ---
        self.item_buttons_frame = ttk.Frame(self.menu_frame)
        self.item_buttons_frame.grid(row=1, column=0, columnspan=len(self.menu_items), padx=5, pady=5, sticky="nsew")

        # --- Order Display ---
        self.order_list = tk.Listbox(self.order_frame, width=40, height=15)
        self.order_list.pack(padx=10, pady=10, fill="both", expand=True)

        self.total_label = ttk.Label(self.order_frame, text=f"Total: ${self.total.get():.2f}", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5, anchor="se")

        # --- Action Buttons ---
        # add_button = ttk.Button(self.action_frame, text="Add Item", command=self.add_item_to_order)
        # add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        remove_button = ttk.Button(self.action_frame, text="Remove Item", command=self.remove_item_from_order)
        remove_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        clear_button = ttk.Button(self.action_frame, text="Clear Order", command=self.clear_order)
        clear_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        checkout_button = ttk.Button(self.action_frame, text="Checkout", command=self.checkout)
        checkout_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- Grid Configuration for Menu Frame ---
        self.menu_frame.grid_rowconfigure(1, weight=1)
        for i in range(len(self.menu_items)):
            self.menu_frame.grid_columnconfigure(i, weight=1)

    def show_menu_items(self, category):
        # Clear any existing item buttons
        for widget in self.item_buttons_frame.winfo_children():
            widget.destroy()

        # Get the items for the selected category
        items = self.menu_items.get(category, {})

        # Create and display buttons for each item
        row_num = 0
        col_num = 0
        for item_name, price in items.items():
            button = ttk.Button(self.item_buttons_frame, text=f"{item_name} (${price:.2f})",
                                command=lambda name=item_name, cost=price: self.add_to_order(name, cost))
            button.grid(row=row_num, column=col_num, padx=5, pady=5, sticky="ew")
            col_num += 1
            if col_num > 2: # Arrange items in a grid (you can adjust the number of columns)
                col_num = 0
                row_num += 1

        # Configure grid weights for resizing of item buttons frame
        for i in range(3): # Assuming a maximum of 3 columns for items
            self.item_buttons_frame.grid_columnconfigure(i, weight=1)
        for i in range(row_num + 1):
            self.item_buttons_frame.grid_rowconfigure(i, weight=1)

    def add_to_order(self, item_name, price):
        if item_name in self.order:
            self.order[item_name]['quantity'] += 1
        else:
            self.order[item_name] = {'price': price, 'quantity': 1}
        self._update_order_display_list()
        self.update_order_display()

    def _update_order_display_list(self):
        self._order_display_list = []
        for item_name, details in self.order.items():
            for _ in range(details['quantity']):
                self._order_display_list.append(item_name)
    
    def update_order_display(self):
        self.order_list.delete(0, tk.END) # Clear the current listbox
        current_total = 0
        for item_name, details in self.order.items():
            quantity = details['quantity']
            price = details['price']
            item_total = quantity * price
            self.order_list.insert(tk.END, f"{item_name} x {quantity} - ${item_total:.2f}")
            current_total += item_total
        self.total.set(current_total)
        self.total_label.config(text=f"Total: ${self.total.get():.2f}")

    def remove_item_from_order(self):
        selected_index = self.order_list.curselection()
        if selected_index:
            index_to_remove = selected_index[0]
            if 0 <= index_to_remove < len(self._order_display_list):
                item_to_remove = self._order_display_list.pop(index_to_remove)
                if item_to_remove in self.order:
                    self.order[item_to_remove]['quantity'] -= 1
                    if self.order[item_to_remove]['quantity'] == 0:
                        del self.order[item_to_remove]
                self._update_order_display_list()
                self.update_order_display()
                print(f"Removed one {item_to_remove}")

    def clear_order(self):
        self.order = {}
        self._order_display_list = []
        self.total.set(0.00)
        self.update_order_display()
        print("Order cleared.")

    def checkout(self):
        total = self.total.get()
        print(f"Total amount due: ${total:.2f}")
        tk.messagebox.showinfo("Checkout", f"Total amount due: ${total:.2f}\nPayment processing not implemented.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantPOS(root)
    root.mainloop()