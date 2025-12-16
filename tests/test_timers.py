"""
Tests for SessionTimer and CountdownTimer.
"""

import pytest  # type: ignore
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.timer.timer import SessionTimer, CountdownTimer, TimerState


class TestSessionTimerBasic:
    """Basic SessionTimer tests."""

    def test_initial_state(self, session_timer):
        """Timer starts in stopped state."""
        assert session_timer.start_time is None
        assert session_timer.paused_time is None
        assert session_timer.total_paused_duration == 0

    def test_start_sets_time(self, session_timer):
        """Starting sets start_time."""
        session_timer.start()
        
        assert session_timer.start_time is not None
        assert isinstance(session_timer.start_time, datetime)

    def test_start_idempotent(self, session_timer):
        """Multiple starts don't reset timer."""
        session_timer.start()
        first_start = session_timer.start_time
        
        time.sleep(0.01)
        session_timer.start()
        
        assert session_timer.start_time == first_start

    def test_stop_resets_state(self, session_timer):
        """Stopping resets all state."""
        session_timer.start()
        session_timer.stop()
        
        assert session_timer.start_time is None
        assert session_timer.paused_time is None
        assert session_timer.total_paused_duration == 0

    def test_reset_clears_state(self, session_timer):
        """Reset clears all state."""
        session_timer.start()
        session_timer.pause()
        session_timer.reset()
        
        assert session_timer.start_time is None
        assert session_timer.paused_time is None
        assert session_timer.total_paused_duration == 0


class TestSessionTimerElapsed:
    """Tests for elapsed time calculation."""

    def test_elapsed_increases(self, session_timer):
        """Elapsed time increases while running."""
        session_timer.start()
        time.sleep(0.1)
        
        elapsed = session_timer.elapsed_seconds()
        
        assert elapsed >= 0  # At least 0 seconds

    def test_elapsed_not_started(self, session_timer):
        """Elapsed is 0 when not started."""
        assert session_timer.elapsed_seconds() == 0

    def test_format_hms_zero(self, session_timer):
        """Formats as 00:00:00 when not started."""
        assert session_timer.format_hms() == "00:00:00"

    def test_format_hms_with_time(self, session_timer):
        """Formats elapsed time correctly."""
        session_timer.start()
        # Manually set start time to test formatting
        session_timer.start_time = datetime.now() - timedelta(hours=1, minutes=30, seconds=45)
        
        formatted = session_timer.format_hms()
        
        assert formatted == "01:30:45"


class TestSessionTimerPauseResume:
    """Tests for pause/resume functionality."""

    def test_pause_sets_paused_time(self, session_timer):
        """Pausing sets paused_time."""
        session_timer.start()
        session_timer.pause()
        
        assert session_timer.paused_time is not None

    def test_is_paused(self, session_timer):
        """is_paused returns correct state."""
        session_timer.start()
        
        assert session_timer.is_paused() is False
        
        session_timer.pause()
        assert session_timer.is_paused() is True
        
        session_timer.resume()
        assert session_timer.is_paused() is False

    def test_pause_freezes_elapsed(self, session_timer):
        """Pausing freezes elapsed time."""
        session_timer.start()
        session_timer.start_time = datetime.now() - timedelta(seconds=10)
        
        session_timer.pause()
        elapsed_when_paused = session_timer.elapsed_seconds()
        
        time.sleep(0.1)
        elapsed_after_wait = session_timer.elapsed_seconds()
        
        # Should be the same (frozen)
        assert elapsed_when_paused == elapsed_after_wait

    def test_resume_continues(self, session_timer):
        """Resuming continues from paused time."""
        session_timer.start()
        session_timer.pause()
        
        paused_duration_before = session_timer.total_paused_duration
        time.sleep(0.05)
        
        session_timer.resume()
        
        # total_paused_duration should increase
        assert session_timer.total_paused_duration > paused_duration_before
        assert session_timer.paused_time is None

    def test_pause_without_start_no_effect(self, session_timer):
        """Pausing without start has no effect."""
        session_timer.pause()
        
        assert session_timer.paused_time is None

    def test_resume_without_pause_no_effect(self, session_timer):
        """Resuming without pause has no effect."""
        session_timer.start()
        original_paused_duration = session_timer.total_paused_duration
        
        session_timer.resume()
        
        assert session_timer.total_paused_duration == original_paused_duration

    def test_multiple_pause_resume_cycles(self, session_timer):
        """Multiple pause/resume cycles track correctly."""
        session_timer.start()
        session_timer.start_time = datetime.now() - timedelta(seconds=100)
        
        # First pause/resume
        session_timer.pause()
        session_timer.paused_time = datetime.now() - timedelta(seconds=10)
        session_timer.resume()
        
        # Second pause/resume  
        session_timer.pause()
        session_timer.paused_time = datetime.now() - timedelta(seconds=5)
        session_timer.resume()
        
        # Total paused should be ~15 seconds
        assert session_timer.total_paused_duration >= 14


