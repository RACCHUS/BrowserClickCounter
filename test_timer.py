#!/usr/bin/env python3
"""
Test script for the timer integration.
This tests the timer functionality without the full click counter app.
"""

import tkinter as tk
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from timer_gui import TimerWidget


class TimerTestApp:
    """Simple test application for timer widget."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Timer Widget Test")
        self.root.geometry("400x500")
        self.root.configure(bg='#1e1e2e')
        
        # Theme colors (same as main app)
        self.colors = {
            'bg_primary': '#1e1e2e',
            'text_success': '#a6e3a1',
            'text_secondary': '#89b4fa',
            'bg_accent': '#3b3f4f',
            'text_primary': '#cdd6f4',
            'text_error': '#f38ba8',
            'green': '#a6e3a1',
            'orange': '#fab387',
            'blue': '#89b4fa',
            'purple': '#cba6f7',
            'red': '#f38ba8'
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the test UI."""
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Timer Widget Test",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=20)
        
        # Create timer widget
        self.timer_widget = TimerWidget(main_frame, self.colors)
        
        # Test compact view
        compact_label = tk.Label(
            main_frame,
            text="Compact View:",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        compact_label.pack(anchor='w', padx=20, pady=(20, 5))
        
        compact_frame = self.timer_widget.create_compact_widget(main_frame)
        compact_frame.pack(padx=20, pady=5)
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg=self.colors['bg_accent'])
        separator.pack(fill='x', padx=20, pady=20)
        
        # Test expanded view
        expanded_label = tk.Label(
            main_frame,
            text="Expanded View:",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        expanded_label.pack(anchor='w', padx=20, pady=(0, 5))
        
        expanded_frame = self.timer_widget.create_expanded_widget(main_frame)
        expanded_frame.pack(fill='x', padx=20, pady=5)
        
        # Status display
        self.status_label = tk.Label(
            main_frame,
            text="Timer ready - set duration and click play",
            font=("Segoe UI", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        self.status_label.pack(pady=20)
        
        # Info button
        info_button = tk.Button(
            main_frame,
            text="Get Timer Info",
            font=("Segoe UI", 10),
            fg=self.colors['bg_primary'],
            bg=self.colors['blue'],
            relief='flat',
            command=self.show_timer_info
        )
        info_button.pack(pady=10)
    
    def show_timer_info(self):
        """Display current timer information."""
        info = self.timer_widget.get_timer_info()
        timer_state = info['timer_state']
        
        status_text = (
            f"State: {timer_state['state']}\n"
            f"Duration: {timer_state['duration_minutes']} min\n"
            f"Remaining: {timer_state['time_display']}\n"
            f"Progress: {timer_state['progress_percentage']:.1f}%\n"
            f"Sound: {'On' if info['sound_enabled'] else 'Off'}\n"
            f"Backend: {info['sound_backend']['backend']}"
        )
        
        self.status_label.config(text=status_text)
    
    def run(self):
        """Start the test application."""
        print("Timer Widget Test Application")
        print("Features to test:")
        print("1. Set different durations (1-30 minutes)")
        print("2. Start/pause/resume timer")
        print("3. Reset timer")
        print("4. Toggle sound notifications")
        print("5. Test preset duration buttons")
        print("6. Observe progress bar")
        print("7. Wait for timer completion (or set to 1 minute for quick test)")
        print()
        print("Close window to exit.")
        
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = TimerTestApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
