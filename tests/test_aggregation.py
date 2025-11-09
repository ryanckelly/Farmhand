"""
Unit tests for aggregation logic (week, season/month, year rollups)

Test IDs reference the comprehensive test matrix from the planning document.
"""

import pytest
from conftest import get_aggregated_data, slice_last_n


class TestAggregationDataAccess:
    """Test rollup data access patterns"""

    # TC-AG-001: Week aggregation (Game time)
    def test_week_aggregation_game(self, rollup_data):
        """Verify week aggregation returns game time weekly rollups"""
        rollup_array = get_aggregated_data(rollup_data, 'week', 'game')

        assert isinstance(rollup_array, list), "Should return a list"
        assert len(rollup_array) > 0, "Should have game week rollups"

        # Verify data structure
        for rollup in rollup_array:
            assert 'period' in rollup, "Rollup should have period label"
            assert 'sessions_count' in rollup, "Rollup should have sessions count"
            assert 'money_change' in rollup, "Rollup should have money_change"
            assert 'xp_by_skill' in rollup, "Rollup should have xp_by_skill"
            assert 'total_xp' in rollup, "Rollup should have total_xp"

        # Verify game week label format (e.g., "Y2W2-Winter")
        assert 'Y' in rollup_array[0]['period'], "Game week should have year prefix"
        assert 'W' in rollup_array[0]['period'], "Game week should have week prefix"

    # TC-AG-006: Week aggregation (Real time)
    def test_week_aggregation_real(self, rollup_data):
        """Verify week aggregation returns real time weekly rollups"""
        rollup_array = get_aggregated_data(rollup_data, 'week', 'real')

        assert isinstance(rollup_array, list), "Should return a list"
        assert len(rollup_array) > 0, "Should have real week rollups"

        # Verify real week label format (e.g., "2025-W45")
        assert 'W' in rollup_array[0]['period'], "Real week should have ISO week format"

    # TC-AG-007: Season aggregation (Game time)
    def test_season_aggregation_game(self, rollup_data):
        """Verify period aggregation returns game seasons"""
        rollup_array = get_aggregated_data(rollup_data, 'period', 'game')

        assert isinstance(rollup_array, list), "Should return a list"
        assert len(rollup_array) > 0, "Should have game season rollups"

        # Verify season label format (e.g., "Fall Y2" or "Winter Y2")
        season_names = ['Spring', 'Summer', 'Fall', 'Winter']
        assert any(season in rollup_array[0]['period'] for season in season_names), \
            "Game period should contain season name"
        assert 'Y' in rollup_array[0]['period'], "Game period should have year"

    # TC-AG-008: Month aggregation (Real time)
    def test_month_aggregation_real(self, rollup_data):
        """Verify period aggregation returns real months"""
        rollup_array = get_aggregated_data(rollup_data, 'period', 'real')

        assert isinstance(rollup_array, list), "Should return a list"
        assert len(rollup_array) > 0, "Should have real month rollups"

        # Verify month label format (e.g., "2025-11")
        assert '-' in rollup_array[0]['period'], "Real month should have YYYY-MM format"

    # TC-AG-009: Year aggregation (Game time)
    def test_year_aggregation_game(self, rollup_data):
        """Verify year aggregation returns game years"""
        rollup_array = get_aggregated_data(rollup_data, 'year', 'game')

        assert isinstance(rollup_array, list), "Should return a list"
        assert len(rollup_array) > 0, "Should have game year rollups"

        # Verify year label format (e.g., "Year 2")
        assert 'Year' in rollup_array[0]['period'], "Game year should have 'Year' prefix"

    # TC-AG-010: Year aggregation (Real time)
    def test_year_aggregation_real(self, rollup_data):
        """Verify year aggregation returns real years"""
        rollup_array = get_aggregated_data(rollup_data, 'year', 'real')

        assert isinstance(rollup_array, list), "Should return a list"
        assert len(rollup_array) > 0, "Should have real year rollups"

        # Verify year label format (e.g., "2025")
        assert len(rollup_array[0]['period']) == 4, "Real year should be 4 digits"
        assert rollup_array[0]['period'].isdigit(), "Real year should be numeric"


class TestAggregationDataIntegrity:
    """Test aggregation data integrity and calculations"""

    # EC-010: Verify cumulative values are correct
    def test_cumulative_values_integrity(self, rollup_data):
        """Verify money_change sums match when aggregated"""
        game_weeks = get_aggregated_data(rollup_data, 'week', 'game')
        game_seasons = get_aggregated_data(rollup_data, 'period', 'game')

        # Sum money_change across all weeks
        week_total = sum(week['money_change'] for week in game_weeks)

        # Sum money_change across all seasons
        season_total = sum(season['money_change'] for season in game_seasons)

        # These should match (or be very close, accounting for floating point)
        assert abs(week_total - season_total) < 100, \
            f"Week total ({week_total}) should match season total ({season_total})"

    # Verify XP totals are consistent
    def test_xp_totals_consistency(self, rollup_data):
        """Verify total_xp matches sum of xp_by_skill"""
        game_weeks = get_aggregated_data(rollup_data, 'week', 'game')

        for week in game_weeks:
            xp_by_skill = week['xp_by_skill']
            total_xp = week['total_xp']

            calculated_total = sum(xp_by_skill.values())

            assert calculated_total == total_xp, \
                f"XP sum ({calculated_total}) should match total_xp ({total_xp}) for {week['period']}"

    # Verify sessions_count is accurate
    def test_sessions_count_accuracy(self, rollup_data, diary_data):
        """Verify sessions_count in rollups matches diary entries"""
        game_weeks = get_aggregated_data(rollup_data, 'week', 'game')
        total_sessions_in_rollups = sum(week['sessions_count'] for week in game_weeks)

        diary_entries_count = len(diary_data['entries'])

        assert total_sessions_in_rollups == diary_entries_count, \
            f"Total sessions in rollups ({total_sessions_in_rollups}) should match diary entries ({diary_entries_count})"


