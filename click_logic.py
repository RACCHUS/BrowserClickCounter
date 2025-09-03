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
        self.is_paused = False
        self.last_region = None  # Store the most recently used region

    # --- Persistence ---
    def save_settings(self, path='click_counter_settings.json'):
        """Save regions and app settings (not session data)."""
        settings = {
            'regions': self.regions,
            'last_region': self.last_region,
            'browser_detection': self.browser_detection,
            'timestamp': datetime.now().isoformat()
        }
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)

    def load_settings(self, path='click_counter_settings.json'):
        """Load regions and app settings."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                settings = json.load(f)
            self.regions = settings.get('regions', [])
            self.last_region = settings.get('last_region', None)
            self.browser_detection = settings.get('browser_detection', True)
            
            # If we have a last_region but no regions, restore the last region
            if self.last_region and not self.regions:
                self.regions = [self.last_region]
            
            return True
        return False

    def save_session(self, session_duration_seconds, path='last_session.json'):
        """Save current session data automatically."""
        if self.count == 0 and session_duration_seconds == 0:
            return  # Don't save empty sessions
        
        # Calculate IPH
        hours = session_duration_seconds / 3600.0 if session_duration_seconds > 0 else 0
        iph = self.count / hours if hours > 0 else 0.0
        
        session_data = {
            'clicks': self.count,
            'duration_seconds': session_duration_seconds,
            'duration_formatted': self._format_duration(session_duration_seconds),
            'iph': round(iph, 1),
            'completed_at': datetime.now().isoformat(),
            'regions_used': len(self.regions)
        }
        
        with open(path, 'w') as f:
            json.dump(session_data, f, indent=2)

    def load_last_session(self, path='last_session.json'):
        """Load the last completed session data."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def _format_duration(self, seconds):
        """Format duration as HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    # --- Region management ---
    def add_region(self, region):
        if region:
            self.regions.append(region)
            self.last_region = region  # Update last used region

    def clear_regions(self):
        self.regions.clear()

    def reset_session(self):
        """Reset current session data (for new session)."""
        self.count = 0
        self.click_times = []
        self.start_time = None

    def get_region_status(self):
        """Get a user-friendly status of current regions."""
        if not self.regions:
            return "No regions set"
        elif len(self.regions) == 1:
            region = self.regions[0]
            width = region['x2'] - region['x1']
            height = region['y2'] - region['y1']
            return f"Region: {width}×{height} at ({region['x1']},{region['y1']})"
        else:
            return f"{len(self.regions)} regions set"

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
                
                # Check for milestone achievements
                milestone = self._check_milestone(self.count)
                return True, milestone
        return False, None

    def _check_milestone(self, count):
        """Check if the current count represents a milestone achievement."""
        if count % 1000 == 0 and count > 0:
            return "major"  # 1000, 2000, 3000...
        elif count % 100 == 0 and count > 0:
            return "minor"  # 100, 200, 300... (excluding 1000s)
        return None

    def handle_click(self, x, y, button, pressed, on_counted=None):
        """Call from a mouse listener. If a click is counted, optionally call on_counted()."""
        if pressed and button == mouse.Button.left:
            # Don't count clicks if paused
            if self.is_paused:
                return
            if not self._is_browser_window(x, y):
                return
            counted, milestone = self._count_if_in_regions(x, y)
            if counted and on_counted:
                try:
                    on_counted(milestone)
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
        self.is_paused = False  # Ensure we're not paused when starting
        if self.start_time is None:
            self.start_time = datetime.now()

    def pause_listening(self):
        """Pause click counting without stopping the listener or timer."""
        if self.is_listening:
            self.is_paused = True

    def resume_listening(self):
        """Resume click counting."""
        if self.is_listening:
            self.is_paused = False

    def stop_listening(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.is_listening = False
        self.is_paused = False

    # --- Stats helpers ---
    def clicks_last_hour(self):
        now = datetime.now()
        return len([t for t in self.click_times if t > now - timedelta(hours=1)])

    def session_seconds(self):
        if not self.start_time:
            return 0
        return int((datetime.now() - self.start_time).total_seconds())
