import ctypes
import sys

# Enable DPI awareness before any GUI code runs
# This ensures mouse coordinates match screen coordinates on high-DPI displays
try:
    # Try Windows 10+ per-monitor DPI awareness
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        # Fallback to system DPI awareness
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from src.gui import ClickCounterGUI

if __name__ == '__main__':
    try:
        app = ClickCounterGUI()
        app.run()
    except Exception as e:
        print(f'Error: {e}')
        input('Press Enter to exit...')  # Keep console open on error
