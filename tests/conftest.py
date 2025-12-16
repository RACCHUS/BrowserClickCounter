"""
Shared pytest fixtures for BrowserClickCounter tests.
"""

import pytest  # type: ignore
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_windows_apis():
    """Mock Windows-specific APIs for cross-platform testing."""
    with patch('src.click_logic.win32gui') as mock_gui, \
         patch('src.click_logic.win32process') as mock_process, \
         patch('src.click_logic.psutil') as mock_psutil, \
         patch('src.click_logic.mouse') as mock_mouse:
        
        # Setup default mock behavior
        mock_gui.WindowFromPoint.return_value = 12345
        mock_gui.GetWindowText.return_value = "Chrome"
        mock_process.GetWindowThreadProcessId.return_value = (1, 1234)
        
        mock_proc = Mock()
        mock_proc.name.return_value = "chrome.exe"
        mock_psutil.Process.return_value = mock_proc
        
        yield {
            'win32gui': mock_gui,
            'win32process': mock_process,
            'psutil': mock_psutil,
            'mouse': mock_mouse
        }


@pytest.fixture
def tracker(mock_windows_apis):
    """Fresh ClickTracker with mocked Windows APIs."""
    from src.click_logic import ClickTracker
    t = ClickTracker()
    t._settings_dir = os.path.dirname(os.path.abspath(__file__))  # Use tests dir
    return t


@pytest.fixture
def region():
    """Standard test region."""
    return {'x1': 100, 'y1': 100, 'x2': 500, 'y2': 500}


@pytest.fixture
def small_region():
    """Small test region for boundary testing."""
    return {'x1': 0, 'y1': 0, 'x2': 10, 'y2': 10}


@pytest.fixture
def session_timer():
    """Fresh SessionTimer instance."""
    from src.timer.timer import SessionTimer
    return SessionTimer()


@pytest.fixture
def countdown_timer():
    """Fresh CountdownTimer instance."""
    from src.timer.timer import CountdownTimer
    return CountdownTimer(default_duration_minutes=5)
