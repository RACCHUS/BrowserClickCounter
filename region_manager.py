import tkinter as tk
from tkinter import messagebox

class RegionManager:
    def __init__(self, parent, regions, update_callback):
        self.regions = regions
        self.update_callback = update_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Manage Regions")
        self.window.geometry("380x280")
        self.window.attributes("-topmost", True)
        self.window.grab_set()
        self.window.configure(bg='#1e1e2e')

        # Region list with modern styling
        list_frame = tk.Frame(self.window, bg='#1e1e2e')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Scrollable listbox with modern colors
        scrollbar = tk.Scrollbar(list_frame, bg='#2a2d3a', troughcolor='#1e1e2e')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                 bg='#2a2d3a', fg='#cdd6f4', selectbackground='#89b4fa',
                                 selectforeground='#1e1e2e', font=("Segoe UI", 9),
                                 relief="flat", bd=1, highlightthickness=0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Buttons with modern styling
        btn_frame = tk.Frame(self.window, bg='#1e1e2e')
        btn_frame.pack(fill=tk.X, padx=15, pady=10)

        remove_btn = tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected,
                              bg='#f38ba8', fg='#1e1e2e', font=("Segoe UI", 9, "bold"),
                              relief="flat", bd=0, padx=12, pady=6,
                              activebackground='#2a2d3a')
        remove_btn.pack(side=tk.LEFT, padx=3)

        clear_btn = tk.Button(btn_frame, text="Clear All", command=self.clear_all,
                             bg='#f38ba8', fg='#1e1e2e', font=("Segoe UI", 9, "bold"),
                             relief="flat", bd=0, padx=12, pady=6,
                             activebackground='#2a2d3a')
        clear_btn.pack(side=tk.LEFT, padx=3)

        done_btn = tk.Button(btn_frame, text="Done", command=self.window.destroy,
                            bg='#a6e3a1', fg='#1e1e2e', font=("Segoe UI", 9, "bold"),
                            relief="flat", bd=0, padx=12, pady=6,
                            activebackground='#2a2d3a')
        done_btn.pack(side=tk.RIGHT, padx=3)

        self.update_list()

    def update_list(self):
        self.listbox.delete(0, tk.END)
        for i, region in enumerate(self.regions):
            width = region['x2'] - region['x1']
            height = region['y2'] - region['y1']
            text = f"Region {i+1}: ({region['x1']},{region['y1']}) {width}×{height}"
            self.listbox.insert(tk.END, text)

    def remove_selected(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.regions.pop(index)
            self.update_list()
            self.update_callback()

    def clear_all(self):
        if messagebox.askyesno("Clear All", "Remove all regions?"):
            self.regions.clear()
            self.update_list()
            self.update_callback()
