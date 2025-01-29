import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os


def modify_hex_section(filename, start_marker, end_marker, replacements, max_changes=99999):
    try:
        backup_filename = filename + ".K1-BACKUP"
        if not os.path.exists(backup_filename):
            # If it doesn't exist, make a copy
            shutil.copy(filename, backup_filename)

        with open(filename, "rb") as f:
            hex_data = f.read().hex()

        start_pos = hex_data.find(start_marker.encode().hex())
        end_pos = hex_data.find(end_marker.encode().hex())

        if start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
            messagebox.showwarning(
                "Error", f"Markers '{start_marker}' - '{end_marker}' not found!")
            return 0

        extracted_hex = hex_data[start_pos:end_pos]
        changes = 0

        for old, new in replacements.items():
            occurrences = extracted_hex.count(old)
            if occurrences > 0:
                limit = min(occurrences, max_changes - changes)
                extracted_hex = extracted_hex.replace(old, new, limit)
                changes += limit
                if changes >= max_changes:
                    break

        hex_data = hex_data[:start_pos] + extracted_hex + hex_data[end_pos:]

        with open(filename, "wb") as f:
            f.write(bytes.fromhex(hex_data))

        return changes
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return 0


def unlock_putters():
    if not file_path.get():
        messagebox.showwarning("Warning", "Please select a file first!")
        return

    replacements_putters = {
        "56616c7565000008": "56616c7565000108",
        "48617356616c7565000009": "48617356616c7565000109"
    }

    changes = modify_hex_section(
        file_path.get(), "PuttersUnlocked", "CourseData", replacements_putters)
    status_label.config(text=f"Putters Unlocked! Changes made: {changes}")


def unlock_balls():
    if not file_path.get():
        messagebox.showwarning("Warning", "Please select a file first!")
        return

    replacements_balls = {
        "48 61 73 56 61 6c 75 65 00 00 09".replace(" ", ""):
        "48 61 73 56 61 6c 75 65 00 01 09".replace(" ", ""),
        "56 61 6c 75 65 00 ff ff ff ff ff ff ff ff 08".replace(" ", ""):
        "56 61 6c 75 65 00 00 00 00 00 00 00 00 00 08".replace(" ", "")
    }

    changes = modify_hex_section(
        file_path.get(), "BallsFound", "BallPositions", replacements_balls)
    status_label.config(text=f"Balls Unlocked! Changes made: {changes}")


def select_file():
    filename = filedialog.askopenfilename(
        filetypes=[("Data Files", "*.data"), ("All Files", "*.*")])
    file_path.set(filename)


# Create GUI window
root = tk.Tk()
root.title("WMG: Balls & Putters Unlocker by K1TTYBLACK")
root.geometry("600x250")

file_path = tk.StringVar()

# File selection
tk.Label(root, text="Select File:").pack(pady=5)
tk.Entry(root, textvariable=file_path, width=40, state="readonly").pack()
tk.Button(root, text="Browse", command=select_file).pack(pady=5)

# Buttons for unlocking
tk.Button(root, text="Unlock Putters", command=unlock_putters,
          fg="black").pack(pady=5)
tk.Button(root, text="Unlock Balls", command=unlock_balls,
          fg="black").pack(pady=5)

# Status label
status_label = tk.Label(root, text="Awaiting action...", fg="gray")
status_label.pack(pady=10)

# Run the GUI
root.mainloop()
