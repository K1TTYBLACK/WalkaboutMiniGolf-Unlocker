import string
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os


def modify_hex_section(filename, start_marker, end_marker, replacements, max_changes=99999):
    global hex_data
    try:
        file_dir, file_name = os.path.split(filename)

        modified_dir = os.path.join(file_dir, f"K1_UNLOCKED/{username}")

        os.makedirs(modified_dir, exist_ok=True)

        modified_filename = os.path.join(modified_dir, file_name)

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

        with open(modified_filename, "wb") as f:
            f.write(bytes.fromhex(hex_data))

        return changes
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return 0


def unlock_putters():
    if not file_path.get():
        messagebox.showwarning("Warning", "Please select a file first!")
        return
    if not hex_data:
        messagebox.showwarning("Warning", "Error reading save file!")
        return

    replacements_putters = {
        "56616c7565000008": "56616c7565000108",
        "48617356616c7565000009": "48617356616c7565000109"
    }

    changes = modify_hex_section(
        file_path.get(), "PuttersUnlocked", "CourseData", replacements_putters)
    status_label.config(text=f"Putters Unlocked: {changes//2}")


def unlock_balls():
    if not file_path.get():
        messagebox.showwarning("Warning", "Please select a file first!")
        return
    if not hex_data:
        messagebox.showwarning("Warning", "Error reading save file!")
        return

    replacements_balls = {
        "48 61 73 56 61 6c 75 65 00 00 09".replace(" ", ""):
        "48 61 73 56 61 6c 75 65 00 01 09".replace(" ", ""),
        "56 61 6c 75 65 00 ff ff ff ff ff ff ff ff 08".replace(" ", ""):
        "56 61 6c 75 65 00 00 00 00 00 00 00 00 00 08".replace(" ", "")
    }

    changes = modify_hex_section(
        file_path.get(), "BallsFound", "BallPositions", replacements_balls)
    status_label.config(text=f"Balls Unlocked: {changes//2}")


def get_profile_username(hex_data):
    name_hex = "4e616d65"  # "Name" in hex
    platform_hex = "506c6174666f726d446973706c61794e616d65"
    value_hex = "56616c7565"  # "Value" in hex
    has_value_hex = "48617356616c7565"  # "HasValue" in hex

    name_start_hex = "000000"
    name_end_hex = "0008"

    # Search for the hex data between "Name" and "PlatformDisplayName"
    try:
        match = re.search(f"{name_hex}(.*?){platform_hex}", hex_data)
        extracted_hex = match.group(1)  # Already in hex format
        match = re.search(f"{value_hex}(.*?){has_value_hex}", extracted_hex)
        extracted_hex = match.group(1)  # Extracted hex data
        match = re.search(
            f"{name_start_hex}(.*?){name_end_hex}", extracted_hex)
        extracted_hex = match.group(1)  # Extracted hex data
        raw_bytes = bytes.fromhex(extracted_hex)  # Convert hex back to bytes
        try:
            decoded_text = raw_bytes.decode(
                "utf-8")  # Attempt UTF-8 decoding
        except UnicodeDecodeError:
            decoded_text = raw_bytes.decode("utf-8")  # Fallback decoding

        decoded_text = "".join(
            c for c in decoded_text if c in string.printable)
        return decoded_text
    except Exception as e:
        print(e)
        return None


def select_file():
    global hex_data
    global username
    filename = filedialog.askopenfilename(
        filetypes=[("Data Files", "*.data"), ("All Files", "*.*")])
    file_path.set(filename)
    with open(filename, "rb") as f:
        hex_data = f.read().hex()

    username = get_profile_username(hex_data)

    try:
        name_label.config(text=f'Profile: "{username}"')
    except:
        pass

    file_dir, file_name = os.path.split(file_path.get())
    backup_dir = os.path.join(file_dir, f"K1_BACKUP/{username}")
    os.makedirs(backup_dir, exist_ok=True)
    backup_filename = os.path.join(backup_dir, file_name)
    if not os.path.exists(backup_filename):
        shutil.copy(filename, backup_filename)


# Create GUI window
root = tk.Tk()
root.title("WMG: Balls & Putters Unlocker by K1TTYBLACK")
root.geometry("600x250")

file_path = tk.StringVar()
hex_data = None
username = None
# File selection
tk.Label(root, text="Select File:").pack(pady=5)
tk.Entry(root, textvariable=file_path, width=40, state="readonly").pack()
tk.Button(root, text="Browse", command=select_file).pack(pady=5)

# Buttons for unlocking
name_label = tk.Label(root, text="PROFILE NAME WILL BE HERE")
name_label.pack(pady=10)

tk.Button(root, text="Unlock Putters", command=unlock_putters,
          fg="black").pack(pady=5)
tk.Button(root, text="Unlock Balls", command=unlock_balls,
          fg="black").pack(pady=5)

# Status label
status_label = tk.Label(root, text="Awaiting action...", fg="gray")
status_label.pack(pady=10)

# Run the GUI
root.mainloop()
