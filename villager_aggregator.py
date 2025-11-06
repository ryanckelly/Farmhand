"""
Villager Relationship Aggregator

Builds time-series data for all villagers across all play sessions.
Reads diary.json and creates Chart.js-compatible datasets.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import TypedDict

from villager_database import get_all_villagers, VILLAGERS


class VillagerDataPoint(TypedDict):
    """Single data point in villager relationship timeline."""
    timestamp: str  # ISO format
    session_id: str
    game_date: str  # e.g., "Fall 16, Year 2"
    hearts: int
    points: int  # Friendship points (0-3500)


class VillagerTimeSeries(TypedDict):
    """Complete time-series for a single villager."""
    name: str
    color: str
    data_points: list[VillagerDataPoint]


def load_diary() -> dict:
    """Load diary.json from project root."""
    diary_path = Path(__file__).parent / "diary.json"
    if not diary_path.exists():
        return {"entries": []}

    with open(diary_path, 'r') as f:
        return json.load(f)


def load_current_snapshot() -> dict:
    """Load current save snapshot for latest friendship data."""
    snapshot_path = Path(__file__).parent / "save_snapshot.json"
    if not snapshot_path.exists():
        return {}

    with open(snapshot_path, 'r') as f:
        return json.load(f)


def aggregate_villager_history() -> dict[str, VillagerTimeSeries]:
    """
    Build complete relationship history for all villagers.

    Returns dict mapping villager name to their time-series data.
    Includes all sessions even if villager wasn't interacted with.
    """
    diary = load_diary()
    snapshot = load_current_snapshot()

    # Initialize time-series for all villagers
    villager_series: dict[str, list[VillagerDataPoint]] = defaultdict(list)

    # Track cumulative hearts across sessions
    villager_hearts: dict[str, int] = {}

    # Process each diary entry chronologically
    for entry in diary.get("entries", []):
        session_id = entry.get("session_id", "unknown")
        timestamp = entry.get("detected_at", "")
        game_date = entry.get("game_progress", {}).get("end", "Unknown")

        # Get friendship changes for this session
        friendship_changes = entry.get("changes_detail", {}).get("friendship_changes", {})

        # Update hearts for villagers that changed
        for villager, change_data in friendship_changes.items():
            new_hearts = change_data.get("new_hearts", 0)
            villager_hearts[villager] = new_hearts

            # Add data point for this villager
            villager_series[villager].append({
                "timestamp": timestamp,
                "session_id": session_id,
                "game_date": game_date,
                "hearts": new_hearts,
                "points": change_data.get("new_points", new_hearts * 250)  # Estimate if not available
            })

    # Add current state for villagers not in diary
    # This catches villagers you've never interacted with
    current_friendships = snapshot.get("friendships", {})

    for villager in get_all_villagers():
        if villager not in villager_hearts and villager in current_friendships:
            # Villager exists in save but no history - add current state
            hearts = current_friendships[villager].get("hearts", 0)
            points = current_friendships[villager].get("points", 0)

            if hearts > 0 or points > 0:
                villager_series[villager].append({
                    "timestamp": snapshot.get("timestamp", ""),
                    "session_id": "current",
                    "game_date": snapshot.get("game_date_str", "Unknown"),
                    "hearts": hearts,
                    "points": points
                })

    # Build final structure with metadata
    result: dict[str, VillagerTimeSeries] = {}

    for villager in get_all_villagers():
        villager_data = VILLAGERS.get(villager, {})

        result[villager] = {
            "name": villager,
            "color": villager_data.get("color", "#00ff00"),
            "data_points": villager_series.get(villager, [])
        }

    return result


def get_villager_chart_data(villager_name: str) -> dict:
    """
    Get Chart.js compatible dataset for a single villager.

    Returns:
        {
            "labels": ["Fall 6, Year 2", "Fall 7, Year 2", ...],
            "datasets": [{
                "label": "Abigail",
                "data": [8, 8, 10, 11, ...],
                "borderColor": "#9b59b6",
                ...
            }]
        }
    """
    all_series = aggregate_villager_history()

    if villager_name not in all_series:
        return {"labels": [], "datasets": []}

    series = all_series[villager_name]
    data_points = series["data_points"]

    if not data_points:
        return {"labels": [], "datasets": []}

    # Sort by timestamp
    sorted_points = sorted(data_points, key=lambda x: x["timestamp"])

    labels = [point["game_date"] for point in sorted_points]
    hearts = [point["hearts"] for point in sorted_points]

    return {
        "labels": labels,
        "datasets": [{
            "label": villager_name,
            "data": hearts,
            "borderColor": series["color"],
            "backgroundColor": f"{series['color']}33",  # 20% opacity
            "borderWidth": 3,
            "tension": 0.4,  # Smooth curves
            "fill": True
        }]
    }


def get_all_villagers_summary() -> list[dict]:
    """
    Get current status summary for all villagers.

    Returns list of dicts with name, hearts, color, initials for UI chip bar.
    """
    snapshot = load_current_snapshot()
    friendships = snapshot.get("friendships", {})

    summary = []

    for villager in get_all_villagers():
        villager_data = VILLAGERS.get(villager, {})
        friendship = friendships.get(villager, {})

        summary.append({
            "name": villager,
            "hearts": friendship.get("hearts", 0),
            "points": friendship.get("points", 0),
            "color": villager_data.get("color", "#00ff00"),
            "initials": villager_data.get("initials", villager[:2].upper()),
            "max_hearts": villager_data.get("max_hearts", 10)
        })

    return summary


# Testing
if __name__ == "__main__":
    print("=== Villager Relationship Aggregator ===\n")

    # Test aggregation
    all_series = aggregate_villager_history()

    print(f"Total villagers tracked: {len(all_series)}")

    # Show villagers with data
    villagers_with_data = [
        name for name, series in all_series.items()
        if series["data_points"]
    ]

    print(f"Villagers with relationship history: {len(villagers_with_data)}")
    print("\nVillagers with data:")
    for name in sorted(villagers_with_data):
        series = all_series[name]
        data_count = len(series["data_points"])
        if data_count > 0:
            latest = series["data_points"][-1]
            print(f"  {name:12} - {data_count:2} sessions, current: {latest['hearts']:2} hearts")

    # Test Chart.js data generation
    print("\n=== Sample Chart Data for Abigail ===")
    abigail_data = get_villager_chart_data("Abigail")
    print(f"Labels: {abigail_data.get('labels', [])[:3]}... ({len(abigail_data.get('labels', []))} total)")
    if abigail_data.get('datasets'):
        dataset = abigail_data['datasets'][0]
        print(f"Data: {dataset['data'][:3]}... ({len(dataset['data'])} total)")
        print(f"Color: {dataset['borderColor']}")

    # Test summary
    print("\n=== All Villagers Summary ===")
    summary = get_all_villagers_summary()
    print(f"Total villagers: {len(summary)}")
    print("\nVillagers with 5+ hearts:")
    for villager in summary:
        if villager["hearts"] >= 5:
            print(f"  {villager['name']:12} {villager['initials']:4} {villager['hearts']:2}♥  {villager['color']}")
