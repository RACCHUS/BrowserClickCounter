#!/usr/bin/env python3
"""
Quick test script to verify timer pause/resume functionality.
"""

import tkinter as tk
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from timer_gui import TimerWidget


class PauseResumeTestApp:
    """Test app specifically for pause/resume functionality."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Timer Pause/Resume Test")
        self.root.geometry("400x300")
        self.root.configure(bg='#1e1e2e')
        
        # Theme colors
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
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Timer Pause/Resume Test",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Test Scenario:\n1. Timer should show 05:00 by default\n2. Click ▶ to start countdown\n3. Click ⏸ to pause\n4. Click ▶ again to resume\n5. Timer should continue from where it paused",
            font=("Segoe UI", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary'],
            justify='left'
        )
        instructions.pack(pady=(0, 20))
        
        # Create timer widget
        self.timer_widget = TimerWidget(main_frame, self.colors)
        
        # Compact view (main test)
        compact_frame = self.timer_widget.create_compact_widget(main_frame)
        compact_frame.pack(pady=20)
        
        # Status display
        self.status_label = tk.Label(
            main_frame,
            text="Timer Status: Ready (05:00)",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors['text_success'],
            bg=self.colors['bg_primary']
        )
        self.status_label.pack(pady=10)
        
        # Update status periodically
        self.update_status()
        
        # Quick test button for 10 seconds
        test_button = tk.Button(
            main_frame,
            text="Quick Test (10 seconds)",
            font=("Segoe UI", 10),
            fg=self.colors['bg_primary'],
            bg=self.colors['purple'],
            relief='flat',
            command=self.quick_test
        )
        test_button.pack(pady=5)
    
    def quick_test(self):
        """Set timer to 10 seconds for quick testing."""
        self.timer_widget.timer.reset()
        self.timer_widget.timer.duration_seconds = 10
        self.timer_widget.timer.remaining_seconds = 10
        self.timer_widget._update_display()
        self.status_label.config(text="Timer Status: Set to 10 seconds for quick test")
    
    def update_status(self):
        """Update the status display."""
        timer_info = self.timer_widget.get_timer_info()
        timer_state = timer_info['timer_state']
        
        status_text = f"Timer Status: {timer_state['state'].title()} ({timer_state['time_display']})"
        self.status_label.config(text=status_text)
        
        # Update every second
        self.root.after(1000, self.update_status)
    
    def run(self):
        """Start the test application."""
        print("Timer Pause/Resume Test")
        print("=======================")
        print("This test verifies that:")
        print("1. Timer shows 05:00 by default")
        print("2. Play button (▶) starts the timer")
        print("3. Pause button (⏸) pauses the timer")
        print("4. Play button (▶) resumes from where it paused")
        print("5. Reset button (⟲) resets to 05:00")
        print()
        print("Use 'Quick Test' to set timer to 10 seconds for faster testing.")
        print("Close window to exit.")
        
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = PauseResumeTestApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
