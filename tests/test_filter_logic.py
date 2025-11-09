"""
Unit tests for quick filter logic (numeric and time-based filters)

Test IDs reference the comprehensive test matrix from the planning document.
"""

import pytest
from conftest import slice_last_n, filter_by_real_time_range, filter_by_game_time_range


class TestQuickFilterNumeric:
    """Test numeric filter values: 5, 10, 20, all"""

    # TC-QF-001: Filter to last 5 sessions
    def test_filter_last_5_sessions(self, diary_data, max_sessions):
        """Verify filtering to last 5 sessions works correctly"""
        entries = diary_data['entries']
        assert len(entries) == max_sessions, f"Expected {max_sessions} total entries"

        filtered = slice_last_n(entries, 5, max_sessions)

        assert len(filtered) == 5, "Should show exactly 5 sessions"
        assert filtered[-1] == entries[-1], "Last entry should match most recent"
        assert filtered[0] == entries[-5], "First entry should be 5th from end"

    # TC-QF-002: Filter to last 10 sessions (default)
    def test_filter_last_10_sessions(self, diary_data, max_sessions):
        """Verify default filter (Last 10 Sessions) works correctly"""
        entries = diary_data['entries']
        filtered = slice_last_n(entries, 10, max_sessions)

        assert len(filtered) == 10, "Should show exactly 10 sessions"
        assert filtered[-1] == entries[-1], "Last entry should match most recent"

    # TC-QF-003: Filter to last 20 sessions
    def test_filter_last_20_sessions(self, diary_data, max_sessions):
        """Verify filtering to last 20 sessions works correctly"""
        entries = diary_data['entries']
        filtered = slice_last_n(entries, 20, max_sessions)

        assert len(filtered) == 20, "Should show exactly 20 sessions"

    # TC-QF-004: Filter to "All Sessions"
    def test_filter_all_sessions(self, diary_data, max_sessions):
        """Verify 'All Sessions' shows complete dataset"""
        entries = diary_data['entries']
        filtered = slice_last_n(entries, max_sessions, max_sessions)

        assert len(filtered) == max_sessions, f"Should show all {max_sessions} sessions"
        assert filtered == entries, "Filtered data should match original"

    # Edge Case: Filter count exceeds total sessions
    def test_filter_exceeds_total(self, diary_data, max_sessions):
        """Verify filtering with count > total returns all sessions"""
        entries = diary_data['entries']
        filtered = slice_last_n(entries, 100, max_sessions)

        assert len(filtered) == max_sessions, "Should not exceed total sessions"
        assert filtered == entries, "Should return complete dataset"

    # Edge Case: Filter with count = 0
    def test_filter_zero_sessions(self, diary_data, max_sessions):
        """Verify filtering to 0 sessions returns empty array"""
        entries = diary_data['entries']
        filtered = slice_last_n(entries, 0, max_sessions)

        assert len(filtered) == 0, "Should return empty array"


