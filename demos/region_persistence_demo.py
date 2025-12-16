#!/usr/bin/env python3
"""
Demo script to show the new region persistence features.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os

def show_settings_file():
    """Show the contents of the settings file."""
    settings_file = 'click_counter_settings.json'
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        info = "Current Settings:\n\n"
        info += f"Count: {settings.get('count', 0)}\n"
        info += f"Browser Detection: {settings.get('browser_detection', True)}\n"
        info += f"Number of Regions: {len(settings.get('regions', []))}\n"
        
        if settings.get('last_region'):
            last_region = settings['last_region']
            width = last_region['x2'] - last_region['x1']
            height = last_region['y2'] - last_region['y1']
            info += f"Last Region: {width}×{height} at ({last_region['x1']},{last_region['y1']})\n"
        
        if settings.get('regions'):
            info += "\nAll Regions:\n"
            for i, region in enumerate(settings['regions']):
                width = region['x2'] - region['x1']
                height = region['y2'] - region['y1']
                info += f"  {i+1}: {width}×{height} at ({region['x1']},{region['y1']})\n"
        
        info += f"\nLast Updated: {settings.get('timestamp', 'Unknown')}"
        
        messagebox.showinfo("Settings File Contents", info)
    else:
        messagebox.showinfo("Settings File", "No settings file found. Run the main app first!")

def create_demo_settings():
    """Create a demo settings file with sample region data."""
    settings = {
        'count': 150,
        'regions': [
            {'x1': 100, 'y1': 100, 'x2': 300, 'y2': 200}
        ],
        'last_region': {'x1': 100, 'y1': 100, 'x2': 300, 'y2': 200},
        'browser_detection': True,
        'timestamp': '2025-09-03T10:30:00'
    }
    
    with open('click_counter_settings.json', 'w') as f:
        json.dump(settings, f, indent=2)
    
    messagebox.showinfo("Demo Created", "Created demo settings file with a sample region!\nNow run the main app to see it loaded automatically.")

def main():
    """Create a simple demo interface."""
    root = tk.Tk()
    root.title("Region Persistence Demo")
    root.geometry("400x300")
    root.configure(bg='#1e1e2e')
    
    # Title
    title = tk.Label(root, text="Browser Click Counter\nRegion Persistence Demo", 
                    font=("Segoe UI", 16, "bold"), fg='#cdd6f4', bg='#1e1e2e')
    title.pack(pady=20)
    
    # Description
    desc = tk.Label(root, text="This demo shows the new region persistence features:\n\n"
                              "• Last used region is automatically saved\n"
                              "• App loads with previous region ready to use\n"
                              "• Compact view shows region status\n"
                              "• Start button is enabled when region is available\n"
                              "• Draw button highlighted when no regions set",
                    font=("Segoe UI", 10), fg='#89b4fa', bg='#1e1e2e', justify='left')
    desc.pack(pady=20, padx=20)
    
    # Buttons
    btn_frame = tk.Frame(root, bg='#1e1e2e')
    btn_frame.pack(pady=20)
    
    show_btn = tk.Button(btn_frame, text="Show Current Settings", command=show_settings_file,
                        bg='#a6e3a1', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                        relief="flat", bd=0, padx=15, pady=8)
    show_btn.pack(pady=5)
    
    demo_btn = tk.Button(btn_frame, text="Create Demo Settings", command=create_demo_settings,
                        bg='#89b4fa', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                        relief="flat", bd=0, padx=15, pady=8)
    demo_btn.pack(pady=5)
    
    close_btn = tk.Button(btn_frame, text="Close", command=root.destroy,
                         bg='#f38ba8', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                         relief="flat", bd=0, padx=15, pady=8)
    close_btn.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()
