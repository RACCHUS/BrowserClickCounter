#!/usr/bin/env python3
"""
Demo script to show the new session-based saving features.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

def show_session_file():
    """Show the contents of the last session file."""
    session_file = 'last_session.json'
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        info = "Last Session Data:\n\n"
        info += f"Clicks: {session.get('clicks', 0)}\n"
        info += f"Duration: {session.get('duration_formatted', '00:00:00')}\n"
        info += f"IPH: {session.get('iph', 0.0)}\n"
        info += f"Regions Used: {session.get('regions_used', 0)}\n"
        completed_at = session.get('completed_at', '')
        if completed_at:
            # Format the timestamp nicely
            completed_at = completed_at[:19].replace('T', ' ')
        info += f"Completed: {completed_at}\n"
        
        info += f"\nRaw Duration: {session.get('duration_seconds', 0)} seconds"
        
        messagebox.showinfo("Session File Contents", info)
    else:
        messagebox.showinfo("Session File", "No session file found. Complete a session in the main app first!")

def show_settings_file():
    """Show the contents of the settings file."""
    settings_file = 'click_counter_settings.json'
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        info = "App Settings (Regions Only):\n\n"
        info += f"Number of Regions: {len(settings.get('regions', []))}\n"
        info += f"Browser Detection: {settings.get('browser_detection', True)}\n"
        
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
        messagebox.showinfo("Settings File", "No settings file found.")

def create_demo_session():
    """Create a demo session file with sample data."""
    session = {
        'clicks': 247,
        'duration_seconds': 3665,  # 1 hour, 1 minute, 5 seconds
        'duration_formatted': '01:01:05',
        'iph': 241.2,
        'completed_at': datetime.now().isoformat(),
        'regions_used': 1
    }
    
    with open('last_session.json', 'w') as f:
        json.dump(session, f, indent=2)
    
    messagebox.showinfo("Demo Created", "Created demo session file!\nUse 'Show Session Data' to view it, or 'Load Last Session' in the main app.")

def main():
    """Create a simple demo interface."""
    root = tk.Tk()
    root.title("Session Saving Demo")
    root.geometry("450x350")
    root.configure(bg='#1e1e2e')
    
    # Title
    title = tk.Label(root, text="Browser Click Counter\nSession Saving Demo", 
                    font=("Segoe UI", 16, "bold"), fg='#cdd6f4', bg='#1e1e2e')
    title.pack(pady=20)
    
    # Description
    desc = tk.Label(root, text="New Session-Based Features:\n\n"
                              "• Sessions auto-save when you reset or close app\n"
                              "• Each session stores: clicks, time, IPH, date/time\n"
                              "• No more cumulative totals - just session data\n"
                              "• Compact JSON storage for efficiency\n"
                              "• Load Last Session shows previous session stats\n"
                              "• App settings (regions) saved separately",
                    font=("Segoe UI", 10), fg='#89b4fa', bg='#1e1e2e', justify='left')
    desc.pack(pady=20, padx=20)
    
    # Buttons
    btn_frame = tk.Frame(root, bg='#1e1e2e')
    btn_frame.pack(pady=20)
    
    session_btn = tk.Button(btn_frame, text="Show Session Data", command=show_session_file,
                           bg='#a6e3a1', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                           relief="flat", bd=0, padx=15, pady=8)
    session_btn.pack(pady=5)
    
    settings_btn = tk.Button(btn_frame, text="Show App Settings", command=show_settings_file,
                            bg='#89b4fa', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                            relief="flat", bd=0, padx=15, pady=8)
    settings_btn.pack(pady=5)
    
    demo_btn = tk.Button(btn_frame, text="Create Demo Session", command=create_demo_session,
                        bg='#f9e2af', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                        relief="flat", bd=0, padx=15, pady=8)
    demo_btn.pack(pady=5)
    
    close_btn = tk.Button(btn_frame, text="Close", command=root.destroy,
                         bg='#f38ba8', fg='#1e1e2e', font=("Segoe UI", 10, "bold"),
                         relief="flat", bd=0, padx=15, pady=8)
    close_btn.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()
