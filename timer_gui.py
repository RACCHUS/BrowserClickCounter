"""
Timer GUI components for Browser Click Counter.
Provides compact and expanded timer interfaces.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any
from timer import CountdownTimer
from sound_manager import SoundManager


class TimerWidget:
    """
    Main timer widget that provides both compact and expanded interfaces.
    Manages timer display, controls, and sound notifications.
    """
    
    def __init__(self, parent: tk.Widget, theme_colors: Dict[str, str]):
        """
        Initialize timer widget.
        
        Args:
            parent: Parent widget
            theme_colors: Color scheme dictionary
        """
        self.parent = parent
        self.colors = theme_colors
        
        # Initialize timer and sound manager
        self.timer = CountdownTimer(default_duration_minutes=5)
        self.sound_manager = SoundManager()
        
        # GUI components
        self.compact_frame: Optional[tk.Frame] = None
        self.expanded_frame: Optional[tk.Frame] = None
        
        # Timer display elements
        self.compact_time_label: Optional[tk.Label] = None
        self.compact_control_button: Optional[tk.Button] = None
        self.compact_reset_button: Optional[tk.Button] = None
        self.expanded_time_label: Optional[tk.Label] = None
        self.expanded_controls_frame: Optional[tk.Frame] = None
        
        # Control elements
        self.duration_var = tk.StringVar(value="5")
        self.sound_enabled_var = tk.BooleanVar(value=True)
        
        # Update tracking
        self.update_job_id: Optional[str] = None
        self.is_updating = False
        
        # Setup timer callbacks
        self._setup_timer_callbacks()
        
        # Initialize display
        self._update_display()
        self._update_controls()
    
    def _setup_timer_callbacks(self):
        """Setup timer event callbacks."""
        self.timer.set_callback('on_tick', self._on_timer_tick)
        self.timer.set_callback('on_complete', self._on_timer_complete)
        self.timer.set_callback('on_start', self._on_timer_start)
        self.timer.set_callback('on_pause', self._on_timer_pause)
        self.timer.set_callback('on_resume', self._on_timer_resume)
        self.timer.set_callback('on_reset', self._on_timer_reset)
    
    def create_compact_widget(self, parent: tk.Widget) -> tk.Frame:
        """
        Create compact timer widget for collapsed mode.
        
        Args:
            parent: Parent widget
            
        Returns:
            tk.Frame: Compact timer frame
        """
        self.compact_frame = tk.Frame(parent, bg=self.colors.get('bg_primary', '#1e1e2e'))
        
        # Timer display
        self.compact_time_label = tk.Label(
            self.compact_frame,
            text="05:00",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors.get('text_primary', '#cdd6f4'),
            bg=self.colors.get('bg_primary', '#1e1e2e'),
            width=6
        )
        self.compact_time_label.pack(side='left', padx=(0, 5))
        
        # Control buttons frame
        compact_buttons_frame = tk.Frame(self.compact_frame, bg=self.colors.get('bg_primary', '#1e1e2e'))
        compact_buttons_frame.pack(side='left')
        
        # Control button (play/pause)
        self.compact_control_button = tk.Button(
            compact_buttons_frame,
            text="▶",
            font=("Segoe UI", 8),
            fg=self.colors.get('bg_primary', '#1e1e2e'),
            bg=self.colors.get('green', '#a6e3a1'),
            relief='flat',
            width=3,
            command=self._toggle_timer
        )
        self.compact_control_button.pack(side='left', padx=(0, 2))
        
        # Reset button
        self.compact_reset_button = tk.Button(
            compact_buttons_frame,
            text="⟲",
            font=("Segoe UI", 8),
            fg=self.colors.get('bg_primary', '#1e1e2e'),
            bg=self.colors.get('orange', '#fab387'),
            relief='flat',
            width=3,
            command=self._reset_timer
        )
        self.compact_reset_button.pack(side='left')
        
        return self.compact_frame
    
    def create_expanded_widget(self, parent: tk.Widget) -> tk.Frame:
        """
        Create expanded timer widget for full mode.
        
        Args:
            parent: Parent widget
            
        Returns:
            tk.Frame: Expanded timer frame
        """
        self.expanded_frame = tk.Frame(parent, bg=self.colors.get('bg_primary', '#1e1e2e'))
        
        # Timer section header
        header_label = tk.Label(
            self.expanded_frame,
            text="Timer",
            font=("Segoe UI", 12, "bold"),
            fg=self.colors.get('text_primary', '#cdd6f4'),
            bg=self.colors.get('bg_primary', '#1e1e2e')
        )
        header_label.pack(fill='x', pady=(0, 5))
        
        # Main timer display
        timer_display_frame = tk.Frame(self.expanded_frame, bg=self.colors.get('bg_primary', '#1e1e2e'))
        timer_display_frame.pack(fill='x', pady=5)
        
        self.expanded_time_label = tk.Label(
            timer_display_frame,
            text="05:00",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors.get('text_primary', '#cdd6f4'),
            bg=self.colors.get('bg_primary', '#1e1e2e')
        )
        self.expanded_time_label.pack(side='left')
        
        # Main controls frame
        self.expanded_controls_frame = tk.Frame(timer_display_frame, bg=self.colors.get('bg_primary', '#1e1e2e'))
        self.expanded_controls_frame.pack(side='right', padx=(10, 0))
        
        # Play/Pause button
        self.play_pause_button = tk.Button(
            self.expanded_controls_frame,
            text="▶",
            font=("Segoe UI", 10),
            fg=self.colors.get('bg_primary', '#1e1e2e'),
            bg=self.colors.get('green', '#a6e3a1'),
            relief='flat',
            width=4,
            command=self._toggle_timer
        )
        self.play_pause_button.pack(side='left', padx=2)
        
        # Reset button
        self.reset_button = tk.Button(
            self.expanded_controls_frame,
            text="⟲",
            font=("Segoe UI", 10),
            fg=self.colors.get('bg_primary', '#1e1e2e'),
            bg=self.colors.get('orange', '#fab387'),
            relief='flat',
            width=4,
            command=self._reset_timer
        )
        self.reset_button.pack(side='left', padx=2)
        
        # Sound toggle button
        self.sound_button = tk.Button(
            self.expanded_controls_frame,
            text="🔊",
            font=("Segoe UI", 10),
            fg=self.colors.get('bg_primary', '#1e1e2e'),
            bg=self.colors.get('blue', '#89b4fa'),
            relief='flat',
            width=4,
            command=self._toggle_sound
        )
        self.sound_button.pack(side='left', padx=2)
        
        # Duration settings frame
        duration_frame = tk.Frame(self.expanded_frame, bg=self.colors.get('bg_primary', '#1e1e2e'))
        duration_frame.pack(fill='x', pady=5)
        
        # Duration label
        duration_label = tk.Label(
            duration_frame,
            text="Duration:",
            font=("Segoe UI", 9),
            fg=self.colors.get('text_secondary', '#94a3b8'),
            bg=self.colors.get('bg_primary', '#1e1e2e')
        )
        duration_label.pack(side='left')
        
        # Duration dropdown
        self.duration_combobox = ttk.Combobox(
            duration_frame,
            textvariable=self.duration_var,
            values=[str(i) for i in range(1, 31)],  # 1-30 minutes
            state='readonly',
            width=5,
            font=("Segoe UI", 9)
        )
        self.duration_combobox.pack(side='left', padx=(5, 10))
        self.duration_combobox.bind('<<ComboboxSelected>>', self._on_duration_change)
        
        # Preset buttons frame
        presets_frame = tk.Frame(duration_frame, bg=self.colors.get('bg_primary', '#1e1e2e'))
        presets_frame.pack(side='left')
        
        # Preset duration buttons
        preset_durations = [1, 3, 5, 10, 15, 30]
        for duration in preset_durations:
            btn = tk.Button(
                presets_frame,
                text=f"{duration}",
                font=("Segoe UI", 8),
                fg=self.colors.get('bg_primary', '#1e1e2e'),
                bg=self.colors.get('purple', '#cba6f7'),
                relief='flat',
                width=3,
                command=lambda d=duration: self._set_preset_duration(d)
            )
            btn.pack(side='left', padx=1)
        
        # Progress bar (optional visual element)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.expanded_frame,
            variable=self.progress_var,
            maximum=100,
            length=200,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', pady=(5, 0))
        
        return self.expanded_frame
    
    def _toggle_timer(self):
        """Toggle timer between start/pause states."""
        # Stop any repeating sound when starting/resuming timer
        if self.timer.is_completed():
            self.sound_manager.stop_repeating_sound()
        
        if self.timer.is_running():
            self.timer.pause()
        elif self.timer.is_paused():
            self.timer.resume()
        else:
            # Start fresh timer
            duration = int(self.duration_var.get())
            self.timer.set_duration(duration)
            self.timer.start()
    
    def _reset_timer(self):
        """Reset timer to initial state."""
        self.timer.reset()
        self._update_display()
    
    def _toggle_sound(self):
        """Toggle sound notifications on/off."""
        current_state = self.sound_manager.is_enabled()
        self.sound_manager.set_enabled(not current_state)
        self._update_sound_button()
    
    def _set_preset_duration(self, minutes: int):
        """Set timer duration to preset value."""
        if self.timer.is_stopped():
            self.duration_var.set(str(minutes))
            self.timer.set_duration(minutes)
            self._update_display()
    
    def _on_duration_change(self, event=None):
        """Handle duration selection change."""
        if self.timer.is_stopped():
            try:
                duration = int(self.duration_var.get())
                self.timer.set_duration(duration)
                self._update_display()
            except ValueError:
                pass
    
    def _on_timer_tick(self, minutes: int, seconds: int):
        """Handle timer tick callback."""
        self._update_display()
    
    def _on_timer_complete(self):
        """Handle timer completion callback."""
        # Start repeating completion sound
        if self.sound_manager.is_enabled():
            self.sound_manager.start_repeating_sound('timer_complete', self.parent)
        
        # Update display
        self._update_display()
        
        # Stop auto-updates
        self._stop_auto_update()
    
    def _on_timer_start(self):
        """Handle timer start callback."""
        self._update_controls()
        self._start_auto_update()
    
    def _on_timer_pause(self):
        """Handle timer pause callback."""
        self._update_controls()
        self._stop_auto_update()
    
    def _on_timer_resume(self):
        """Handle timer resume callback."""
        self._update_controls()
        self._start_auto_update()

    def _on_timer_reset(self):
        """Handle timer reset callback."""
        # Stop any repeating sound
        self.sound_manager.stop_repeating_sound()
        
        self._update_display()
        self._update_controls()
        self._stop_auto_update()
    
    def _update_display(self):
        """Update timer display elements."""
        time_display = self.timer.get_time_display()
        
        # Update compact display
        if self.compact_time_label:
            self.compact_time_label.config(text=time_display)
        
        # Update expanded display
        if self.expanded_time_label:
            self.expanded_time_label.config(text=time_display)
        
        # Update progress bar
        if hasattr(self, 'progress_var'):
            progress = self.timer.get_progress_percentage()
            self.progress_var.set(progress)
    
    def _update_controls(self):
        """Update control button states."""
        if self.timer.is_running():
            button_text = "⏸"
            button_color = self.colors.get('orange', '#fab387')
        elif self.timer.is_paused():
            button_text = "▶"
            button_color = self.colors.get('green', '#a6e3a1')
        else:
            button_text = "▶"
            button_color = self.colors.get('green', '#a6e3a1')
        
        # Update compact button
        if self.compact_control_button:
            self.compact_control_button.config(text=button_text, bg=button_color)
        
        # Update expanded button
        if hasattr(self, 'play_pause_button'):
            self.play_pause_button.config(text=button_text, bg=button_color)
    
    def _update_sound_button(self):
        """Update sound button appearance."""
        if hasattr(self, 'sound_button'):
            if self.sound_manager.is_enabled():
                self.sound_button.config(text="🔊", bg=self.colors.get('blue', '#89b4fa'))
            else:
                self.sound_button.config(text="🔇", bg=self.colors.get('red', '#f38ba8'))
    
    def _start_auto_update(self):
        """Start automatic timer updates."""
        if self.is_updating:
            return
        
        self.is_updating = True
        self._schedule_update()
    
    def _stop_auto_update(self):
        """Stop automatic timer updates."""
        self.is_updating = False
        if self.update_job_id:
            # Cancel scheduled update
            try:
                self.parent.after_cancel(self.update_job_id)
            except:
                pass
            self.update_job_id = None
    
    def _schedule_update(self):
        """Schedule next timer update."""
        if not self.is_updating:
            return
        
        # Update timer
        timer_active = self.timer.update()
        
        # Schedule next update if timer is still active
        if timer_active and self.is_updating:
            self.update_job_id = self.parent.after(1000, self._schedule_update)  # 1 second
        else:
            self.is_updating = False
            self.update_job_id = None
    
    def cleanup(self):
        """Clean up timer resources."""
        self._stop_auto_update()
        self.sound_manager.stop_repeating_sound()
        self.timer.reset()
    
    def get_timer_info(self) -> Dict[str, Any]:
        """Get current timer information."""
        return {
            'timer_state': self.timer.get_state_info(),
            'sound_enabled': self.sound_manager.is_enabled(),
            'sound_backend': self.sound_manager.get_backend_info()
        }