class TestTimeBasedFilters:
    """Test time-based filters: this-week-real, this-month-real, this-season-game, this-year-game"""

    # TC-TF-001: Filter "This Week (real)"
    def test_filter_this_week_real(self, diary_data):
        """Verify 'This Week (real)' filters to last 7 days"""
        entries = diary_data['entries']
        filtered = filter_by_real_time_range(entries, 'week')

        # Verify all entries are within last 7 days
        from datetime import datetime, timedelta
        now = datetime.now()
        cutoff = now - timedelta(days=7)

        for entry in filtered:
            assert 'detected_at' in entry, "Entry should have detected_at timestamp"
            entry_date = datetime.fromisoformat(entry['detected_at'].replace('Z', '+00:00'))
            assert entry_date >= cutoff, f"Entry {entry_date} should be within last 7 days"

    # TC-TF-002: Filter "This Month (real)"
    def test_filter_this_month_real(self, diary_data):
        """Verify 'This Month (real)' filters to last 30 days"""
        entries = diary_data['entries']
        filtered = filter_by_real_time_range(entries, 'month')

        # Verify all entries are within last 30 days
        from datetime import datetime, timedelta
        now = datetime.now()
        cutoff = now - timedelta(days=30)

        for entry in filtered:
            assert 'detected_at' in entry, "Entry should have detected_at timestamp"
            entry_date = datetime.fromisoformat(entry['detected_at'].replace('Z', '+00:00'))
            assert entry_date >= cutoff, f"Entry should be within last 30 days"

    # TC-TF-003: Filter "This Season (game)"
    def test_filter_this_season_game(self, diary_data):
        """Verify 'This Season (game)' filters to current game season"""
        entries = diary_data['entries']
        filtered = filter_by_game_time_range(entries, 'season')

        if not filtered:
            pytest.skip("No entries in current season")

        # Get latest season from last entry
        latest_entry = entries[-1]
        latest_end = latest_entry.get('game_progress', {}).get('end', '')

        # Verify all filtered entries match this season and year
        import re
        latest_match = re.match(r'(\w+)\s+\d+,\s+Year\s+(\d+)', latest_end)
        assert latest_match, "Should parse latest game date"

        latest_season = latest_match.group(1)
        latest_year = latest_match.group(2)

        for entry in filtered:
            end_date = entry.get('game_progress', {}).get('end', '')
            assert latest_season in end_date, f"Entry should be in {latest_season}"
            assert f"Year {latest_year}" in end_date, f"Entry should be in Year {latest_year}"

    # TC-TF-004: Filter "This Year (game)"
    def test_filter_this_year_game(self, diary_data):
        """Verify 'This Year (game)' filters to current game year"""
        entries = diary_data['entries']
        filtered = filter_by_game_time_range(entries, 'year')

        if not filtered:
            pytest.skip("No entries in current year")

        # Get latest year from last entry
        latest_entry = entries[-1]
        latest_end = latest_entry.get('game_progress', {}).get('end', '')

        import re
        latest_match = re.match(r'(\w+)\s+\d+,\s+Year\s+(\d+)', latest_end)
        assert latest_match, "Should parse latest game date"
        latest_year = latest_match.group(2)

        for entry in filtered:
            end_date = entry.get('game_progress', {}).get('end', '')
            assert f"Year {latest_year}" in end_date, f"Entry should be in Year {latest_year}"

    # EC-004: Empty time range
    def test_filter_empty_time_range(self, diary_data):
        """Verify graceful handling when time range has no data"""
        # This test validates the function doesn't crash on empty results
        entries = []  # Empty dataset
        filtered = filter_by_real_time_range(entries, 'week')

        assert filtered == [], "Should return empty array for empty input"


class TestFilterEdgeCases:
    """Test edge cases in filter logic"""

    # EC-005: Missing detected_at timestamp
    def test_missing_timestamp(self):
        """Verify entries without detected_at are skipped in real-time filters"""
        entries = [
            {'detected_at': '2025-11-01T10:00:00Z'},
            {},  # No detected_at
            {'detected_at': '2025-11-08T10:00:00Z'}
        ]

        filtered = filter_by_real_time_range(entries, 'week')

        # Should only include entries with valid timestamps
        assert len(filtered) <= len(entries), "Should not add extra entries"
        for entry in filtered:
            assert 'detected_at' in entry, "Filtered entries should have timestamps"

    # Test filter consistency
    def test_filter_idempotent(self, diary_data, max_sessions):
        """Verify filtering same data twice produces same result"""
        entries = diary_data['entries']

        filtered1 = slice_last_n(entries, 10, max_sessions)
        filtered2 = slice_last_n(entries, 10, max_sessions)

        assert filtered1 == filtered2, "Filter should be deterministic"

    # Test data integrity after filtering
    def test_filter_preserves_data(self, diary_data, max_sessions):
        """Verify filtering doesn't modify original data"""
        entries = diary_data['entries']
        original_count = len(entries)

        _ = slice_last_n(entries, 5, max_sessions)

        assert len(entries) == original_count, "Filter should not modify original array"
