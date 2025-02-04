import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sv_ttk
import string
import re
import shutil
import os


class WMGUnlocker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.file_path = tk.StringVar()
        self.hex_data = None
        self.username = None
        self.balls_var = tk.BooleanVar()
        self.putters_var = tk.BooleanVar()
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="Select File:").grid(
            row=0, column=0, pady=5, sticky="w")
        ttk.Entry(self, textvariable=self.file_path, width=40,
                  state="readonly").grid(row=0, column=1, padx=5)
        ttk.Button(self, text="Browse", command=self.select_file).grid(
            row=0, column=2, pady=5)

        self.name_label = ttk.Label(
            self, text="Profile name: UNKNOWN", font=("Arial", 12, "bold"), anchor="w")
        self.name_label.grid(
            row=1, column=0, columnspan=3, pady=10, sticky="w")

        self.status_label = ttk.Label(
            self, text="Awaiting action...", foreground="gray", anchor="w")
        self.status_label.grid(
            row=2, column=0, columnspan=3, pady=10, sticky="w")

        ttk.Checkbutton(self, text="Unlock Putters", variable=self.putters_var).grid(
            row=3, column=0, columnspan=3, pady=5, sticky="w")
        ttk.Checkbutton(self, text="Unlock Balls", variable=self.balls_var).grid(
            row=4, column=0, columnspan=3, pady=5, sticky="w")

        ttk.Button(self, text="Unlock", command=self.unlock,
                   style="secondary.TButton").grid(row=5, column=0, pady=10, padx=5)

    def select_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Data Files", "*.data"), ("All Files", "*.*")])
        if not filename:
            return

        self.file_path.set(os.path.basename(filename))
        with open(filename, "rb") as f:
            self.hex_data = f.read().hex()

        self.username = self.get_profile_username()
        self.name_label.config(
            text=f'Profile: "{self.username}"' if self.username else "Profile: Unknown")
        self.status_label.config(
            text="Profile loaded. Select what to unlock and press 'Unlock'.")

        backup_dir = os.path.join(os.path.dirname(
            filename), f"K1_BACKUP/{self.username}")
        os.makedirs(backup_dir, exist_ok=True)
        backup_filename = os.path.join(backup_dir, os.path.basename(filename))
        if not os.path.exists(backup_filename):
            shutil.copy(filename, backup_filename)

    def get_profile_username(self):
        try:
            match = re.search(
                "4e616d65(.*?)506c6174666f726d446973706c61794e616d65", self.hex_data)
            extracted_hex = match.group(1)
            match = re.search("56616c7565(.*?)48617356616c7565", extracted_hex)
            extracted_hex = match.group(1)
            match = re.search("000000(.*?)0008", extracted_hex)
            extracted_hex = match.group(1)
            raw_bytes = bytes.fromhex(extracted_hex)
            return "".join(c for c in raw_bytes.decode("utf-8", errors="ignore") if c in string.printable)
        except:
            return None

    def modify_hex_section(self, start_marker, end_marker, replacements):
        try:
            start_pos = self.hex_data.find(start_marker.encode().hex())
            end_pos = self.hex_data.find(end_marker.encode().hex())
            if start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
                messagebox.showwarning(
                    "Error", f"Markers '{start_marker}' - '{end_marker}' not found!")
                return 0
            extracted_hex = self.hex_data[start_pos:end_pos]

            changes = 0
            for old, new in replacements.items():
                occurrences = extracted_hex.count(old)
                if occurrences > 0:
                    extracted_hex = extracted_hex.replace(
                        old, new, occurrences)
                    changes += occurrences

            self.hex_data = self.hex_data[:start_pos] + \
                extracted_hex + self.hex_data[end_pos:]
            return changes
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return 0

    def unlock(self):
        if not self.file_path.get():
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        if not self.hex_data:
            messagebox.showwarning("Warning", "Error reading save file!")
            return

        ball_changes = 0
        if self.putters_var.get():
            replacements_putters = {
                "56616c7565000008": "56616c7565000108",
                "48617356616c7565000009": "48617356616c7565000109"
            }
            ball_changes += self.modify_hex_section(
                "PuttersUnlocked", "CourseData", replacements_putters)

        putter_changes = 0
        if self.balls_var.get():
            replacements_balls = {
                "48617356616c7565000009": "48617356616c7565000109",
                "56616c756500ffffffffffffffff08": "56616c75650000000000000000000008"
            }
            putter_changes += self.modify_hex_section(
                "BallsFound", "BallPositions", replacements_balls)

        self.status_label.config(
            text=f"Balls added: {ball_changes//2}, Putters added: {putter_changes//2}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("WMG Unlocker by K1TTYBLACK")
    root.geometry("600x260")
    root.resizable(False, False)
    sv_ttk.set_theme("light")

    app = WMGUnlocker(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
