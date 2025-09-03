import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from click_logic import ClickTracker
from timer import SessionTimer


class ClickCounterGUI:
    """GUI wrapper that uses ClickTracker for core logic."""

    def __init__(self):
        self.tracker = ClickTracker()
        self.timer = SessionTimer()
        # UI state
        self.is_expanded = False
        # Resizing state
        self.resizing = False
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_w = 0
        self.resize_start_h = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.setup_gui()
        loaded = self.tracker.load_settings()
        if loaded:
            messagebox.showinfo("Loaded", "Settings loaded!")
        self.update_stats_loop()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Browser Click Counter")
        self.root.attributes("-topmost", True)
        # Allow programmatic resizing; we provide a custom grip for undecorated window
        self.root.resizable(True, True)
        self.root.overrideredirect(True)

        # Simple color scheme to keep it fast
        self.colors = {
            'bg_primary': '#1e1e2e',
            'text_success': '#a6e3a1',
            'text_secondary': '#89b4fa',
            'bg_accent': '#3b3f4f',
            'text_primary': '#cdd6f4',
            'text_error': '#f38ba8',
        }

        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], bd=1, relief='solid')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Resize grip (bottom-right)
        self.resize_grip = tk.Frame(self.main_frame, width=12, height=12, bg=self.colors['bg_accent'], cursor='size_nw_se')
        # Use place so it stays in bottom-right regardless of layout
        self.resize_grip.place(relx=1.0, rely=1.0, x=-6, y=-6, anchor='se')
        self.resize_grip.bind("<Button-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.do_resize)
        self.resize_grip.bind("<ButtonRelease-1>", self.stop_resize)

        # Title bar
        self.title_bar = tk.Frame(self.main_frame, bg=self.colors['bg_accent'], height=28)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_label = tk.Label(self.title_bar, text="Click Counter", fg=self.colors['text_primary'], bg=self.colors['bg_accent'])
        self.title_label.pack(side=tk.LEFT, padx=8)
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.drag_window)

        close_btn = tk.Button(self.title_bar, text='×', command=self.on_closing, bg=self.colors['bg_accent'], fg=self.colors['text_primary'], relief='flat')
        close_btn.pack(side=tk.RIGHT, padx=6)

        # Compact view
        self.compact_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.count_label = tk.Label(self.compact_frame, text=str(self.tracker.count), font=("Segoe UI", 24, "bold"), fg=self.colors['text_success'], bg=self.colors['bg_primary'])
        self.count_label.pack(pady=10)
        self.expand_btn = tk.Button(self.compact_frame, text='⚙ Expand', command=self.toggle_view)
        self.expand_btn.pack()
        # Allow dragging the window by the compact area (click-and-drag anywhere on compact_frame)
        self.compact_frame.bind("<Button-1>", self.start_drag)
        self.compact_frame.bind("<B1-Motion>", self.drag_window)
        # Also bind the big label so users can drag by the count text
        self.count_label.bind("<Button-1>", self.start_drag)
        self.count_label.bind("<B1-Motion>", self.drag_window)

        # Expanded view
        self.expanded_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.expanded_count_label = tk.Label(self.expanded_frame, text=f"Clicks: {self.tracker.count}", fg=self.colors['text_success'], bg=self.colors['bg_primary'])
        self.expanded_count_label.pack(anchor='w', padx=8, pady=4)

        # Personal message
        self.love_label = tk.Label(self.expanded_frame, text='I love you Ash', fg=self.colors['text_secondary'], bg=self.colors['bg_primary'], font=("Segoe UI", 10, "italic"))
        self.love_label.pack(anchor='center', pady=(0, 6))

        btn_frame = tk.Frame(self.expanded_frame, bg=self.colors['bg_primary'])
        btn_frame.pack(fill=tk.X, padx=8)
        tk.Button(btn_frame, text='Start', command=self.toggle_listening, bg=self.colors['text_success']).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Reset', command=self.reset_count, bg=self.colors['text_error']).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Draw', command=self.draw_region).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Manage', command=self.manage_regions).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Save', command=self.save_settings).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Load', command=self.load_settings).pack(side=tk.LEFT, padx=4)
        # Collapse button for returning to compact view
        tk.Button(btn_frame, text='⬇ Collapse', command=self.toggle_view).pack(side=tk.RIGHT, padx=4)

        # Timer display (expanded view)
        self.timer_label = tk.Label(self.expanded_frame, text='Session: 00:00:00', fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        self.timer_label.pack(anchor='e', padx=8, pady=(6, 0))

        # Images Per Hour (IPH) stat — derived from session timer and click count
        self.iph_label = tk.Label(self.expanded_frame, text='IPH: 0.0', fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        self.iph_label.pack(anchor='e', padx=8, pady=(2, 8))

        self.show_compact()

    # UI helpers
    def show_compact(self):
        self.expanded_frame.pack_forget()
        self.compact_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        # Respect manual resizing if the user previously resized; otherwise set default
        try:
            cur_w = self.root.winfo_width()
            cur_h = self.root.winfo_height()
            if cur_w < 140 or cur_h < 140:
                self.root.geometry('140x140+30+30')
        except Exception:
            self.root.geometry('140x140+30+30')
        self.is_expanded = False

    def show_expanded(self):
        self.compact_frame.pack_forget()
        self.expanded_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        try:
            cur_w = self.root.winfo_width()
            cur_h = self.root.winfo_height()
            if cur_w < 360 or cur_h < 240:
                self.root.geometry('360x420+30+30')
        except Exception:
            self.root.geometry('360x420+30+30')
        self.is_expanded = True

    def toggle_view(self):
        if self.is_expanded:
            self.show_compact()
        else:
            self.show_expanded()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self.drag_start_x
        y = self.root.winfo_pointery() - self.drag_start_y
        self.root.geometry(f'+{x}+{y}')

    # Action methods
    def draw_region(self):
        from region_drawer import RegionDrawer
        self.root.withdraw()
        RegionDrawer(self.on_region_drawn)

    def on_region_drawn(self, region):
        self.root.deiconify()
        if region:
            self.tracker.add_region(region)
            messagebox.showinfo('Success', f"Added region: ({region['x1']},{region['y1']}) to ({region['x2']},{region['y2']})")

    def manage_regions(self):
        from region_manager import RegionManager
        if not self.tracker.regions:
            messagebox.showinfo('No Regions', 'No regions to manage. Draw some first!')
            return
        RegionManager(self.root, self.tracker.regions, self.update_region_display)

    def update_region_display(self):
        if self.is_expanded:
            # update label in expanded view
            pass

    def toggle_listening(self):
        if not self.tracker.regions:
            messagebox.showwarning('No Regions', 'Please draw at least one click region first!')
            return
        if self.tracker.is_listening:
            self.tracker.stop_listening()
            self.update_status(False)
            # when stopping, keep the timer visible but do not reset
        else:
            self.tracker.start_listening(on_counted=self.update_count_display)
            # start session timer when tracking starts
            self.timer.start()
            self.update_status(True)

    def update_count_display(self):
        self.count_label.config(text=str(self.tracker.count))
        self.expanded_count_label.config(text=f"Clicks: {self.tracker.count}")

    def update_status(self, running: bool):
        if running:
            self.expanded_count_label.config(fg=self.colors['text_success'])
        else:
            self.expanded_count_label.config(fg=self.colors['text_error'])

    def reset_count(self):
        if messagebox.askyesno('Reset Count', 'Reset counter to 0?'):
            self.tracker.count = 0
            self.tracker.click_times = []
            self.tracker.start_time = None
            # reset timer when resetting session
            self.timer.reset()
            self.update_count_display()

    def save_settings(self):
        try:
            self.tracker.save_settings()
            messagebox.showinfo('Saved', 'Settings saved!')
        except Exception as e:
            messagebox.showerror('Error', f'Save failed: {e}')

    def load_settings(self):
        try:
            if self.tracker.load_settings():
                self.update_count_display()
                messagebox.showinfo('Loaded', 'Settings loaded!')
        except Exception as e:
            messagebox.showerror('Error', f'Load failed: {e}')

    def update_stats_loop(self):
        if self.is_expanded:
            # update rate and session
            self.expanded_count_label.config(text=f"Clicks: {self.tracker.count}")
            # update timer label
            self.timer_label.config(text=f"Session: {self.timer.format_hms()}")
            # update IPH (Images Per Hour) based on session timer and total clicks
            secs = self.timer.elapsed_seconds()
            if secs <= 0:
                iph = 0.0
            else:
                hours = secs / 3600.0
                iph = self.tracker.count / hours if hours > 0 else 0.0
            # show with one decimal place
            self.iph_label.config(text=f"IPH: {iph:.1f}")
        self.root.after(1000, self.update_stats_loop)

    # --- Resize handlers ---
    def start_resize(self, event):
        # record initial pointer and window size
        self.resizing = True
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_w = self.root.winfo_width()
        self.resize_start_h = self.root.winfo_height()

    def do_resize(self, event):
        if not self.resizing:
            return
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        new_w = max(120, int(self.resize_start_w + dx))
        new_h = max(80, int(self.resize_start_h + dy))
        # enforce larger minimums for expanded mode
        if self.is_expanded:
            new_w = max(360, new_w)
            new_h = max(240, new_h)
        self.root.geometry(f"{new_w}x{new_h}")

    def stop_resize(self, event):
        self.resizing = False

    def on_closing(self):
        self.tracker.stop_listening()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
