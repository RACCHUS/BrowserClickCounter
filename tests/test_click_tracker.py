"""
Tests for ClickTracker core logic.
"""

import pytest  # type: ignore
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestRegionManagement:
    """Tests for region add/clear/status functionality."""

    def test_add_region(self, tracker, region):
        """Adding region increases count and sets last_region."""
        tracker.add_region(region)
        
        assert len(tracker.regions) == 1
        assert tracker.regions[0] == region
        assert tracker.last_region == region

    def test_add_multiple_regions(self, tracker, region, small_region):
        """Multiple regions can be tracked."""
        tracker.add_region(region)
        tracker.add_region(small_region)
        
        assert len(tracker.regions) == 2
        assert tracker.last_region == small_region  # Last added

    def test_clear_regions(self, tracker, region):
        """Clearing removes all regions and last_region."""
        tracker.add_region(region)
        tracker.clear_regions()
        
        assert len(tracker.regions) == 0
        assert tracker.last_region is None

    def test_get_region_status_no_regions(self, tracker):
        """Returns 'No regions set' when empty."""
        status = tracker.get_region_status()
        assert status == "No regions set"

    def test_get_region_status_single_region(self, tracker, region):
        """Returns dimensions and position for single region."""
        tracker.add_region(region)
        status = tracker.get_region_status()
        
        # Region is 400x400 at (100,100)
        assert "400×400" in status
        assert "(100,100)" in status

    def test_get_region_status_multiple_regions(self, tracker, region, small_region):
        """Returns count for multiple regions."""
        tracker.add_region(region)
        tracker.add_region(small_region)
        status = tracker.get_region_status()
        
        assert "2 regions set" in status


class TestClickCounting:
    """Tests for click detection and counting."""

    def test_count_click_inside_region(self, tracker, region):
        """Click inside region increments count."""
        tracker.add_region(region)
        
        # Click at center of region (300, 300)
        counted, milestone = tracker._count_if_in_regions(300, 300)
        
        assert counted is True
        assert tracker.count == 1

    def test_count_click_outside_region(self, tracker, region):
        """Click outside region does not increment."""
        tracker.add_region(region)
        
        # Click outside region (50, 50)
        counted, milestone = tracker._count_if_in_regions(50, 50)
        
        assert counted is False
        assert tracker.count == 0

    def test_count_click_on_region_boundary(self, tracker, region):
        """Click on exact boundary is counted (inclusive)."""
        tracker.add_region(region)
        
        # Click on boundaries
        assert tracker._count_if_in_regions(100, 100)[0] is True  # Top-left
        assert tracker._count_if_in_regions(500, 500)[0] is True  # Bottom-right
        assert tracker._count_if_in_regions(100, 300)[0] is True  # Left edge
        assert tracker._count_if_in_regions(500, 300)[0] is True  # Right edge

    def test_count_click_just_outside_boundary(self, tracker, region):
        """Click just outside boundary is not counted."""
        tracker.add_region(region)
        
        assert tracker._count_if_in_regions(99, 300)[0] is False   # Just left
        assert tracker._count_if_in_regions(501, 300)[0] is False  # Just right
        assert tracker._count_if_in_regions(300, 99)[0] is False   # Just above
        assert tracker._count_if_in_regions(300, 501)[0] is False  # Just below

    def test_count_click_multiple_regions(self, tracker, region, small_region):
        """Click in any of multiple regions increments once."""
        tracker.add_region(region)
        tracker.add_region(small_region)
        
        # Click in first region
        tracker._count_if_in_regions(300, 300)
        assert tracker.count == 1
        
        # Click in second region
        tracker._count_if_in_regions(5, 5)
        assert tracker.count == 2

    def test_paused_ignores_clicks(self, tracker, region):
        """Clicks ignored when is_paused=True."""
        tracker.add_region(region)
        tracker.is_paused = True
        
        # Use handle_click which checks is_paused
        tracker.handle_click(300, 300, Mock(name='left'), True)
        
        assert tracker.count == 0

    def test_click_times_tracked(self, tracker, region):
        """Click times are recorded for rate calculation."""
        tracker.add_region(region)
        
        tracker._count_if_in_regions(300, 300)
        tracker._count_if_in_regions(300, 300)
        
        assert len(tracker.click_times) == 2
        assert all(isinstance(t, datetime) for t in tracker.click_times)