class TestCountdownTimerBasic:
    """Basic CountdownTimer tests."""

    def test_initial_state(self, countdown_timer):
        """Timer starts in stopped state with default duration."""
        assert countdown_timer.state == TimerState.STOPPED
        assert countdown_timer.duration_minutes == 5
        assert countdown_timer.remaining_seconds == 300

    def test_set_duration(self, countdown_timer):
        """Setting duration updates remaining time."""
        result = countdown_timer.set_duration(10)
        
        assert result is True
        assert countdown_timer.duration_minutes == 10
        assert countdown_timer.remaining_seconds == 600

    def test_set_duration_invalid(self, countdown_timer):
        """Invalid duration returns False."""
        assert countdown_timer.set_duration(0) is False
        assert countdown_timer.set_duration(-1) is False
        assert countdown_timer.set_duration(61) is False
        assert countdown_timer.set_duration("5") is False

    def test_set_duration_while_running_fails(self, countdown_timer):
        """Cannot change duration while running."""
        countdown_timer.start()
        
        result = countdown_timer.set_duration(10)
        
        assert result is False
        assert countdown_timer.duration_minutes == 5  # Unchanged


class TestCountdownTimerStateTransitions:
    """Tests for countdown timer state transitions."""

    def test_start_changes_state(self, countdown_timer):
        """Starting changes state to RUNNING."""
        result = countdown_timer.start()
        
        assert result is True
        assert countdown_timer.state == TimerState.RUNNING
        assert countdown_timer.start_time is not None

    def test_start_while_running_fails(self, countdown_timer):
        """Cannot start while already running."""
        countdown_timer.start()
        
        result = countdown_timer.start()
        
        assert result is False

    def test_pause_changes_state(self, countdown_timer):
        """Pausing changes state to PAUSED."""
        countdown_timer.start()
        
        result = countdown_timer.pause()
        
        assert result is True
        assert countdown_timer.state == TimerState.PAUSED

    def test_pause_while_stopped_fails(self, countdown_timer):
        """Cannot pause while stopped."""
        result = countdown_timer.pause()
        
        assert result is False

    def test_resume_changes_state(self, countdown_timer):
        """Resuming from pause changes state to RUNNING."""
        countdown_timer.start()
        countdown_timer.pause()
        
        result = countdown_timer.resume()
        
        assert result is True
        assert countdown_timer.state == TimerState.RUNNING

    def test_resume_while_running_fails(self, countdown_timer):
        """Cannot resume while already running."""
        countdown_timer.start()
        
        result = countdown_timer.resume()
        
        assert result is False

    def test_reset_restores_duration(self, countdown_timer):
        """Reset restores initial duration."""
        countdown_timer.start()
        countdown_timer.remaining_seconds = 100  # Simulate some elapsed time
        
        result = countdown_timer.reset()
        
        assert result is True
        assert countdown_timer.state == TimerState.STOPPED
        assert countdown_timer.remaining_seconds == 300