class TestAggregationEdgeCases:
    """Test edge cases in aggregation logic"""

    # EC-002: Empty/missing rollup data
    def test_empty_rollup_data(self):
        """Verify graceful handling of empty rollup data"""
        empty_rollup = {}
        rollup_array = get_aggregated_data(empty_rollup, 'week', 'game')

        assert rollup_array == [], "Should return empty array for missing data"

    # EC-003: Single session aggregation
    def test_single_session_rollup(self):
        """Verify aggregation works with single session"""
        single_rollup = {
            'game_time': {
                'by_week': [{
                    'period': 'Y2W1-Fall',
                    'sessions_count': 1,
                    'money_change': 100,
                    'xp_by_skill': {'farming': 50},
                    'total_xp': 50
                }]
            }
        }

        rollup_array = get_aggregated_data(single_rollup, 'week', 'game')

        assert len(rollup_array) == 1, "Should handle single rollup entry"
        assert rollup_array[0]['sessions_count'] == 1, "Should show 1 session"

    # Verify all aggregation levels return data
    def test_all_aggregation_levels(self, rollup_data):
        """Verify all aggregation levels return non-empty data"""
        levels = ['week', 'period', 'year']
        modes = ['game', 'real']

        for level in levels:
            for mode in modes:
                rollup_array = get_aggregated_data(rollup_data, level, mode)
                assert len(rollup_array) > 0, \
                    f"Aggregation level '{level}' in mode '{mode}' should return data"


class TestAggregationWithFilters:
    """Test combined aggregation + filtering behavior"""

    # TC-FA-003: Filter week rollups to last N
    def test_filter_aggregated_weeks(self, rollup_data):
        """Verify filtering applies to aggregated data"""
        game_weeks = get_aggregated_data(rollup_data, 'week', 'game')
        total_weeks = len(game_weeks)

        # Filter to last 5 weeks
        filtered = slice_last_n(game_weeks, 5, total_weeks)

        assert len(filtered) <= 5, "Should show at most 5 weeks"
        if total_weeks >= 5:
            assert len(filtered) == 5, "Should show exactly 5 weeks if available"
            assert filtered[-1] == game_weeks[-1], "Last week should match most recent"

    # TC-FA-006: Filter seasons to last N
    def test_filter_aggregated_seasons(self, rollup_data):
        """Verify filtering applies to season rollups"""
        game_seasons = get_aggregated_data(rollup_data, 'period', 'game')
        total_seasons = len(game_seasons)

        # Filter to last 2 seasons
        filtered = slice_last_n(game_seasons, 2, total_seasons)

        assert len(filtered) <= 2, "Should show at most 2 seasons"
        if total_seasons >= 2:
            assert len(filtered) == 2, "Should show exactly 2 seasons if available"

    # TC-FA-007: Filter years (edge case - usually only 1-2 years)
    def test_filter_aggregated_years(self, rollup_data):
        """Verify filtering applies to year rollups"""
        game_years = get_aggregated_data(rollup_data, 'year', 'game')
        total_years = len(game_years)

        # Try to filter to last 5 years (likely will return all)
        filtered = slice_last_n(game_years, 5, total_years)

        assert len(filtered) == total_years, "Should return all years if less than filter count"


class TestContextAwareAggregation:
    """Test context-aware aggregation (Season vs Month)"""

    # TC-AG-003: Period aggregation changes based on mode
    def test_period_mode_switching(self, rollup_data):
        """Verify period aggregation uses Season (game) or Month (real) correctly"""
        game_period = get_aggregated_data(rollup_data, 'period', 'game')
        real_period = get_aggregated_data(rollup_data, 'period', 'real')

        # Verify game period uses seasons
        season_names = ['Spring', 'Summer', 'Fall', 'Winter']
        assert any(season in game_period[0]['period'] for season in season_names), \
            "Game period should use season names"

        # Verify real period uses month format
        assert '-' in real_period[0]['period'], \
            "Real period should use YYYY-MM format"

    # Verify different data sources
    def test_period_different_data_sources(self, rollup_data):
        """Verify game/real period aggregations use different rollup arrays"""
        game_period = get_aggregated_data(rollup_data, 'period', 'game')
        real_period = get_aggregated_data(rollup_data, 'period', 'real')

        # Should have different data (different time groupings)
        assert game_period != real_period, "Game and real periods should differ"

        # Should potentially have different counts
        # (4 game seasons vs ~1-2 real months for same time span)
        game_count = len(game_period)
        real_count = len(real_period)

        # This is expected for typical data
        assert game_count != real_count or game_period[0] != real_period[0], \
            "Game and real aggregations should produce different results"
