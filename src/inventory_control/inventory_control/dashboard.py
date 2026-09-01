import tkinter as tk
from tkinter import font

class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management Dashboard")
        self.root.geometry("950x650") # Taller window for extra data
        self.root.configure(bg="white")

        # Custom Fonts
        self.header_font = font.Font(family="Arial", size=12, weight="bold")
        self.label_font = font.Font(family="Arial", size=10)
        self.value_font = font.Font(family="Arial", size=10, weight="bold")

        # --- MAIN LAYOUT ---
        self.top_container = tk.Frame(self.root, bg="white")
        self.top_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.bottom_container = tk.Frame(self.root, bg="white")
        self.bottom_container.pack(fill="x", padx=20, pady=(0, 20))

        # --- SHELF DATA STORAGE ---
        self.shelf_widgets = {} 
        
        # Define your specific shelves here
        self.create_shelf_box(1, "Shelf 1 (Green)", self.top_container)
        self.create_shelf_box(2, "Shelf 2 (Purple)", self.top_container)
        self.create_shelf_box(3, "Shelf 3 (Yellow)", self.top_container)

        # --- STATUS BOX ---
        self.create_status_box(self.bottom_container)

    def create_shelf_box(self, shelf_id, title_text, parent):
        # Frame with GREEN border
        frame = tk.Frame(parent, bg="white", highlightbackground="#4CAF50", highlightthickness=2, padx=15, pady=15)
        frame.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(frame, text=title_text, bg="white", font=self.header_font, anchor="w").pack(fill="x", pady=(0, 10))

        self.shelf_widgets[shelf_id] = {
            "count": self.add_data_row(frame, "Total count:"),
            "misplaced": self.add_data_row(frame, "Misplaced:"),
            "colors": self.add_data_row(frame, "Misplaced colors:")
        }

    def create_status_box(self, parent):
        # Frame with BLACK border
        frame = tk.Frame(parent, bg="white", highlightbackground="black", highlightthickness=2, padx=15, pady=15)
        frame.pack(fill="x")

        tk.Label(frame, text="Robot's current location:", bg="white", font=self.header_font, anchor="w").pack(fill="x")
        self.loc_label = tk.Label(frame, text="Start", bg="white", font=self.value_font, anchor="w", fg="blue")
        self.loc_label.pack(fill="x", pady=(0, 10))

        # === ADDED COORDINATE LABELS ===
        self.cur_pos_label = self.add_data_row(frame, "Current (x,y,w):")
        self.goal_pos_label = self.add_data_row(frame, "Goal (x,y,w):")
        # ===============================

        self.total_mis_label = self.add_data_row(frame, "Total Misplaced:")
        self.total_count_label = self.add_data_row(frame, "Total count:")
        self.timestamp_label = self.add_data_row(frame, "Time stamp:")

    def add_data_row(self, parent, label_text):
        container = tk.Frame(parent, bg="white")
        container.pack(fill="x", pady=2)
        tk.Label(container, text=label_text, bg="white", font=self.label_font, width=15, anchor="w").pack(side="left")
        value_label = tk.Label(container, text="-", bg="white", font=self.value_font, anchor="w")
        value_label.pack(side="left", fill="x", expand=True)
        return value_label

    # === UPDATED FUNCTION SIGNATURE ===
    def update_dashboard(self, location, shelf_data_list, timestamp, current_coords, goal_coords):
        """
        Now accepts 5 arguments + self (total 6) to match the error message requirements.
        """
        self.loc_label.config(text=location)
        self.timestamp_label.config(text=timestamp)
        
        # Update the new coordinate labels
        self.cur_pos_label.config(text=current_coords)
        self.goal_pos_label.config(text=goal_coords)

        grand_total_mis = 0
        grand_total_cnt = 0

        for data in shelf_data_list:
            sid = data['id']
            if sid in self.shelf_widgets:
                self.shelf_widgets[sid]["count"].config(text=str(data['total']))
                self.shelf_widgets[sid]["misplaced"].config(text=str(data['misplaced']))
                self.shelf_widgets[sid]["colors"].config(text=str(data['bad_colors']))
                
                grand_total_cnt += data['total']
                grand_total_mis += data['misplaced']

        self.total_count_label.config(text=str(grand_total_cnt))
        self.total_mis_label.config(text=str(grand_total_mis))