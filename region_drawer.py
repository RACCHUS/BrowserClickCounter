import tkinter as tk

class RegionDrawer:
    def __init__(self, callback):
        self.callback = callback
        self.start_x = self.start_y = 0
        self.rect_id = None

        # Create fullscreen transparent overlay with modern styling
        self.overlay = tk.Tk()
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(bg='#1e1e2e')

        # Create canvas for drawing
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='#1e1e2e')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Instructions with modern styling
        instruction = tk.Label(self.canvas,
                             text="Click and drag to draw a rectangle around your button\nPress ESC to cancel",
                             font=("Segoe UI", 16, "bold"), bg="#cdd6f4", fg="#1e1e2e",
                             relief="solid", bd=2, padx=20, pady=10)
        self.canvas.create_window(self.overlay.winfo_screenwidth()//2, 60,
                                window=instruction, anchor="n")        # Bind events
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw_rect)
        self.canvas.bind('<ButtonRelease-1>', self.end_draw)
        self.overlay.bind('<Escape>', self.cancel)

        self.overlay.focus_set()  # Ensure window has focus for key events

    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def draw_rect(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='#89b4fa', width=3, fill='', dash=(8, 4))

    def end_draw(self, event):
        # Calculate region coordinates
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)

        # Minimum size check
        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
            self.cancel()
            return

        region = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
        self.overlay.destroy()
        self.callback(region)

    def cancel(self, event=None):
        self.overlay.destroy()
        self.callback(None)
