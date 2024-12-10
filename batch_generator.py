import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Initialize database
conn = sqlite3.connect("batch_data.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_number TEXT,
    product_type TEXT,
    color TEXT,
    mrp TEXT,
    mfd_date TEXT,
    date_generated TEXT
)
""")
conn.commit()

# Global countdown variable
undo_countdown = 10

# Batch number generator
def generate_batch_number():
    global undo_countdown
    year = datetime.now().year % 100  # Last two digits of the year
    product_type = type_var.get()
    color = color_var.get()
    mrp = datetime.now().strftime("%Y-%m-%d")  # Default today's date
    mfd_date = datetime.now().strftime("%Y-%m-%d")  # Today's date as MFD

    if not product_type or not color:
        messagebox.showerror("Input Error", "Please fill all fields.")
        return

    # Assign type code
    type_code = "1" if product_type.lower() == "polymer" else "2"

    # Get color code (position in the color list + 1)
    color_code = str(color_list.index(color) + 1).zfill(2)

    # Get the last sequence number
    cursor.execute("""
        SELECT MAX(batch_number) FROM batches
        WHERE batch_number LIKE ?
    """, (f"{year}{type_code}{color_code}%",))
    last_batch = cursor.fetchone()[0]

    # Increment the sequence number
    if last_batch:
        sequence_number = int(last_batch[-3:]) + 1
    else:
        sequence_number = 1

    batch_number = f"{year}{type_code}{color_code}{str(sequence_number).zfill(3)}"

    # Save to database
    cursor.execute("""
        INSERT INTO batches (batch_number, product_type, color, mrp, mfd_date, date_generated)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (batch_number, product_type, color, mrp, mfd_date, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    # Display the batch number and MFD
    result_label.config(text=f"Product: {color}\nMRP: {mrp}\nBatch Number: {batch_number}\nMFD: {mfd_date}")

    # Reset and start undo timer
    undo_countdown = 10
    undo_button.config(state="normal", text=f"Undo Last ({undo_countdown}s)")
    update_undo_timer()

# Undo the last batch number generation
def undo_last():
    global undo_countdown
    cursor.execute("SELECT id FROM batches ORDER BY id DESC LIMIT 1")
    last_batch = cursor.fetchone()
    if not last_batch:
        messagebox.showinfo("Undo", "No batch numbers to undo.")
        return

    cursor.execute("DELETE FROM batches WHERE id = ?", (last_batch[0],))
    conn.commit()
    result_label.config(text="Undo successful. No batch details to display.")
    undo_button.config(state="disabled")  # Disable the button after undo
    undo_countdown = 0  # Stop the timer

# Timer for the undo button
def update_undo_timer():
    global undo_countdown
    if undo_countdown > 0:
        undo_countdown -= 1
        undo_button.config(text=f"Undo Last ({undo_countdown}s)")
        undo_button.after(1000, update_undo_timer)  # Update every second
    else:
        undo_button.config(state="disabled", text="Undo Last")

# GUI Application
app = tk.Tk()
app.title("Batch Number Generator")
app.geometry("250x220")  # Compact window size

# Set application icon
app.iconbitmap("app_icon.ico")  # Ensure you have an 'app_icon.ico' file in the same directory

# Color list
color_list = [
    "White", "Bone", "Ivory", "Cream", "Off White", "Light Blue", "Blue", "Dark Blue",
    "Cobalt Blue", "Terracotta", "Peach", "Light Beige", "Beige", "Gold", "Sand Stone",
    "Light Green", "Green", "Dark Green", "Goma Green", "Sahara Sand", "Silver Gray",
    "Creamish Gray", "Gray", "Dark Gray", "Black", "Light Pink", "Pink", "Light Brown",
    "Brown", "Burgundy"
]

# Widgets
tk.Label(app, text="Product Type").grid(row=0, column=0, padx=5, pady=5, sticky="w")
type_var = tk.StringVar()
ttk.Combobox(app, textvariable=type_var, values=["Polymer", "Normal"], width=20).grid(row=0, column=1, padx=5, pady=5)

tk.Label(app, text="Color").grid(row=1, column=0, padx=5, pady=5, sticky="w")
color_var = tk.StringVar()
ttk.Combobox(app, textvariable=color_var, values=color_list, width=20).grid(row=1, column=1, padx=5, pady=5)

# Buttons in a single row
button_frame = tk.Frame(app)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(button_frame, text="Generate Batch", command=generate_batch_number, width=15).pack(side="left", padx=5)
undo_button = tk.Button(button_frame, text="Undo Last", command=undo_last, width=15, state="disabled")
undo_button.pack(side="left", padx=5)

# Result label
result_label = tk.Label(app, text="", fg="blue", justify="left", anchor="w")
result_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Run the application
app.mainloop()
