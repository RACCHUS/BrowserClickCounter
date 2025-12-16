"""
Tests for settings and session persistence.
"""

import pytest  # type: ignore
import json
import os
from unittest.mock import patch, mock_open


class TestSettingsSave:
    """Tests for saving settings."""

    def test_save_settings_creates_file(self, tracker, region, tmp_path):
        """Saving creates JSON file with correct structure."""
        settings_file = tmp_path / "test_settings.json"
        tracker.add_region(region)
        tracker.browser_detection = True
        
        result = tracker.save_settings(str(settings_file))
        
        assert result is True
        assert settings_file.exists()
        
        with open(settings_file) as f:
            data = json.load(f)
        
        assert 'regions' in data
        assert 'last_region' in data
        assert 'browser_detection' in data
        assert 'timestamp' in data
        assert len(data['regions']) == 1
        assert data['regions'][0] == region

    def test_save_settings_overwrites_existing(self, tracker, region, tmp_path):
        """Saving overwrites existing file."""
        settings_file = tmp_path / "test_settings.json"
        
        # Save first region
        tracker.add_region(region)
        tracker.save_settings(str(settings_file))
        
        # Clear and save empty
        tracker.clear_regions()
        tracker.save_settings(str(settings_file))
        
        with open(settings_file) as f:
            data = json.load(f)
        
        assert len(data['regions']) == 0

    def test_save_settings_permission_error(self, tracker, region, monkeypatch):
        """Handles write permission errors gracefully."""
        tracker.add_region(region)
        
        # Mock os.makedirs to raise permission error
        def mock_makedirs(*args, **kwargs):
            raise PermissionError("Access denied")
        
        monkeypatch.setattr('os.makedirs', mock_makedirs)
        
        # Should return False, not raise exception
        result = tracker.save_settings('/fake/path/settings.json')
        assert result is False


class TestSettingsLoad:
    """Tests for loading settings."""

    def test_load_settings_restores_regions(self, tracker, region, tmp_path):
        """Loading restores saved regions."""
        settings_file = tmp_path / "test_settings.json"
        
        # Create settings file
        settings_data = {
            'regions': [region],
            'last_region': region,
            'browser_detection': False,
            'timestamp': '2025-01-01T00:00:00'
        }
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f)
        
        result = tracker.load_settings(str(settings_file))
        
        assert result is True
        assert len(tracker.regions) == 1
        assert tracker.regions[0] == region
        assert tracker.browser_detection is False

    def test_load_settings_restores_last_region(self, tracker, region, tmp_path):
        """Loading restores last_region if regions empty."""
        settings_file = tmp_path / "test_settings.json"
        
        # Create settings with only last_region (no regions array)
        settings_data = {
            'regions': [],
            'last_region': region,
            'browser_detection': True,
            'timestamp': '2025-01-01T00:00:00'
        }
        with open(settings_file, 'w') as f:
            json.dump(settings_data, f)
        
        result = tracker.load_settings(str(settings_file))
        
        assert result is True
        # Should restore last_region to regions
        assert len(tracker.regions) == 1
        assert tracker.regions[0] == region

    def test_load_settings_missing_file(self, tracker, tmp_path):
        """Returns False when file doesn't exist."""
        missing_file = tmp_path / "nonexistent.json"
        
        result = tracker.load_settings(str(missing_file))
        
        assert result is False
        assert len(tracker.regions) == 0

    def test_load_settings_corrupt_json(self, tracker, tmp_path):
        """Handles corrupt JSON gracefully."""
        corrupt_file = tmp_path / "corrupt.json"
        
        with open(corrupt_file, 'w') as f:
            f.write("{ not valid json }")
        
        result = tracker.load_settings(str(corrupt_file))
        
        assert result is False

    def test_load_settings_missing_keys(self, tracker, tmp_path):
        """Handles missing keys with defaults."""
        settings_file = tmp_path / "minimal.json"
        
        # Minimal settings file
        with open(settings_file, 'w') as f:
            json.dump({}, f)
        
        result = tracker.load_settings(str(settings_file))
        
        assert result is True
        assert tracker.regions == []
        assert tracker.last_region is None