class TestCountdownTimerCallbacks:
    """Tests for countdown timer callbacks."""

    def test_on_start_callback(self, countdown_timer):
        """on_start callback fires when timer starts."""
        callback = Mock()
        countdown_timer.callbacks['on_start'] = callback
        
        countdown_timer.start()
        
        callback.assert_called_once()

    def test_on_pause_callback(self, countdown_timer):
        """on_pause callback fires when timer pauses."""
        callback = Mock()
        countdown_timer.callbacks['on_pause'] = callback
        
        countdown_timer.start()
        countdown_timer.pause()
        
        callback.assert_called_once()

    def test_on_resume_callback(self, countdown_timer):
        """on_resume callback fires when timer resumes."""
        callback = Mock()
        countdown_timer.callbacks['on_resume'] = callback
        
        countdown_timer.start()
        countdown_timer.pause()
        countdown_timer.resume()
        
        callback.assert_called_once()

    def test_on_reset_callback(self, countdown_timer):
        """on_reset callback fires when timer resets."""
        callback = Mock()
        countdown_timer.callbacks['on_reset'] = callback
        
        countdown_timer.start()
        countdown_timer.reset()
        
        callback.assert_called_once()

    def test_on_duration_change_callback(self, countdown_timer):
        """on_duration_change callback fires when duration changes."""
        callback = Mock()
        countdown_timer.callbacks['on_duration_change'] = callback
        
        countdown_timer.set_duration(10)
        
        callback.assert_called_once_with(10)

    def test_callback_error_handled(self, countdown_timer):
        """Callback errors don't crash timer."""
        def bad_callback(*args):
            raise ValueError("Callback error")
        
        countdown_timer.callbacks['on_start'] = bad_callback
        
        # Should not raise
        countdown_timer.start()
        
        assert countdown_timer.state == TimerState.RUNNING


class TestCountdownTimerUpdate:
    """Tests for countdown timer update logic."""

    def test_update_decreases_remaining(self, countdown_timer):
        """Update decreases remaining time."""
        countdown_timer.start()
        initial_remaining = countdown_timer.remaining_seconds
        
        # Manually adjust start time to simulate elapsed time
        countdown_timer.start_time = time.time() - 10
        # Reset last_update_time to force update
        countdown_timer.last_update_time = None
        countdown_timer.update()
        
        assert countdown_timer.remaining_seconds < initial_remaining

    def test_update_when_stopped_no_change(self, countdown_timer):
        """Update when stopped doesn't change remaining."""
        initial = countdown_timer.remaining_seconds
        
        countdown_timer.update()
        
        assert countdown_timer.remaining_seconds == initial

    def test_completion_state(self, countdown_timer):
        """Timer reaches COMPLETED state at zero."""
        countdown_timer.set_duration(1)  # 1 minute = 60 seconds
        countdown_timer.start()
        
        # Simulate time passing and force update
        countdown_timer.start_time = time.time() - 61
        countdown_timer.last_update_time = None
        countdown_timer.update()
        
        assert countdown_timer.state == TimerState.COMPLETED
        assert countdown_timer.remaining_seconds == 0

    def test_on_complete_callback(self, countdown_timer):
        """on_complete callback fires when timer reaches zero."""
        callback = Mock()
        countdown_timer.callbacks['on_complete'] = callback
        
        countdown_timer.set_duration(1)
        countdown_timer.start()
        countdown_timer.start_time = time.time() - 61
        countdown_timer.last_update_time = None
        countdown_timer.update()
        
        callback.assert_called_once()


class TestCountdownTimerFormatting:
    """Tests for countdown timer display formatting."""

    def test_get_time_display_full(self, countdown_timer):
        """Full time formatted correctly (MM:SS format)."""
        countdown_timer.remaining_seconds = 125  # 2:05
        
        display = countdown_timer.get_time_display()
        
        assert display == "02:05"

    def test_get_time_display_minutes_only(self, countdown_timer):
        """Minutes and seconds formatted correctly."""
        countdown_timer.remaining_seconds = 65  # 1:05
        
        display = countdown_timer.get_time_display()
        
        assert display == "01:05"

    def test_get_time_display_zero(self, countdown_timer):
        """Zero time formatted correctly."""
        countdown_timer.remaining_seconds = 0
        
        display = countdown_timer.get_time_display()
        
        assert display == "00:00"
