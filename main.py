import sv_ttk
from tkinter import ttk
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


def unlock():
    if not file_path.get():
        messagebox.showwarning("Warning", "Please select a file first!")
        return
    if not hex_data:
        messagebox.showwarning("Warning", "Error reading save file!")
        return
    ball_changes = 0
    if putters_var.get():
        replacements_putters = {
            "56616c7565000008": "56616c7565000108",
            "48617356616c7565000009": "48617356616c7565000109"
        }
        ball_changes += modify_hex_section(file_path.get(),

                                           "PuttersUnlocked", "CourseData", replacements_putters)
    putter_changes = 0
    if balls_var.get():
        replacements_balls = {
            "48617356616c7565000009": "48617356616c7565000109",
            "56616c756500ffffffffffffffff08": "56616c75650000000000000000000008"
        }
        putter_changes += modify_hex_section(file_path.get(),
                                             "BallsFound", "BallPositions", replacements_balls)
    status_label.config(
        text=f"Balls added: {ball_changes//2}, Putters added: {putter_changes//2}")


def get_profile_username(hex_data):
    try:
        match = re.search(
            "4e616d65(.*?)506c6174666f726d446973706c61794e616d65", hex_data)
        extracted_hex = match.group(1)
        match = re.search("56616c7565(.*?)48617356616c7565", extracted_hex)
        extracted_hex = match.group(1)
        match = re.search("000000(.*?)0008", extracted_hex)
        extracted_hex = match.group(1)
        raw_bytes = bytes.fromhex(extracted_hex)
        decoded_text = raw_bytes.decode("utf-8", errors="ignore")
        return "".join(c for c in decoded_text if c in string.printable)
    except:
        return None


def select_file():
    global hex_data, username
    filename = filedialog.askopenfilename(
        filetypes=[("Data Files", "*.data"), ("All Files", "*.*")])
    if not filename:
        return
    file_path.set(os.path.basename(filename))
    with open(filename, "rb") as f:
        hex_data = f.read().hex()
    username = get_profile_username(hex_data)
    name_label.config(
        text=f'Profile: "{username}"' if username else "Profile: Unknown")
    status_label.config(
        text=f"Profile loaded. Select what to unlock and press 'Unlock'.")
    file_dir, file_name = os.path.split(filename)
    backup_dir = os.path.join(file_dir, f"K1_BACKUP/{username}")
    os.makedirs(backup_dir, exist_ok=True)
    backup_filename = os.path.join(backup_dir, file_name)
    if not os.path.exists(backup_filename):
        shutil.copy(filename, backup_filename)


root = tk.Tk()
root.title("WMG: Balls & Putters Unlocker by K1TTYBLACK")
root.geometry("600x260")
root.resizable(False, False)
sv_ttk.set_theme("light", root)
style = ttk.Style()
style.configure("TFrame", background="#303030")  # змінюємо фон

frame = ttk.Frame(root, width=0, height=0, style="TFrame")
frame.pack(fill="both", expand=True)


file_path = tk.StringVar()
hex_data = None
username = None
frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)
ttk.Label(frame, text="Select File:").grid(row=0, column=0, pady=5, sticky="w")
entry = ttk.Entry(frame, textvariable=file_path, width=40, state="readonly")
entry.grid(row=0, column=1, padx=5)
ttk.Button(frame, text="Browse", command=select_file).grid(
    row=0, column=2, pady=5)
name_label = ttk.Label(frame, text="Profile name: UNKNOWN",
                       font=("Arial", 12, "bold"), anchor="w")
name_label.grid(row=1, column=0, columnspan=3, pady=10, sticky="w")
status_label = ttk.Label(frame, text="Awaiting action...",
                         foreground="gray", anchor="w")
status_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="w")
putters_var = tk.BooleanVar()
balls_var = tk.BooleanVar()
ttk.Checkbutton(frame, text="Unlock Putters", variable=putters_var).grid(
    row=3, column=0, columnspan=3, pady=5, sticky="w")
ttk.Checkbutton(frame, text="Unlock Balls", variable=balls_var).grid(
    row=4, column=0, columnspan=3, pady=5, sticky="w")

unlock_button = ttk.Button(
    frame, text="Unlock", command=unlock, style="secondary.TButton")
unlock_button.grid(row=5, column=0, columnspan=1,
                   pady=10, padx=5)  # Reduced width


root.mainloop()
