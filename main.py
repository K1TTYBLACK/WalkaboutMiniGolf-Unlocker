import tkinter as tk
from tkinter import ttk
import string
import re
from tkinter import filedialog, messagebox
import shutil
import os
import webbrowser


class App(ttk.Frame):
    """
    Azure ttk theme provided by:
    Author: rdbende
    Source: https://github.com/rdbende/ttk-widget-factory

    WMG: Balls & Putters unlocker provided by:
    Author: K1TTYBLACK
    Source: https://github.com/K1TTYBLACK/WalkaboutMiniGolf-Unlocker
    """

    def __init__(self, parent):
        super().__init__()
        self.unlock_balls = tk.BooleanVar(value=True)
        self.unlock_putters = tk.BooleanVar(value=True)
        self.username = None
        self.hex_data = None
        self.file_name = tk.StringVar()
        self.file_dir = None

        self.setup_widgets()

    def open_github(self):
        webbrowser.open(
            "https://github.com/K1TTYBLACK/WalkaboutMiniGolf-Unlocker")

    def open_meta(self):
        webbrowser.open("https://horizon.meta.com/profile/112795680903761/")

    def modify_hex_section(self, start_marker, end_marker, replacements, max_changes=99999):
        try:
            file_dir, file_name = self.file_dir, self.file_name.get()
            modified_dir = os.path.join(
                file_dir, f"K1_UNLOCKED/{self.username}")
            os.makedirs(modified_dir, exist_ok=True)
            modified_filename = os.path.join(modified_dir, file_name)
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
                    limit = min(occurrences, max_changes - changes)
                    extracted_hex = extracted_hex.replace(old, new, limit)
                    changes += limit
                    if changes >= max_changes:
                        break
            self.hex_data = self.hex_data[:start_pos] + \
                extracted_hex + self.hex_data[end_pos:]
            with open(modified_filename, "wb") as f:
                f.write(bytes.fromhex(self.hex_data))
            return changes
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return 0

    def unlock(self):
        if not self.file_dir:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        if not self.hex_data:
            messagebox.showwarning("Warning", "Error reading save file!")
            return
        ball_changes = 0
        if self.unlock_putters.get():
            replacements_putters = {
                "56616c7565000008": "56616c7565000108",
                "48617356616c7565000009": "48617356616c7565000109"
            }
            ball_changes += self.modify_hex_section(
                "PuttersUnlocked", "CourseData", replacements_putters)
        putter_changes = 0
        if self.unlock_balls.get():
            replacements_balls = {
                "48617356616c7565000009": "48617356616c7565000109",
                "56616c756500ffffffffffffffff08": "56616c75650000000000000000000008"
            }
            putter_changes += self.modify_hex_section(
                "BallsFound", "BallPositions", replacements_balls)
        messagebox.showinfo(
            "Success", f"Balls added: {ball_changes//2}, Putters added: {putter_changes//2}\n\nFile saved to:\n{os.path.join(self.file_dir, f'K1_UNLOCKED/{self.username}')}")

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
            decoded_text = raw_bytes.decode("utf-8", errors="ignore")
            return "".join(c for c in decoded_text if c in string.printable)
        except:
            return None

    def select_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Data Files", "*.data"), ("All Files", "*.*")])
        if not filename:
            return

        with open(filename, "rb") as f:
            self.hex_data = f.read().hex()
        self.username = self.get_profile_username()

        self.profile_name.config(
            text=f'{self.username}' if self.username else "UNKNOWN")
        self.profile_name.config(style="Accent.TButton")
        self.browse_button.config(style="TButton")
        self.unlock_balls_check.state(["!disabled"])
        self.unlock_balls_check.config(cursor="hand2")
        self.unlock_putters_check.state(["!disabled"])
        self.unlock_putters_check.config(cursor="hand2")
        self.proceed_unlock.config(style="Accent.TButton", cursor="hand2")
        self.proceed_unlock.state(["!disabled"])

        file_dir, file_name = os.path.split(filename)
        self.file_name.set(file_name)
        self.file_dir = file_dir
        backup_dir = os.path.join(file_dir, f"K1_BACKUP/{self.username}")
        os.makedirs(backup_dir, exist_ok=True)
        backup_filename = os.path.join(backup_dir, file_name)
        if not os.path.exists(backup_filename):
            shutil.copy(filename, backup_filename)

    def setup_widgets(self):
        ttk.Label(self, text="Walkabout Mini Golf\nBALLS & PUTTERS UNLOCKER", justify="center", font=(
            "", 13, "bold")).grid(row=0, column=0, pady=10, columnspan=2)

        frame = ttk.Frame(self, padding=(10, 0, 0, 25))
        frame.grid(row=1, column=0, sticky="nsew")

        # Center the frame
        frame.columnconfigure((0), weight=1)

        # Inner frame to group elements closely
        inner_frame = ttk.Frame(frame)
        inner_frame.grid(row=0, column=0)

        ttk.Label(inner_frame, text="by K1TTYBLACK", state=["disabled", "!alternate"]).grid(
            row=0, column=0, padx=5, pady=(0, 10))
        ttk.Button(inner_frame, text="GitHub", command=self.open_github, cursor="hand2").grid(
            row=0, column=1, padx=5, pady=(0, 10))
        ttk.Button(inner_frame, text="Meta", command=self.open_meta, cursor="hand2").grid(
            row=0, column=2, padx=5, pady=(0, 10))

        # ttk.Separator(self).grid(row=2, column=0,
        #                          padx=20, pady=10, sticky="ew")

        profile_frame = ttk.LabelFrame(
            self, text="1. Profile", padding=(20, 10))
        profile_frame.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")
        ttk.Label(profile_frame, text='''Select "Profile_Default.data" or "Profile_XXXXXX.data"''', state=["disabled", "!alternate"]).grid(
            row=0, column=0, columnspan=2, padx=5, pady=(0, 10))

        file_name = ttk.Entry(profile_frame, textvariable=self.file_name)
        file_name.state(["disabled"])
        file_name.grid(row=1, column=0,
                       padx=5, pady=(0, 10), sticky="nsew")

        self.browse_button = ttk.Button(
            profile_frame, text="Browse...", command=self.select_file, cursor="hand2", style="Accent.TButton")
        self.browse_button.grid(row=1, column=1, padx=5,
                                pady=(0, 10), sticky="nsew")

        self.profile_name = ttk.Button(
            profile_frame, text="YOUR NAME WILL BE HERE")
        self.profile_name.state(["disabled"])
        self.profile_name.grid(
            row=2, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="nsew")

        ttk.Separator(self).grid(row=4, column=0,
                                 padx=20, pady=10, sticky="ew")

        unlocking_frame = ttk.LabelFrame(
            self, text="2. Unlocker", padding=(20, 10))
        unlocking_frame.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")

        self.unlock_balls_check = ttk.Checkbutton(
            unlocking_frame, text="Unlock balls", variable=self.unlock_balls, cursor="X_cursor", command=self.update_button_state
        )
        self.unlock_balls_check.grid(
            row=0, column=0, padx=5, pady=10, sticky="w")
        self.unlock_balls_check.state(["disabled"])
        self.unlock_putters_check = ttk.Checkbutton(
            unlocking_frame, text="Unlock putters", variable=self.unlock_putters, cursor="X_cursor", command=self.update_button_state
        )
        self.unlock_putters_check.grid(
            row=1, column=0, padx=5, pady=10, sticky="w")
        self.unlock_putters_check.state(["disabled"])
        self.proceed_unlock = ttk.Button(
            unlocking_frame, text="UNLOCK", command=self.unlock, cursor="X_cursor"
        )
        self.proceed_unlock.state(["disabled"])
        self.proceed_unlock.grid(row=0, column=2, rowspan=2,
                                 padx=10, pady=10, sticky="nsew")

        # Ensure the layout expands properly
        unlocking_frame.columnconfigure(2, weight=1)

    def update_button_state(self):
        """Enable UNLOCK button if at least one checkbox is checked."""
        if self.unlock_balls.get() or self.unlock_putters.get():
            self.proceed_unlock.state(["!disabled"])
            self.proceed_unlock.config(style="Accent.TButton")
        else:
            self.proceed_unlock.state(["disabled"])
            self.proceed_unlock.config(style="TButton")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("WMG Unlocker by K1TTYBLACK")
    root.resizable(False, False)
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    root.update()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2 - 20
    root.geometry(f"+{x}+{y}")
    root.mainloop()
