#!/usr/bin/env python3
"""
Demo script showing the updated timer features:
1. 5-minute timer by default in compact view
2. Play/pause and reset buttons
3. Repeating sound until reset
"""

import tkinter as tk
import sys
import os

# Add the current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from timer_gui import TimerWidget


class TimerDemoApp:
    """Demo application showing the updated timer features."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Updated Timer Demo - 5min Default + Repeat Sound")
        self.root.geometry("500x400")
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
        """Set up the demo UI."""
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Updated Timer Features Demo",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Feature list
        features_label = tk.Label(
            main_frame,
            text="✅ 5-minute timer by default\n✅ Play/pause button\n✅ Reset button in compact view\n✅ Sound repeats until reset",
            font=("Segoe UI", 12),
            fg=self.colors['text_success'],
            bg=self.colors['bg_primary'],
            justify='left'
        )
        features_label.pack(pady=(0, 20))
        
        # Create timer widget
        self.timer_widget = TimerWidget(main_frame, self.colors)
        
        # Compact view demo (what user sees by default)
        compact_demo_frame = tk.Frame(main_frame, bg=self.colors['bg_accent'], relief='solid', bd=2)
        compact_demo_frame.pack(pady=10, padx=20, fill='x')
        
        compact_title = tk.Label(
            compact_demo_frame,
            text="Compact View (Default in Browser Click Counter):",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_accent']
        )
        compact_title.pack(pady=5)
        
        # Simulated click counter
        count_label = tk.Label(
            compact_demo_frame,
            text="42",
            font=("Segoe UI", 24, "bold"),
            fg=self.colors['text_success'],
            bg=self.colors['bg_accent']
        )
        count_label.pack(pady=5)
        
        # The actual timer widget
        compact_frame = self.timer_widget.create_compact_widget(compact_demo_frame)
        compact_frame.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Instructions:\n1. Timer shows 05:00 by default\n2. Click ▶ to start, ⏸ to pause\n3. Click ⟲ to reset\n4. When timer completes, sound repeats every 3 seconds\n5. Reset stops the repeating sound",
            font=("Segoe UI", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary'],
            justify='left'
        )
        instructions.pack(pady=20)
        
        # Quick test button
        test_button = tk.Button(
            main_frame,
            text="Quick Test (Set to 5 seconds)",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors['bg_primary'],
            bg=self.colors['purple'],
            relief='flat',
            command=self.quick_test
        )
        test_button.pack(pady=10)
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Timer ready at 5 minutes. Click play to start or use quick test.",
            font=("Segoe UI", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg_primary']
        )
        self.status_label.pack(pady=10)
    
    def quick_test(self):
        """Set timer to 5 seconds for quick testing."""
        # Reset timer first
        self.timer_widget.timer.reset()
        # Manually set for demo (bypass normal validation)
        self.timer_widget.timer.duration_seconds = 5
        self.timer_widget.timer.remaining_seconds = 5
        self.timer_widget._update_display()
        self.status_label.config(text="Timer set to 5 seconds for quick demo. Click play!")
    
    def run(self):
        """Start the demo application."""
        print("Timer Features Demo")
        print("===================")
        print("This demo shows the updated timer features:")
        print("- 5-minute default duration")
        print("- Play/pause button (▶/⏸)")
        print("- Reset button (⟲)")
        print("- Repeating sound on completion")
        print()
        print("Try the 'Quick Test' button to set timer to 5 seconds for fast demo!")
        print("Close window to exit.")
        
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = TimerDemoApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
