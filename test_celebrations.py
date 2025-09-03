#!/usr/bin/env python3
"""
Test script for the new lightweight celebration system.
"""

import tkinter as tk
import time
import sys

# Mock GUI class for testing
class MockGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Celebration Test")
        self.root.geometry("400x300")
        self.root.configure(bg='#1e1e2e')  # Dark theme
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='#1e1e2e')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create count label (simulating the real app)
        self.count_label = tk.Label(
            self.main_frame,
            text="0",
            font=("Segoe UI", 24, "bold"),
            fg="#cdd6f4",  # Text color
            bg="#1e1e2e",  # Background
            justify='center'
        )
        self.count_label.pack(pady=50)
        
        # Test buttons
        self.button_frame = tk.Frame(self.main_frame, bg='#1e1e2e')
        self.button_frame.pack(pady=20)
        
        # Button for 100-click celebration
        self.test_minor_btn = tk.Button(
            self.button_frame,
            text="Test 100-Click Celebration",
            command=self.test_minor_celebration,
            bg="#89b4fa",
            fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            relief='flat',
            padx=20,
            pady=5
        )
        self.test_minor_btn.pack(side='left', padx=10)
        
        # Button for 1000-click celebration
        self.test_major_btn = tk.Button(
            self.button_frame,
            text="Test 1000-Click Celebration",
            command=self.test_major_celebration,
            bg="#cba6f7",
            fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            relief='flat',
            padx=20,
            pady=5
        )
        self.test_major_btn.pack(side='left', padx=10)
        
        # Initialize celebration manager
        from celebration import CelebrationManager
        self.celebration_manager = CelebrationManager(self)
        
        # Status label
        self.status_label = tk.Label(
            self.main_frame,
            text="Click buttons to test celebrations",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#1e1e2e"
        )
        self.status_label.pack(pady=10)
    
    def test_minor_celebration(self):
        """Test 100-click celebration."""
        self.count_label.config(text="100")
        self.status_label.config(text="Testing 100-click celebration...")
        self.celebration_manager.trigger_celebration("minor", 100)
        
        # Reset after animation
        self.root.after(3000, lambda: self.status_label.config(text="Click buttons to test celebrations"))
    
    def test_major_celebration(self):
        """Test 1000-click celebration."""
        self.count_label.config(text="1000")
        self.status_label.config(text="Testing 1000-click celebration...")
        self.celebration_manager.trigger_celebration("major", 1000)
        
        # Reset after animation
        self.root.after(4000, lambda: self.status_label.config(text="Click buttons to test celebrations"))
    
    def run(self):
        """Start the test application."""
        print("Starting celebration test...")
        print("1. Click 'Test 100-Click Celebration' to see light celebration")
        print("2. Click 'Test 1000-Click Celebration' to see enhanced celebration")
        print("3. Close window to exit")
        
        self.root.mainloop()


if __name__ == "__main__":
    try:
        # Create and run test GUI
        app = MockGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error during test: {e}")
        sys.exit(1)
