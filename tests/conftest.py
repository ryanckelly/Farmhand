"""
Pytest configuration and shared fixtures for dashboard testing
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import pytest

# Base path
BASE_DIR = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def dashboard_html():
    """Load the generated trends.html file"""
    html_path = BASE_DIR / 'dashboard' / 'trends.html'
    if not html_path.exists():
        pytest.skip("trends.html not found - run dashboard_generator.py first")

    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope="session")
def embedded_data(dashboard_html):
    """Extract embedded JSON data from the HTML file"""
    soup = BeautifulSoup(dashboard_html, 'html.parser')

    # Find the script tag containing the embedded data
    scripts = soup.find_all('script')

    data = {
        'diary': None,
        'rollups': None,
        'villagers': None,
        'max_sessions': None
    }

    for script in scripts:
        script_text = script.string
        if not script_text:
            continue

        # Extract diaryData
        diary_match = re.search(r'const diaryData = ({.*?});', script_text, re.DOTALL)
        if diary_match:
            data['diary'] = json.loads(diary_match.group(1))

        # Extract rollupData
        rollup_match = re.search(r'const rollupData = ({.*?});', script_text, re.DOTALL)
        if rollup_match:
            data['rollups'] = json.loads(rollup_match.group(1))

        # Extract villagersData
        villagers_match = re.search(r'const villagersData = (\[.*?\]);', script_text, re.DOTALL)
        if villagers_match:
            data['villagers'] = json.loads(villagers_match.group(1))

        # Extract maxSessions
        max_match = re.search(r'const maxSessions = (\d+);', script_text)
        if max_match:
            data['max_sessions'] = int(max_match.group(1))

    return data


@pytest.fixture(scope="session")
def diary_data(embedded_data):
    """Get diary data"""
    return embedded_data['diary']


@pytest.fixture(scope="session")
def rollup_data(embedded_data):
    """Get rollup data"""
    return embedded_data['rollups']


@pytest.fixture(scope="session")
def max_sessions(embedded_data):
    """Get max sessions count"""
    # Calculate from diary entries if not explicitly defined
    if embedded_data['max_sessions'] is not None:
        return embedded_data['max_sessions']
    elif embedded_data['diary'] and 'entries' in embedded_data['diary']:
        return len(embedded_data['diary']['entries'])
    else:
        return 0


def slice_last_n(data_array, n, max_count):
    """
    Helper function to simulate JavaScript array slicing for last N elements
    Equivalent to: data.slice(Math.max(0, data.length - n))
    """
    if n >= max_count:
        return data_array
    start_index = max(0, len(data_array) - n)
    return data_array[start_index:]


def filter_by_real_time_range(entries, range_type):
    """
    Simulate filterByRealTimeRange function
    Returns entries within the specified time range
    """
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)

    if range_type == 'week':
        cutoff = now - timedelta(days=7)
    elif range_type == 'month':
        cutoff = now - timedelta(days=30)
    else:
        return entries

    filtered = []
    for entry in entries:
        if 'detected_at' in entry:
            # Parse entry date - handle both with and without timezone
            entry_date_str = entry['detected_at']
            if entry_date_str.endswith('Z'):
                entry_date_str = entry_date_str.replace('Z', '+00:00')
            entry_date = datetime.fromisoformat(entry_date_str)

            # Make timezone-aware if needed
            if entry_date.tzinfo is None:
                entry_date = entry_date.replace(tzinfo=timezone.utc)

            if entry_date >= cutoff:
                filtered.append(entry)

    return filtered


def filter_by_game_time_range(entries, range_type):
    """
    Simulate filterByGameTimeRange function
    Returns entries within the specified game time range
    """
    if not entries:
        return []

    # Get the latest entry's game date
    latest_entry = entries[-1]
    latest_game_progress = latest_entry.get('game_progress', {})
    latest_end = latest_game_progress.get('end', '')

    # Parse "Winter 23, Year 2" format
    match = re.match(r'(\w+)\s+\d+,\s+Year\s+(\d+)', latest_end)
    if not match:
        return entries

    latest_season = match.group(1)
    latest_year = int(match.group(2))

    filtered = []
    for entry in entries:
        game_progress = entry.get('game_progress', {})
        end_date = game_progress.get('end', '')

        entry_match = re.match(r'(\w+)\s+\d+,\s+Year\s+(\d+)', end_date)
        if not entry_match:
            continue

        entry_season = entry_match.group(1)
        entry_year = int(entry_match.group(2))

        if range_type == 'season':
            # Same season and year
            if entry_season == latest_season and entry_year == latest_year:
                filtered.append(entry)
        elif range_type == 'year':
            # Same year
            if entry_year == latest_year:
                filtered.append(entry)

    return filtered


def get_aggregated_data(rollup_data, level, mode):
    """
    Simulate getAggregatedChartData function
    Returns aggregated data based on level and mode
    """
    time_mode = 'real_time' if mode == 'real' else 'game_time'

    if level == 'week':
        rollup_array = rollup_data.get(time_mode, {}).get('by_week', [])
    elif level == 'period':
        if mode == 'real':
            rollup_array = rollup_data.get('real_time', {}).get('by_month', [])
        else:
            rollup_array = rollup_data.get('game_time', {}).get('by_season', [])
    elif level == 'year':
        rollup_array = rollup_data.get(time_mode, {}).get('by_year', [])
    else:
        rollup_array = []

    return rollup_array