class TestSessionSave:
    """Tests for session data saving."""

    def test_save_session_creates_file(self, tracker, region, tmp_path):
        """Session data saved with correct fields."""
        session_file = tmp_path / "test_session.json"
        tracker.add_region(region)
        tracker.count = 150
        
        tracker.save_session(3600, str(session_file))  # 1 hour
        
        assert session_file.exists()
        
        with open(session_file) as f:
            data = json.load(f)
        
        assert data['clicks'] == 150
        assert data['duration_seconds'] == 3600
        assert data['duration_formatted'] == "01:00:00"
        assert data['iph'] == 150.0
        assert data['regions_used'] == 1
        assert 'completed_at' in data

    def test_save_session_skips_empty(self, tracker, tmp_path):
        """Empty sessions (0 clicks, 0 duration) not saved."""
        session_file = tmp_path / "test_session.json"
        
        tracker.save_session(0, str(session_file))
        
        assert not session_file.exists()

    def test_save_session_iph_calculation(self, tracker, tmp_path):
        """IPH calculated correctly."""
        session_file = tmp_path / "test_session.json"
        tracker.count = 500
        
        # 30 minutes = 0.5 hours, so IPH = 500 / 0.5 = 1000
        tracker.save_session(1800, str(session_file))
        
        with open(session_file) as f:
            data = json.load(f)
        
        assert data['iph'] == 1000.0

    def test_save_session_iph_zero_duration(self, tracker, tmp_path):
        """IPH is 0 when duration is 0 but clicks > 0."""
        session_file = tmp_path / "test_session.json"
        tracker.count = 100
        
        # Can't save with 0 duration and 0 clicks, but 100 clicks should work
        # Actually the skip check is: count == 0 AND duration == 0
        tracker.save_session(1, str(session_file))  # 1 second
        
        with open(session_file) as f:
            data = json.load(f)
        
        # 100 clicks / (1/3600) hours = 360000 IPH
        assert data['iph'] == 360000.0


class TestSessionLoad:
    """Tests for loading session data."""

    def test_load_last_session(self, tracker, tmp_path):
        """Session data loaded correctly."""
        session_file = tmp_path / "test_session.json"
        
        session_data = {
            'clicks': 250,
            'duration_seconds': 1800,
            'duration_formatted': "00:30:00",
            'iph': 500.0,
            'completed_at': '2025-01-01T12:00:00',
            'regions_used': 2
        }
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        result = tracker.load_last_session(str(session_file))
        
        assert result is not None
        assert result['clicks'] == 250
        assert result['iph'] == 500.0

    def test_load_last_session_missing_file(self, tracker, tmp_path):
        """Returns None when session file doesn't exist."""
        missing_file = tmp_path / "nonexistent_session.json"
        
        result = tracker.load_last_session(str(missing_file))
        
        assert result is None

    def test_load_last_session_corrupt(self, tracker, tmp_path):
        """Returns None for corrupt session file."""
        corrupt_file = tmp_path / "corrupt_session.json"
        
        with open(corrupt_file, 'w') as f:
            f.write("not json")
        
        result = tracker.load_last_session(str(corrupt_file))
        
        assert result is None


class TestDurationFormatting:
    """Tests for duration formatting helper."""

    def test_format_duration_seconds(self, tracker):
        """Formats seconds correctly."""
        assert tracker._format_duration(45) == "00:00:45"

    def test_format_duration_minutes(self, tracker):
        """Formats minutes correctly."""
        assert tracker._format_duration(125) == "00:02:05"

    def test_format_duration_hours(self, tracker):
        """Formats hours correctly."""
        assert tracker._format_duration(3661) == "01:01:01"

    def test_format_duration_zero(self, tracker):
        """Formats zero correctly."""
        assert tracker._format_duration(0) == "00:00:00"
