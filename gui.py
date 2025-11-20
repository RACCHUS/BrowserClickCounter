import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from typing import Optional
from click_logic import ClickTracker
from timer import SessionTimer
from celebration import CelebrationManager
from timer_gui import TimerWidget
    
class ClickCounterGUI:
    """GUI wrapper that uses ClickTracker for core logic."""

    def __init__(self):
        self.tracker = ClickTracker()
        self.timer = SessionTimer()
        self.celebration_manager = None  # Will be initialized after GUI setup
        self.countdown_timer: Optional[TimerWidget] = None  # Will be initialized after GUI setup
        # UI state
        self.is_expanded = False
        # Resizing state
        self.resizing = False
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_w = 0
        self.resize_start_h = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.setup_gui()
        
        # Initialize celebration manager after GUI is set up
        self.celebration_manager = CelebrationManager(self)
        
        loaded = self.tracker.load_settings()
        if loaded:
            messagebox.showinfo("Loaded", "Settings loaded!")
        
        # Initialize countdown timer widget after GUI is fully set up
        self.countdown_timer = TimerWidget(self.main_frame, self.colors)
        self._setup_timer_widgets()
        
        # Update region display after loading settings
        self.update_region_display()
        
        # Refresh the compact view to show the timer
        if not self.is_expanded:
            self.show_compact()
        
        # Set up auto-save on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.update_stats_loop()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Browser Click Counter")
        self.root.attributes("-topmost", True)
        # Allow programmatic resizing; we provide a custom grip for undecorated window
        self.root.resizable(True, True)
        self.root.overrideredirect(True)

        # Simple color scheme to keep it fast
        self.colors = {
            'bg_primary': '#1e1e2e',
            'text_success': '#a6e3a1',
            'text_secondary': '#89b4fa',
            'bg_accent': '#3b3f4f',
            'text_primary': '#cdd6f4',
            'text_error': '#f38ba8',
            'warning_orange': '#fab387',
            'warning_bg': '#2d2416',
        }

        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], bd=1, relief='solid')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title bar
        self.title_bar = tk.Frame(self.main_frame, bg=self.colors['bg_accent'], height=28)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_label = tk.Label(self.title_bar, text="Click Counter", fg=self.colors['text_primary'], bg=self.colors['bg_accent'])
        self.title_label.pack(side=tk.LEFT, padx=8)
        # Make window draggable by both the title bar and the title label
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.drag_window)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.drag_window)

        close_btn = tk.Button(self.title_bar, text='×', command=self.on_closing, bg=self.colors['bg_accent'], fg=self.colors['text_primary'], relief='flat')
        close_btn.pack(side=tk.RIGHT, padx=6)

        # Compact view
        self.compact_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        
        # Warning banner for first 105 clicks (Feature 3)
        self.compact_warning_banner = tk.Label(self.compact_frame, text='⚠ CAREFUL - First 105! ⚠', 
                                              font=("Segoe UI", 9, "bold"), fg='#1e1e2e', 
                                              bg=self.colors['warning_orange'], pady=2)
        # Don't pack it yet - will be shown/hidden based on count
        
        self.count_label = tk.Label(self.compact_frame, text=str(self.tracker.count), font=("Segoe UI", 16, "bold"), fg=self.colors['text_success'], bg=self.colors['bg_primary'])
        self.count_label.pack(pady=10)
        
        # IPH stat in compact view
        self.compact_iph_label = tk.Label(self.compact_frame, text="IPH: 0.0", font=("Segoe UI", 8), 
                                        fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        self.compact_iph_label.pack(pady=(0, 5))
        
        # Compact control buttons
        compact_controls = tk.Frame(self.compact_frame, bg=self.colors['bg_primary'])
        compact_controls.pack(pady=5)
        
        self.compact_start_btn = tk.Button(compact_controls, text='▶ Start', command=self.toggle_listening,
                                         bg=self.colors['text_success'], fg='white', width=8, font=("Segoe UI", 9))
        self.compact_start_btn.pack(side=tk.LEFT, padx=2)
        
        self.compact_draw_btn = tk.Button(compact_controls, text='✏ Draw', command=self.draw_region,
                                        bg=self.colors['text_secondary'], fg='white', width=8, font=("Segoe UI", 9))
        self.compact_draw_btn.pack(side=tk.LEFT, padx=2)
        
        # Placeholder for compact timer (will be added after timer initialization)
        self.compact_timer_placeholder = tk.Frame(self.compact_frame, bg=self.colors['bg_primary'], height=25)
        self.compact_timer_placeholder.pack(pady=5)
        
        self.expand_btn = tk.Button(self.compact_frame, text='⚙', command=self.toggle_view,
                                   bg=self.colors['bg_accent'], fg=self.colors['text_primary'], 
                                   font=("Segoe UI", 8), relief='flat', padx=4, pady=2, width=3)
        self.expand_btn.pack()
        # Allow dragging the window by the compact area (click-and-drag anywhere on compact_frame)
        self.compact_frame.bind("<Button-1>", self.start_drag)
        self.compact_frame.bind("<B1-Motion>", self.drag_window)
        # Also bind the big label so users can drag by the count text
        self.count_label.bind("<Button-1>", self.start_drag)
        self.count_label.bind("<B1-Motion>", self.drag_window)

        # Expanded view
        self.expanded_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        
        # Warning banner for first 105 clicks in expanded view (Feature 3)
        self.expanded_warning_banner = tk.Label(self.expanded_frame, text='⚠ CAREFUL - First 105 Clicks! ⚠', 
                                               font=("Segoe UI", 11, "bold"), fg='#1e1e2e', 
                                               bg=self.colors['warning_orange'], pady=4)
        # Don't pack it yet - will be shown/hidden based on count
        
        self.expanded_count_label = tk.Label(self.expanded_frame, text=f"Clicks: {self.tracker.count}", fg=self.colors['text_success'], bg=self.colors['bg_primary'])
        self.expanded_count_label.pack(anchor='w', padx=8, pady=4)

        # Sweet message
        self.love_label = tk.Label(self.expanded_frame, text='💖 I love you Ashley 💖', 
                                   fg='#f5c2e7', bg=self.colors['bg_primary'], 
                                   font=("Segoe UI", 10, "italic"))
        self.love_label.pack(anchor='center', pady=(0, 6))

        # Button container with improved layout
        btn_container = tk.Frame(self.expanded_frame, bg=self.colors['bg_primary'])
        btn_container.pack(fill=tk.X, padx=8, pady=4)

        # Row 1: Session Controls
        session_frame = tk.Frame(btn_container, bg=self.colors['bg_primary'])
        session_frame.pack(fill=tk.X, pady=2)
        
        self.start_btn = tk.Button(session_frame, text='▶ Start', command=self.toggle_listening, 
                                  bg=self.colors['text_success'], fg='white', width=10)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = tk.Button(session_frame, text='⏸ Pause', command=self.toggle_pause, 
                                  bg='#f1c40f', fg='white', width=10, state='disabled')
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(session_frame, text='🔄 Reset Session', command=self.reset_session, 
                 bg=self.colors['text_error'], fg='white', width=12).pack(side=tk.LEFT, padx=2)

        # Row 2: Region Management and Settings
        tools_frame = tk.Frame(btn_container, bg=self.colors['bg_primary'])
        tools_frame.pack(fill=tk.X, pady=2)
        
        tk.Button(tools_frame, text='✏ Draw', command=self.draw_region, 
                 bg=self.colors['bg_accent'], fg=self.colors['text_primary'], width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text='⚙ Manage', command=self.manage_regions, 
                 bg=self.colors['bg_accent'], fg=self.colors['text_primary'], width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(tools_frame, text='� Load Last Session', command=self.load_last_session, 
                 bg='#3498db', fg='white', width=16).pack(side=tk.RIGHT, padx=2)

        # Row 3: View Control
        view_frame = tk.Frame(btn_container, bg=self.colors['bg_primary'])
        view_frame.pack(fill=tk.X, pady=(6, 2))
        
        tk.Button(view_frame, text='⬇ Collapse', command=self.toggle_view, 
                 bg='#8e44ad', fg='white', width=15).pack(anchor='center')

        # Countdown Timer (expanded view) - placeholder for now
        self.expanded_timer_placeholder = tk.Frame(self.expanded_frame, bg=self.colors['bg_primary'], height=100)
        self.expanded_timer_placeholder.pack(fill='x', padx=8, pady=5)

        # Timer display (expanded view)
        self.timer_label = tk.Label(self.expanded_frame, text='Session: 00:00:00', fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        self.timer_label.pack(anchor='e', padx=8, pady=(6, 0))

        # Images Per Hour (IPH) stat — derived from session timer and click count
        self.iph_label = tk.Label(self.expanded_frame, text='IPH: 0.0', fg=self.colors['text_secondary'], bg=self.colors['bg_primary'])
        self.iph_label.pack(anchor='e', padx=8, pady=(2, 8))

        # Add ttk.Sizegrip in bottom-right corner only
        self.sizegrip = ttk.Sizegrip(self.root)
        self.sizegrip.place(relx=1.0, rely=1.0, anchor='se')

        self.show_compact()

    def _setup_timer_widgets(self):
        """Set up timer widgets in their designated areas."""
        if not self.countdown_timer:
            return  # Safety check
            
        # Remove placeholders
        self.compact_timer_placeholder.destroy()
        self.expanded_timer_placeholder.destroy()
        
        # Create actual timer widgets
        self.compact_timer_frame = self.countdown_timer.create_compact_widget(self.compact_frame)
        self.expanded_timer_frame = self.countdown_timer.create_expanded_widget(self.expanded_frame)
        
        # Position the expanded timer frame before the session timer
        self.expanded_timer_frame.pack_configure(before=self.timer_label)

    # UI helpers
    def show_compact(self):
        # Hide expanded view
        self.expanded_frame.pack_forget()
        # Only show essential items in compact view (no control buttons for minimal size)
        for widget in self.compact_frame.winfo_children():
            widget.pack_forget()
        
        # Pack the essential compact elements only
        self.count_label.pack(pady=(5, 2))  # Main count display - reduced padding
        self.compact_iph_label.pack(pady=(0, 3))  # Show IPH
        
        # Show compact timer if it exists
        if hasattr(self, 'compact_timer_frame') and self.compact_timer_frame:
            self.compact_timer_frame.pack(pady=2)  # Timer with its controls
        
        # Add expand button below timer
        self.expand_btn.pack(pady=(3, 5))  # Expand button with small spacing
        self.compact_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Set to narrower compact size - preserve current position
        # Adjust height based on whether we're in first 105 (banner visible)
        if self.tracker.count < 105:
            self.root.geometry('130x185')  # Taller to accommodate warning banner
        else:
            self.root.geometry('130x160')  # Normal compact size
        self.is_expanded = False

    def show_expanded(self):
        self.compact_frame.pack_forget()
        self.expanded_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Resize to expanded size - preserve current position
        try:
            cur_w = self.root.winfo_width()
            cur_h = self.root.winfo_height()
            if cur_w < 360 or cur_h < 280:
                self.root.geometry('360x480')
        except Exception:
            self.root.geometry('360x480')
        self.is_expanded = True

    def toggle_view(self):
        if self.is_expanded:
            self.show_compact()
        else:
            self.show_expanded()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self.drag_start_x
        y = self.root.winfo_pointery() - self.drag_start_y
        self.root.geometry(f'+{x}+{y}')

    # Action methods
    def draw_region(self):
        from region_drawer import RegionDrawer
        self.root.withdraw()
        RegionDrawer(self.on_region_drawn)

    def on_region_drawn(self, region):
        self.root.deiconify()
        if region:
            print(f"DEBUG: GUI received region: {region}")
            
            # If there are existing regions, ask if user wants to replace or add
            if self.tracker.regions:
                replace = messagebox.askyesno('Region Settings', 
                    f'You already have {len(self.tracker.regions)} region(s) set.\n\n'
                    'Yes = Replace existing regions with this new one\n'
                    'No = Add this region to existing ones',
                    default='yes')
                if replace:
                    self.tracker.clear_regions()
                    print(f"DEBUG: Cleared existing regions before adding new one")
            
            self.tracker.add_region(region)
            save_result = self.tracker.save_settings()  # Auto-save after adding region
            print(f"DEBUG: Save settings result: {save_result}")
            self.update_region_display()  # Update region status display
            
            # Show appropriate success message
            if len(self.tracker.regions) == 1:
                messagebox.showinfo('Success', f"Set new click region: ({region['x1']},{region['y1']}) to ({region['x2']},{region['y2']})")
            else:
                messagebox.showinfo('Success', f"Added region: ({region['x1']},{region['y1']}) to ({region['x2']},{region['y2']}) - Total: {len(self.tracker.regions)} regions")
        else:
            print("DEBUG: GUI received None region (cancelled)")

    def manage_regions(self):
        from region_manager import RegionManager
        if not self.tracker.regions:
            result = messagebox.askyesno('No Regions', 'No regions to manage. Would you like to draw one now?')
            if result:
                self.draw_region()
            return
        RegionManager(self.root, self.tracker.regions, self.on_regions_changed)

    def on_regions_changed(self):
        """Called when regions are modified in the region manager."""
        self.tracker.save_settings()  # Auto-save when regions change
        self.update_region_display()  # Update the display

    def update_region_display(self):
        """Update the region status display in both compact and expanded views."""
        status = self.tracker.get_region_status()
        print(f"DEBUG: Updating region display with status: {status}")
        print(f"DEBUG: Current regions count: {len(self.tracker.regions)}")
        # No region display in compact view anymore - just update button states
        # Update button visibility - if no regions, make draw button more prominent
        if not self.tracker.regions:
            self.compact_start_btn.config(state='disabled')
            self.compact_draw_btn.config(bg=self.colors['text_error'])  # Make draw button red to draw attention
        else:
            self.compact_start_btn.config(state='normal')
            self.compact_draw_btn.config(bg=self.colors['text_secondary'])  # Normal blue

    def toggle_listening(self):
        if not self.tracker.regions:
            # If no regions, prompt to draw one
            result = messagebox.askyesno('No Regions', 'No click regions set. Would you like to draw one now?')
            if result:
                self.draw_region()
            return
            
        if self.tracker.is_listening:
            self.tracker.stop_listening()
            self.timer.stop()
            self.update_status(False)
            # Update button states
            self.start_btn.config(text='▶ Start', bg=self.colors['text_success'])
            self.compact_start_btn.config(text='▶ Start', bg=self.colors['text_success'])
            self.pause_btn.config(state='disabled', text='⏸ Pause', bg='#f1c40f')
        else:
            self.tracker.start_listening(on_counted=self.on_click_counted)
            # start session timer when tracking starts
            self.timer.start()
            self.update_status(True)
            # Update button states
            self.start_btn.config(text='⏹ Stop', bg=self.colors['text_error'])
            self.compact_start_btn.config(text='⏹ Stop', bg=self.colors['text_error'])
            self.pause_btn.config(state='normal')

    def toggle_pause(self):
        if not self.tracker.is_listening:
            return
        
        if self.tracker.is_paused:
            # Resume
            self.tracker.resume_listening()
            self.timer.resume()
            self.pause_btn.config(text='⏸ Pause', bg='#f1c40f')
            self.update_status(True)
        else:
            # Pause
            self.tracker.pause_listening()
            self.timer.pause()
            self.pause_btn.config(text='▶ Resume', bg='#27ae60')
            self.update_status(False)

    def on_click_counted(self, milestone=None):
        """Called when a click is counted, handles celebrations and display updates."""
        self.update_count_display()
        
        # Special celebration when reaching 105 clicks (Feature 5)
        if self.tracker.count == 105:
            messagebox.showinfo('Milestone Reached! 🎉', 
                              '✅ Congratulations!\n\nYou\'ve completed the critical first 105 clicks!\n\nYou can now relax - the difficult part is over!')
        
        # Trigger celebration if milestone reached
        if milestone and self.celebration_manager:
            self.celebration_manager.trigger_celebration(milestone, self.tracker.count)

    def update_count_display(self):
        count = self.tracker.count
        in_first_105 = count < 105
        
        # Feature 1: Color-coded counter (orange during first 105)
        # Feature 2: Show progress format X/105 while under 105
        if in_first_105:
            compact_text = f"{count}/105"
            expanded_text = f"Clicks: {count}/105"
            text_color = self.colors['warning_orange']
        else:
            compact_text = str(count)
            expanded_text = f"Clicks: {count}"
            text_color = self.colors['text_success']
        
        self.count_label.config(text=compact_text, fg=text_color)
        self.expanded_count_label.config(text=expanded_text, fg=text_color)
        
        # Feature 3: Show/hide warning banners
        if in_first_105:
            # Show banners if not already shown
            if not self.compact_warning_banner.winfo_ismapped():
                self.compact_warning_banner.pack(side=tk.TOP, fill=tk.X, before=self.count_label)
            if not self.expanded_warning_banner.winfo_ismapped():
                self.expanded_warning_banner.pack(side=tk.TOP, fill=tk.X, pady=(0, 4))
        else:
            # Hide banners
            if self.compact_warning_banner.winfo_ismapped():
                self.compact_warning_banner.pack_forget()
            if self.expanded_warning_banner.winfo_ismapped():
                self.expanded_warning_banner.pack_forget()
        
        # Feature 4: Background color change
        warning_bg = self.colors['warning_bg'] if in_first_105 else self.colors['bg_primary']
        self.compact_frame.config(bg=warning_bg)
        self.expanded_frame.config(bg=warning_bg)
        self.count_label.config(bg=warning_bg)
        self.expanded_count_label.config(bg=warning_bg)
        self.compact_iph_label.config(bg=warning_bg)
        
        # Update all compact frame children backgrounds
        for child in self.compact_frame.winfo_children():
            try:
                if isinstance(child, tk.Frame):
                    child.config(bg=warning_bg)
            except:
                pass
        
        # Adjust compact window size when transitioning at 105 clicks
        if not self.is_expanded:
            if count == 105:
                # Just passed 105, shrink window since banner is now hidden
                self.root.geometry('130x160')
            elif count == 104:
                # About to reach 105, ensure window is tall enough
                self.root.geometry('130x185')

    def update_status(self, running: bool):
        if running and not self.tracker.is_paused:
            self.expanded_count_label.config(fg=self.colors['text_success'])
        else:
            self.expanded_count_label.config(fg=self.colors['text_error'])

    def reset_session(self):
        """Reset current session and save it first."""
        if self.tracker.count > 0 or self.timer.elapsed_seconds() > 0:
            if messagebox.askyesno('Reset Session', 'Save current session and start a new one?'):
                # Save current session before resetting
                self.save_current_session()
                
                # Reset session data
                self.tracker.reset_session()
                self.timer.reset()
                
                # Reset button states
                self.start_btn.config(text='▶ Start', bg=self.colors['text_success'])
                self.compact_start_btn.config(text='▶ Start', bg=self.colors['text_success'])
                self.pause_btn.config(state='disabled', text='⏸ Pause', bg='#f1c40f')
                
                # Stop listening
                self.tracker.stop_listening()
                self.update_count_display()
                self.update_status(False)
                
                messagebox.showinfo('Session Reset', 'Previous session saved. New session started!')
        else:
            messagebox.showinfo('No Session', 'No active session to reset.')

    def save_current_session(self):
        """Save the current session data."""
        duration_seconds = self.timer.elapsed_seconds()
        self.tracker.save_session(duration_seconds)

    def load_last_session(self):
        """Load and display information from the last saved session."""
        try:
            session_data = self.tracker.load_last_session()
            if session_data:
                info = f"Last Session Data:\n\n"
                info += f"Clicks: {session_data['clicks']}\n"
                info += f"Duration: {session_data['duration_formatted']}\n"
                info += f"IPH: {session_data['iph']}\n"
                info += f"Regions Used: {session_data['regions_used']}\n"
                info += f"Completed: {session_data['completed_at'][:19].replace('T', ' ')}"
                messagebox.showinfo('Last Session', info)
            else:
                messagebox.showinfo('No Session', 'No previous session data found.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load session: {e}')

    def force_reload_settings(self):
        """Force reload settings from disk - useful for debugging region issues."""
        result = self.tracker.force_reload_settings()
        self.update_region_display()
        if result:
            messagebox.showinfo('Reload Settings', f'Settings reloaded! Found {len(self.tracker.regions)} regions.')
        else:
            messagebox.showwarning('Reload Settings', 'No settings file found or failed to load.')

    def on_closing(self):
        """Handle app closing - save session and settings."""
        # Save current session if there's activity
        if self.tracker.count > 0 or self.timer.elapsed_seconds() > 0:
            self.save_current_session()
        
        # Save app settings (regions, etc.)
        self.tracker.save_settings()
        
        # Clean up celebration animations
        if self.celebration_manager:
            self.celebration_manager.cleanup_all()
        
        # Clean up countdown timer
        if self.countdown_timer:
            self.countdown_timer.cleanup()
        
        # Stop any running processes
        if self.tracker.is_listening:
            self.tracker.stop_listening()
        
        self.root.destroy()

    def update_stats_loop(self):
        # Calculate IPH for both views
        secs = self.timer.elapsed_seconds()
        if secs <= 0:
            iph = 0.0
        else:
            hours = secs / 3600.0
            iph = self.tracker.count / hours if hours > 0 else 0.0
        
        # Update count display with all first-105 features
        self.update_count_display()
        
        if self.is_expanded:
            # update timer label with pause indication
            timer_text = f"Session: {self.timer.format_hms()}"
            if self.timer.is_paused():
                timer_text += " (PAUSED)"
            self.timer_label.config(text=timer_text)
            # show with one decimal place
            self.iph_label.config(text=f"IPH: {iph:.1f}")
        else:
            # Update compact IPH
            self.compact_iph_label.config(text=f"IPH: {iph:.1f}")
        
        self.root.after(1000, self.update_stats_loop)

    # --- Resize handlers ---
    def start_resize(self, event):
        # record initial pointer and window size
        self.resizing = True
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_w = self.root.winfo_width()
        self.resize_start_h = self.root.winfo_height()

    def do_resize(self, event):
        if not self.resizing:
            return
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y
        new_w = max(120, int(self.resize_start_w + dx))
        new_h = max(80, int(self.resize_start_h + dy))
        # enforce larger minimums for expanded mode
        if self.is_expanded:
            new_w = max(360, new_w)
            new_h = max(240, new_h)
        self.root.geometry(f"{new_w}x{new_h}")

    def stop_resize(self, event):
        self.resizing = False

    def old_on_closing_cleanup(self):
        """Original cleanup code for reference."""
        # Clean up celebration animations
        if self.celebration_manager:
            self.celebration_manager.cleanup_all()
        
        # Clean up countdown timer
        if self.countdown_timer:
            self.countdown_timer.cleanup()
            
        self.tracker.stop_listening()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
