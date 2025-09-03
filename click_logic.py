import json
import os
from datetime import datetime, timedelta
import psutil
import win32gui
import win32process
from pynput import mouse

class ClickTracker:
    """Core non-UI logic for counting clicks and managing regions/settings."""
    def __init__(self):
        self.count = 0
        self.regions = []
        self.click_times = []
        self.start_time = None
        self.browser_detection = True
        self.listener = None
        self.is_listening = False

    # --- Persistence ---
    def save_settings(self, path='click_counter_settings.json'):
        settings = {
            'count': self.count,
            'regions': self.regions,
            'browser_detection': self.browser_detection,
            'timestamp': datetime.now().isoformat()
        }
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_settings(self, path='click_counter_settings.json'):
        if os.path.exists(path):
            with open(path, 'r') as f:
                settings = json.load(f)
            self.count = settings.get('count', 0)
            self.regions = settings.get('regions', [])
            self.browser_detection = settings.get('browser_detection', True)
            return True
        return False

    # --- Region management ---
    def add_region(self, region):
        if region:
            self.regions.append(region)

    def clear_regions(self):
        self.regions.clear()

    # --- Counting logic ---
    def _is_browser_window(self, x, y):
        if not self.browser_detection:
            return True
        try:
            hwnd = win32gui.WindowFromPoint((x, y))
            if hwnd == 0:
                return False
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(process_id)
                process_name = process.name().lower()
                return any(browser in process_name for browser in ['chrome.exe', 'msedge.exe', 'edge.exe'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False
        except Exception:
            return False

    def _count_if_in_regions(self, x, y):
        for region in self.regions:
            if (region['x1'] <= x <= region['x2'] and region['y1'] <= y <= region['y2']):
                self.count += 1
                now = datetime.now()
                self.click_times.append(now)
                cutoff = now - timedelta(hours=1)
                self.click_times = [t for t in self.click_times if t > cutoff]
                return True
        return False

    def handle_click(self, x, y, button, pressed, on_counted=None):
        """Call from a mouse listener. If a click is counted, optionally call on_counted()."""
        if pressed and button == mouse.Button.left:
            if not self._is_browser_window(x, y):
                return
            counted = self._count_if_in_regions(x, y)
            if counted and on_counted:
                try:
                    on_counted()
                except Exception:
                    pass

    # --- Listener control ---
    def start_listening(self, on_counted=None):
        if self.is_listening:
            return
        # Bind the internal handler which will call on_counted when appropriate
        def listener_cb(x, y, button, pressed):
            self.handle_click(x, y, button, pressed, on_counted=on_counted)
        self.listener = mouse.Listener(on_click=listener_cb)
        self.listener.start()
        self.is_listening = True
        if self.start_time is None:
            self.start_time = datetime.now()

    def stop_listening(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.is_listening = False

    # --- Stats helpers ---
    def clicks_last_hour(self):
        now = datetime.now()
        return len([t for t in self.click_times if t > now - timedelta(hours=1)])

    def session_seconds(self):
        if not self.start_time:
            return 0
        return int((datetime.now() - self.start_time).total_seconds())
