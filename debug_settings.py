#!/usr/bin/env python3
"""
Debug script to test settings loading/saving behavior.
Run this to check where the settings file is being saved and loaded from.
"""

import os
import sys
from click_logic import ClickTracker

def main():
    print("=== Settings Debug Information ===")
    print(f"Python executable: {sys.executable}")
    print(f"Script location: {__file__}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    
    # Create tracker to test settings paths
    tracker = ClickTracker()
    
    settings_path = tracker._get_settings_path()
    session_path = tracker._get_settings_path('last_session.json')
    
    print(f"\nSettings directory: {tracker._settings_dir}")
    print(f"Settings file path: {settings_path}")
    print(f"Session file path: {session_path}")
    
    # Check if settings file exists
    print(f"\nSettings file exists: {os.path.exists(settings_path)}")
    if os.path.exists(settings_path):
        print(f"Settings file size: {os.path.getsize(settings_path)} bytes")
        print(f"Settings file modified: {os.path.getmtime(settings_path)}")
    
    # Try to load settings
    print(f"\nTrying to load settings...")
    loaded = tracker.load_settings()
    print(f"Load result: {loaded}")
    print(f"Regions loaded: {len(tracker.regions)}")
    for i, region in enumerate(tracker.regions):
        print(f"  Region {i+1}: {region}")
    
    # Test saving a dummy region
    print(f"\nTesting save functionality...")
    test_region = {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}
    tracker.add_region(test_region)
    save_result = tracker.save_settings()
    print(f"Save result: {save_result}")
    
    # Verify the save worked
    tracker2 = ClickTracker()
    loaded2 = tracker2.load_settings()
    print(f"Verification load result: {loaded2}")
    print(f"Verification regions count: {len(tracker2.regions)}")

if __name__ == '__main__':
    main()