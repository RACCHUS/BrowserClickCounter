"""
Tests for celebration milestone detection.
Note: Visual celebration tests are in demos/test_celebrations_visual.py
"""

import pytest  # type: ignore
from unittest.mock import Mock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMilestoneDetectionIntegration:
    """Tests for milestone detection through ClickTracker."""

    def test_minor_milestone_at_100(self, tracker, region):
        """100 clicks triggers minor milestone."""
        tracker.add_region(region)
        tracker.count = 99
        
        counted, milestone = tracker._count_if_in_regions(300, 300)
        
        assert milestone == "minor"

    def test_major_milestone_at_1000(self, tracker, region):
        """1000 clicks triggers major milestone."""
        tracker.add_region(region)
        tracker.count = 999
        
        counted, milestone = tracker._count_if_in_regions(300, 300)
        
        assert milestone == "major"

    def test_no_milestone_at_50(self, tracker, region):
        """50 clicks triggers no milestone."""
        tracker.add_region(region)
        tracker.count = 49
        
        counted, milestone = tracker._count_if_in_regions(300, 300)
        
        assert milestone is None

    def test_milestone_callback_integration(self, tracker, region):
        """Milestone callback is called via handle_click."""
        tracker.add_region(region)
        tracker.count = 99
        tracker.browser_detection = False
        
        callback = Mock()
        
        # Create a mock button that will match mouse.Button.left
        mock_button = Mock(name='left_button')
        
        # Patch mouse.Button.left to return our mock
        with patch('src.click_logic.mouse.Button') as mock_mouse_button:
            mock_mouse_button.left = mock_button
            tracker.handle_click(300, 300, mock_button, True, on_counted=callback)
        
        callback.assert_called_once_with("minor")


class TestMilestoneValues:
    """Tests for specific milestone value checks."""

    @pytest.mark.parametrize("count,expected", [
        (100, "minor"),
        (200, "minor"),
        (300, "minor"),
        (400, "minor"),
        (500, "minor"),
        (600, "minor"),
        (700, "minor"),
        (800, "minor"),
        (900, "minor"),
    ])
    def test_minor_milestones(self, tracker, count, expected):
        """All 100-interval milestones (except 1000s) are minor."""
        assert tracker._check_milestone(count) == expected

    @pytest.mark.parametrize("count,expected", [
        (1000, "major"),
        (2000, "major"),
        (3000, "major"),
        (5000, "major"),
        (10000, "major"),
    ])
    def test_major_milestones(self, tracker, count, expected):
        """All 1000-interval milestones are major."""
        assert tracker._check_milestone(count) == expected

    @pytest.mark.parametrize("count", [
        1, 50, 99, 101, 150, 199, 999, 1001, 1050
    ])
    def test_non_milestones(self, tracker, count):
        """Non-milestone counts return None."""
        assert tracker._check_milestone(count) is None


class TestCelebrationManagerUnit:
    """Unit tests for CelebrationManager (without GUI)."""

    def test_celebration_manager_init(self):
        """CelebrationManager initializes with GUI reference."""
        mock_gui = Mock()
        mock_gui.main_frame = Mock()
        mock_gui.count_label = Mock()
        
        from src.celebration.celebration import CelebrationManager
        manager = CelebrationManager(mock_gui)
        
        assert manager.gui == mock_gui
        assert manager.active_effects == []

    def test_celebration_manager_has_colors(self):
        """CelebrationManager has color definitions."""
        mock_gui = Mock()
        
        from src.celebration.celebration import CelebrationManager
        manager = CelebrationManager(mock_gui)
        
        assert 'success' in manager.colors
        assert 'celebration_gold' in manager.colors