class TestMilestoneDetection:
    """Tests for milestone achievement detection."""

    def test_milestone_at_100(self, tracker):
        """Returns 'minor' at 100 clicks."""
        milestone = tracker._check_milestone(100)
        assert milestone == "minor"

    def test_milestone_at_200(self, tracker):
        """Returns 'minor' at 200 clicks."""
        milestone = tracker._check_milestone(200)
        assert milestone == "minor"

    def test_milestone_at_500(self, tracker):
        """Returns 'minor' at 500 (not major)."""
        milestone = tracker._check_milestone(500)
        assert milestone == "minor"

    def test_milestone_at_1000(self, tracker):
        """Returns 'major' at 1000 clicks."""
        milestone = tracker._check_milestone(1000)
        assert milestone == "major"

    def test_milestone_at_2000(self, tracker):
        """Returns 'major' at 2000."""
        milestone = tracker._check_milestone(2000)
        assert milestone == "major"

    def test_no_milestone_at_99(self, tracker):
        """Returns None at non-milestone counts."""
        milestone = tracker._check_milestone(99)
        assert milestone is None

    def test_no_milestone_at_101(self, tracker):
        """Returns None at non-milestone counts."""
        milestone = tracker._check_milestone(101)
        assert milestone is None

    def test_no_milestone_at_0(self, tracker):
        """Returns None at zero."""
        milestone = tracker._check_milestone(0)
        assert milestone is None

    def test_milestone_callback_called(self, tracker, region):
        """Milestone is returned when click reaches milestone."""
        tracker.add_region(region)
        tracker.count = 99  # Set to one before milestone
        
        counted, milestone = tracker._count_if_in_regions(300, 300)
        
        assert counted is True
        assert milestone == "minor"
        assert tracker.count == 100


class TestStatistics:
    """Tests for statistics calculations."""

    def test_clicks_last_hour_filters_old(self, tracker):
        """Only counts clicks within last hour."""
        now = datetime.now()
        
        # Add clicks from different times
        tracker.click_times = [
            now - timedelta(hours=2),   # Old, should be excluded
            now - timedelta(minutes=30), # Recent, should be included
            now - timedelta(minutes=5),  # Recent, should be included
        ]
        
        count = tracker.clicks_last_hour()
        assert count == 2

    def test_clicks_last_hour_empty(self, tracker):
        """Returns 0 when no clicks."""
        count = tracker.clicks_last_hour()
        assert count == 0

    def test_session_seconds_calculation(self, tracker):
        """Returns correct elapsed time."""
        tracker.start_time = datetime.now() - timedelta(seconds=120)
        
        seconds = tracker.session_seconds()
        
        # Allow 1 second tolerance for test execution time
        assert 119 <= seconds <= 121

    def test_session_seconds_not_started(self, tracker):
        """Returns 0 when session not started."""
        assert tracker.session_seconds() == 0

    def test_reset_session_clears_state(self, tracker, region):
        """Reset clears count, click_times, start_time."""
        tracker.add_region(region)
        tracker.count = 50
        tracker.click_times = [datetime.now()]
        tracker.start_time = datetime.now()
        
        tracker.reset_session()
        
        assert tracker.count == 0
        assert tracker.click_times == []
        assert tracker.start_time is None
        # Regions should NOT be cleared
        assert len(tracker.regions) == 1


class TestBrowserDetection:
    """Tests for browser window detection."""

    def test_browser_detection_disabled_always_true(self, tracker):
        """When browser_detection=False, always returns True."""
        tracker.browser_detection = False
        
        result = tracker._is_browser_window(300, 300)
        assert result is True

    def test_browser_detection_enabled_checks_process(self, tracker, mock_windows_apis):
        """When browser_detection=True, checks process name."""
        tracker.browser_detection = True
        
        # Mock is configured to return chrome.exe
        result = tracker._is_browser_window(300, 300)
        assert result is True
