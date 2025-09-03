from datetime import datetime
import time
from typing import Optional, Callable, Dict, Tuple
from enum import Enum


class TimerState(Enum):
    """Timer state enumeration."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class SessionTimer:
    """Simple session timer to keep GUI code concise.

    Responsibilities:
    - start()/pause()/resume()/stop() session timing
    - return elapsed seconds (excluding paused time)
    - format as HH:MM:SS for display
    """
    def __init__(self):
        self.start_time = None
        self.paused_time = None
        self.total_paused_duration = 0

    def start(self):
        if self.start_time is None:
            self.start_time = datetime.now()
            self.total_paused_duration = 0

    def pause(self):
        if self.start_time and not self.paused_time:
            self.paused_time = datetime.now()

    def resume(self):
        if self.paused_time:
            pause_duration = (datetime.now() - self.paused_time).total_seconds()
            self.total_paused_duration += pause_duration
            self.paused_time = None

    def stop(self):
        self.start_time = None
        self.paused_time = None
        self.total_paused_duration = 0

    def reset(self):
        self.start_time = None
        self.paused_time = None
        self.total_paused_duration = 0

    def is_paused(self):
        return self.paused_time is not None

    def elapsed_seconds(self):
        if not self.start_time:
            return 0
        
        current_time = datetime.now()
        total_elapsed = (current_time - self.start_time).total_seconds()
        
        # Subtract total paused duration
        active_elapsed = total_elapsed - self.total_paused_duration
        
        # If currently paused, subtract the current pause duration
        if self.paused_time:
            current_pause_duration = (current_time - self.paused_time).total_seconds()
            active_elapsed -= current_pause_duration
            
        return max(0, int(active_elapsed))

    def format_hms(self):
        secs = self.elapsed_seconds()
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"


class CountdownTimer:
    """
    A countdown timer with configurable duration and callback system.
    Provides accurate timing with pause/resume functionality.
    """
    
    def __init__(self, default_duration_minutes: int = 5):
        """Initialize timer with default duration."""
        self.default_duration_minutes = default_duration_minutes
        self.duration_minutes = default_duration_minutes
        self.duration_seconds = default_duration_minutes * 60
        
        # Timer state
        self.state = TimerState.STOPPED
        self.remaining_seconds = self.duration_seconds
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.elapsed_when_paused = 0.0
        
        # Callback system
        self.callbacks: Dict[str, Optional[Callable]] = {
            'on_tick': None,          # Called every second with remaining time
            'on_complete': None,      # Called when timer reaches zero
            'on_start': None,         # Called when timer starts
            'on_pause': None,         # Called when timer pauses
            'on_resume': None,        # Called when timer resumes
            'on_reset': None,         # Called when timer resets
            'on_duration_change': None # Called when duration changes
        }
        
        # Update tracking
        self.last_update_time: Optional[float] = None
        self.update_interval = 1.0  # Update every second
    
    def set_duration(self, minutes: int) -> bool:
        """
        Set timer duration in minutes.
        
        Args:
            minutes: Duration in minutes (1-60)
            
        Returns:
            bool: True if duration was set successfully
        """
        if not isinstance(minutes, int) or minutes < 1 or minutes > 60:
            return False
        
        # Only allow duration change when timer is stopped
        if self.state != TimerState.STOPPED:
            return False
        
        self.duration_minutes = minutes
        self.duration_seconds = minutes * 60
        self.remaining_seconds = self.duration_seconds
        
        # Trigger callback
        if self.callbacks['on_duration_change']:
            try:
                self.callbacks['on_duration_change'](minutes)
            except Exception:
                pass  # Silently handle callback errors
        
        return True
    
    def start(self) -> bool:
        """
        Start the timer.
        
        Returns:
            bool: True if timer was started successfully
        """
        if self.state == TimerState.RUNNING:
            return False  # Already running
        
        current_time = time.time()
        
        if self.state == TimerState.PAUSED:
            # Resume from pause
            self.start_time = current_time - self.elapsed_when_paused
            self.pause_time = None
            self.state = TimerState.RUNNING
            
            # Trigger resume callback
            if self.callbacks['on_resume']:
                try:
                    self.callbacks['on_resume']()
                except Exception:
                    pass
        else:
            # Fresh start
            self.start_time = current_time
            self.elapsed_when_paused = 0.0
            self.remaining_seconds = self.duration_seconds
            self.state = TimerState.RUNNING
            
            # Trigger start callback
            if self.callbacks['on_start']:
                try:
                    self.callbacks['on_start']()
                except Exception:
                    pass
        
        self.last_update_time = current_time
        return True
    
    def pause(self) -> bool:
        """
        Pause the timer.
        
        Returns:
            bool: True if timer was paused successfully
        """
        if self.state != TimerState.RUNNING:
            return False
        
        current_time = time.time()
        self.pause_time = current_time
        
        if self.start_time:
            self.elapsed_when_paused = current_time - self.start_time
        
        self.state = TimerState.PAUSED
        
        # Trigger pause callback
        if self.callbacks['on_pause']:
            try:
                self.callbacks['on_pause']()
            except Exception:
                pass
        
        return True
    
    def resume(self) -> bool:
        """Resume the timer from pause."""
        return self.start()
    
    def reset(self) -> bool:
        """
        Reset the timer to initial state.
        
        Returns:
            bool: True if timer was reset successfully
        """
        self.state = TimerState.STOPPED
        self.remaining_seconds = self.duration_seconds
        self.start_time = None
        self.pause_time = None
        self.elapsed_when_paused = 0.0
        self.last_update_time = None
        
        # Trigger reset callback
        if self.callbacks['on_reset']:
            try:
                self.callbacks['on_reset']()
            except Exception:
                pass
        
        return True
    
    def update(self) -> bool:
        """
        Update timer state. Should be called regularly (every second).
        
        Returns:
            bool: True if timer is still active, False if completed
        """
        if self.state != TimerState.RUNNING:
            return self.state != TimerState.COMPLETED
        
        current_time = time.time()
        
        # Check if enough time has passed for an update
        if (self.last_update_time and 
            current_time - self.last_update_time < self.update_interval):
            return True
        
        if not self.start_time:
            return True
        
        # Calculate elapsed time
        elapsed = current_time - self.start_time
        self.remaining_seconds = max(0, self.duration_seconds - elapsed)
        
        # Check if timer completed
        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0
            self.state = TimerState.COMPLETED
            
            # Trigger completion callback
            if self.callbacks['on_complete']:
                try:
                    self.callbacks['on_complete']()
                except Exception:
                    pass
            
            return False
        
        # Trigger tick callback
        if self.callbacks['on_tick']:
            try:
                minutes, seconds = self.get_remaining_time()
                self.callbacks['on_tick'](minutes, seconds)
            except Exception:
                pass
        
        self.last_update_time = current_time
        return True
    
    def get_remaining_time(self) -> Tuple[int, int]:
        """
        Get remaining time as (minutes, seconds).
        
        Returns:
            Tuple[int, int]: (minutes, seconds) remaining
        """
        total_seconds = int(self.remaining_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return minutes, seconds
    
    def get_progress_percentage(self) -> float:
        """
        Get timer progress as percentage (0.0 to 100.0).
        
        Returns:
            float: Progress percentage
        """
        if self.duration_seconds == 0:
            return 100.0
        
        elapsed_seconds = self.duration_seconds - self.remaining_seconds
        return min(100.0, (elapsed_seconds / self.duration_seconds) * 100.0)
    
    def get_time_display(self) -> str:
        """
        Get formatted time display string (MM:SS).
        
        Returns:
            str: Formatted time string
        """
        minutes, seconds = self.get_remaining_time()
        return f"{minutes:02d}:{seconds:02d}"
    
    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self.state == TimerState.RUNNING
    
    def is_paused(self) -> bool:
        """Check if timer is currently paused."""
        return self.state == TimerState.PAUSED
    
    def is_stopped(self) -> bool:
        """Check if timer is stopped."""
        return self.state == TimerState.STOPPED
    
    def is_completed(self) -> bool:
        """Check if timer has completed."""
        return self.state == TimerState.COMPLETED
    
    def set_callback(self, event: str, callback: Optional[Callable]) -> bool:
        """
        Set callback for timer events.
        
        Args:
            event: Event name ('on_tick', 'on_complete', etc.)
            callback: Callback function
            
        Returns:
            bool: True if callback was set successfully
        """
        if event not in self.callbacks:
            return False
        
        self.callbacks[event] = callback
        return True
    
    def get_state_info(self) -> Dict:
        """
        Get comprehensive timer state information.
        
        Returns:
            Dict: Timer state information
        """
        minutes, seconds = self.get_remaining_time()
        
        return {
            'state': self.state.value,
            'duration_minutes': self.duration_minutes,
            'remaining_minutes': minutes,
            'remaining_seconds': seconds,
            'total_remaining_seconds': self.remaining_seconds,
            'progress_percentage': self.get_progress_percentage(),
            'time_display': self.get_time_display(),
            'is_running': self.is_running(),
            'is_paused': self.is_paused(),
            'is_stopped': self.is_stopped(),
            'is_completed': self.is_completed()
        }
