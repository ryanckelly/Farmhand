import json
import sys
from pathlib import Path
from datetime import datetime
from save_analyzer import analyze_save
from bundle_checker import check_bundle_readiness, get_ready_bundles_summary, get_bundles_by_priority

DIARY_PATH = Path(r'C:\opt\stardew\diary.json')
METRICS_PATH = Path(r'C:\opt\stardew\metrics.json')
SNAPSHOT_PATH = Path(r'C:\opt\stardew\save_snapshot.json')

def track_session():
    """
    Main session tracking function.
    Compares current save state with last snapshot and generates diary entry if changes detected.
    """
    print("Analyzing Stardew Valley save file...")

    # Analyze current save state
    current_state = analyze_save()

    if 'error' in current_state:
        print(f"Error analyzing save: {current_state['error']}")
        return {
            'status': 'error',
            'message': current_state['error']
        }

    print(f"Current state: {current_state['game_date_str']}, {current_state['money']:,}g")

    # Load last snapshot
    if not SNAPSHOT_PATH.exists():
        print("First run - creating initial snapshot")
        save_snapshot(current_state)
        initialize_tracking_files()
        return {
            'status': 'initialized',
            'message': 'Tracking system initialized with current save state'
        }

    with open(SNAPSHOT_PATH, 'r') as f:
        last_state = json.load(f)

    # Check if save has changed
    if states_are_identical(current_state, last_state):
        last_check = datetime.fromisoformat(last_state['timestamp'])
        time_since = datetime.now() - last_check
        hours = int(time_since.total_seconds() / 3600)
        minutes = int((time_since.total_seconds() % 3600) / 60)

        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        print(f"No changes detected (last check: {time_str} ago)")
        print(f"Last play session: {last_state.get('game_date_str', 'unknown')}")

        return {
            'status': 'no_change',
            'message': f'No play session detected since last check ({time_str} ago)',
            'last_state': last_state
        }

    # Changes detected - generate diary entry
    print("Changes detected - generating diary entry...")

    changes = calculate_changes(last_state, current_state)

    # NEW: Check bundle readiness
    bundle_readiness = check_bundles_against_inventory(current_state)

    diary_entry = generate_diary_entry(changes, last_state, current_state, bundle_readiness)

    # Update tracking files
    add_diary_entry(diary_entry)
    update_metrics(current_state)
    save_snapshot(current_state)

    print(f"Session recorded: {diary_entry['game_progress']['start']} -> {diary_entry['game_progress']['end']}")
    print(f"Money: {changes['money_change']:+,}g")
    print(f"{len(diary_entry['key_accomplishments'])} accomplishments logged")

    return {
        'status': 'session_recorded',
        'diary_entry': diary_entry,
        'changes': changes
    }

def check_bundles_against_inventory(state):
    """Check which bundles can be completed with current inventory/chests."""
    if 'bundles' not in state or 'inventory' not in state:
        return None

    bundle_progress = state['bundles']
    inventory = state.get('inventory', [])
    chest_contents_raw = state.get('chest_contents', [])

    # Flatten chest contents from new organized format to flat list
    chest_contents = []
    for chest in chest_contents_raw:
        for item in chest.get('items', []):
            chest_contents.append({
                'id': item['id'],
                'name': item['name'],
                'quantity': item['quantity'],
                'quality': item['quality'],
                'location': f"Chest #{chest['chest_number']} ({chest['location']})"
            })

    # Check bundle readiness
    readiness = check_bundle_readiness(bundle_progress, inventory, chest_contents)
    ready_bundles = get_ready_bundles_summary(readiness)
    priority_bundles = get_bundles_by_priority(readiness)

    return {
        'ready_bundles': ready_bundles,
        'priority_bundles': priority_bundles[:5],  # Top 5 closest to completion
        'full_readiness': readiness
    }


def states_are_identical(state1, state2):
    """Check if two save states represent the same game state (no play session between them)."""
    return (
        state1['game_date'] == state2['game_date'] and
        state1['money'] == state2['money'] and
        state1['play_time'] == state2['play_time']
    )

def calculate_changes(old_state, new_state):
    """Calculate what changed between two save states."""
    changes = {
        'money_change': new_state['money'] - old_state['money'],
        'total_earned_change': new_state['total_earned'] - old_state['total_earned'],
        'days_passed': calculate_days_passed(old_state['game_date'], new_state['game_date']),
        'play_time_change': new_state['play_time'] - old_state['play_time'],
    }

    # Skill changes
    changes['skill_changes'] = {}
    for skill in new_state['skills']:
        old_level = old_state['skills'].get(skill, {}).get('level', 0)
        new_level = new_state['skills'][skill]['level']
        old_xp = old_state['skills'].get(skill, {}).get('xp', 0)
        new_xp = new_state['skills'][skill]['xp']

        if new_level != old_level or new_xp != old_xp:
            changes['skill_changes'][skill] = {
                'old_level': old_level,
                'new_level': new_level,
                'xp_gained': new_xp - old_xp
            }

    # Animal changes
    old_total = old_state['animals']['total']
    new_total = new_state['animals']['total']
    changes['animals_change'] = new_total - old_total

    # Friendship changes
    changes['friendship_changes'] = {}
    for npc, data in new_state['friendships'].items():
        old_points = old_state['friendships'].get(npc, {}).get('points', 0)
        new_points = data['points']
        if new_points != old_points:
            changes['friendship_changes'][npc] = {
                'old_hearts': old_points // 250,
                'new_hearts': new_points // 250,
                'points_gained': new_points - old_points
            }

    # Bundle changes
    old_complete = old_state.get('bundles', {}).get('complete_count', 0)
    new_complete = new_state.get('bundles', {}).get('complete_count', 0)
    changes['bundles_completed'] = new_complete - old_complete

    # Golden Walnuts (Ginger Island)
    old_walnuts = old_state.get('unlocks', {}).get('golden_walnuts_found', 0)
    new_walnuts = new_state.get('unlocks', {}).get('golden_walnuts_found', 0)
    changes['golden_walnuts_found'] = new_walnuts - old_walnuts

    # Skull Cavern deepest level
    old_skull_depth = old_state.get('unlocks', {}).get('skull_cavern_level', 0)
    new_skull_depth = new_state.get('unlocks', {}).get('skull_cavern_level', 0)
    changes['skull_cavern_depth_change'] = new_skull_depth - old_skull_depth

    # Perfection tracking
    old_perfection = old_state.get('perfection', {})
    new_perfection = new_state.get('perfection', {})

    changes['perfection_changes'] = {
        'overall_percent_change': new_perfection.get('total_percent', 0) - old_perfection.get('total_percent', 0),
        'obelisks_built': new_perfection.get('obelisks', {}).get('count', 0) - old_perfection.get('obelisks', {}).get('count', 0),
        'golden_clock_acquired': new_perfection.get('golden_clock', False) and not old_perfection.get('golden_clock', False),
        'produce_shipped_change': new_perfection.get('produce_shipped', {}).get('count', 0) - old_perfection.get('produce_shipped', {}).get('count', 0),
        'fish_caught_change': new_perfection.get('fish_caught', {}).get('count', 0) - old_perfection.get('fish_caught', {}).get('count', 0),
        'recipes_cooked_change': new_perfection.get('recipes_cooked', {}).get('count', 0) - old_perfection.get('recipes_cooked', {}).get('count', 0),
        'recipes_crafted_change': new_perfection.get('recipes_crafted', {}).get('count', 0) - old_perfection.get('recipes_crafted', {}).get('count', 0),
        'stardrops_found_change': new_perfection.get('stardrops_found', {}).get('count', 0) - old_perfection.get('stardrops_found', {}).get('count', 0),
        'monster_goals_completed': new_perfection.get('monster_goals', {}).get('count', 0) - old_perfection.get('monster_goals', {}).get('count', 0)
    }

    return changes

def calculate_days_passed(old_date, new_date):
    """Calculate in-game days passed between two dates."""
    season_order = ['spring', 'summer', 'fall', 'winter']

    old_season = old_date['season'].lower()
    new_season = new_date['season'].lower()

    old_season_idx = season_order.index(old_season) if old_season in season_order else 0
    new_season_idx = season_order.index(new_season) if new_season in season_order else 0

    # Calculate total days
    old_total = (old_date['year'] * 112) + (old_season_idx * 28) + old_date['day']
    new_total = (new_date['year'] * 112) + (new_season_idx * 28) + new_date['day']

    return new_total - old_total

def parse_game_date(date_string):
    """
    Parse human-readable game date string into structured object.

    Args:
        date_string (str): Date in format "Fall 6, Year 2"

    Returns:
        dict: {season: str, day: int, year: int} or None if parsing fails

    Examples:
        "Fall 6, Year 2" -> {'season': 'fall', 'day': 6, 'year': 2}
        "Spring 1, Year 1" -> {'season': 'spring', 'day': 1, 'year': 1}
    """
    import re

    # Pattern: "Season Day, Year Y"
    match = re.match(r'(\w+)\s+(\d+),\s+Year\s+(\d+)', date_string)

    if not match:
        return None

    season = match.group(1).lower()
    day = int(match.group(2))
    year = int(match.group(3))

    return {
        'season': season,
        'day': day,
        'year': year
    }

def generate_diary_entry(changes, old_state, new_state, bundle_readiness=None):
    """Generate a detailed diary entry from the changes detected."""
    # Parse game dates into structured format
    start_parsed = parse_game_date(old_state['game_date_str'])
    end_parsed = parse_game_date(new_state['game_date_str'])

    entry = {
        'session_id': f"{datetime.now().strftime('%Y-%m-%d-%H%M')}",
        'detected_at': datetime.now().isoformat(),
        'game_progress': {
            'start': old_state['game_date_str'],
            'end': new_state['game_date_str'],
            'start_parsed': start_parsed,
            'end_parsed': end_parsed,
            'days_played': changes['days_passed'],
            'play_time_minutes': changes['play_time_change'] // 60000
        },
        'financial': {
            'starting_money': old_state['money'],
            'ending_money': new_state['money'],
            'change': changes['money_change'],
            'total_earned_lifetime': new_state['total_earned']
        },
        'key_accomplishments': []
    }

    # Add bundle readiness info if available
    if bundle_readiness:
        entry['bundle_readiness'] = {
            'ready_to_complete': [b['name'] for b in bundle_readiness['ready_bundles']],
            'priority_bundles': [
                {
                    'name': b['name'],
                    'missing': b['missing_count'],
                    'completion': f"{b['completion_percent']:.0f}%"
                }
                for b in bundle_readiness['priority_bundles']
            ]
        }

    # Build accomplishments list
    accomplishments = []

    # Skill level ups
    for skill, change in changes['skill_changes'].items():
        if change['new_level'] > change['old_level']:
            accomplishments.append(f"Reached {skill.title()} Level {change['new_level']}")
        elif change['xp_gained'] > 0:
            accomplishments.append(f"Gained {change['xp_gained']:,} {skill.title()} XP")

    # Money milestones
    if changes['money_change'] > 0:
        accomplishments.append(f"Earned {changes['money_change']:,}g (net)")
    elif changes['money_change'] < 0:
        accomplishments.append(f"Invested {abs(changes['money_change']):,}g")

    # Animals
    if changes['animals_change'] > 0:
        accomplishments.append(f"Purchased {changes['animals_change']} new animals")
    elif changes['animals_change'] < 0:
        accomplishments.append(f"Sold {abs(changes['animals_change'])} animals")

    # Friendships
    for npc, change in changes['friendship_changes'].items():
        if change['new_hearts'] > change['old_hearts']:
            accomplishments.append(f"Reached {change['new_hearts']} hearts with {npc}")

    # Bundles
    if changes['bundles_completed'] > 0:
        accomplishments.append(f"Completed {changes['bundles_completed']} Community Center bundle(s)")

    # Golden Walnuts (Ginger Island)
    if changes['golden_walnuts_found'] > 0:
        accomplishments.append(f"Found {changes['golden_walnuts_found']} Golden Walnut(s)")

    # Skull Cavern depth
    if changes['skull_cavern_depth_change'] > 0:
        accomplishments.append(f"Reached floor {new_state['unlocks']['skull_cavern_level']} in Skull Cavern (new record!)")

    # Days progression
    if changes['days_passed'] > 0:
        accomplishments.append(f"Progressed {changes['days_passed']} in-game day(s)")

    # Perfection accomplishments
    perfection = changes.get('perfection_changes', {})

    if perfection.get('golden_clock_acquired'):
        accomplishments.append("Built the Golden Clock! (10% toward Perfection)")

    if perfection.get('obelisks_built', 0) > 0:
        accomplishments.append(f"Built {perfection['obelisks_built']} obelisk(s)")

    if perfection.get('stardrops_found_change', 0) > 0:
        accomplishments.append(f"Found {perfection['stardrops_found_change']} stardrop(s)")

    if perfection.get('recipes_cooked_change', 0) > 0:
        accomplishments.append(f"Cooked {perfection['recipes_cooked_change']} new recipe(s)")

    if perfection.get('recipes_crafted_change', 0) > 0:
        accomplishments.append(f"Crafted {perfection['recipes_crafted_change']} new item(s)")

    if perfection.get('fish_caught_change', 0) > 0:
        accomplishments.append(f"Caught {perfection['fish_caught_change']} new fish species")

    if perfection.get('produce_shipped_change', 0) > 0:
        accomplishments.append(f"Shipped {perfection['produce_shipped_change']} new item type(s)")

    if perfection.get('monster_goals_completed', 0) > 0:
        accomplishments.append(f"Completed {perfection['monster_goals_completed']} Monster Slayer goal(s)")

    # Overall perfection progress
    if perfection.get('overall_percent_change', 0) > 0:
        accomplishments.append(f"Perfection: +{perfection['overall_percent_change']:.1f}%")

    entry['key_accomplishments'] = accomplishments
    entry['changes_detail'] = changes

    return entry

def add_diary_entry(entry):
    """Add a new entry to diary.json."""
    with open(DIARY_PATH, 'r') as f:
        diary = json.load(f)

    diary['entries'].append(entry)
    diary['meta']['total_sessions'] = len(diary['entries'])
    diary['meta']['last_updated'] = datetime.now().isoformat()

    # Update date_index metadata
    diary['meta']['schema_version'] = "1.2"
    diary['meta']['date_index'] = {
        'game': get_game_date_range(diary['entries']),
        'real': get_real_date_range(diary['entries'])
    }

    with open(DIARY_PATH, 'w') as f:
        json.dump(diary, f, indent=2)

def update_metrics(state):
    """Update metrics.json with new snapshot data."""
    with open(METRICS_PATH, 'r') as f:
        metrics = json.load(f)

    # Extract perfection data
    perfection = state.get('perfection', {})
    perfection_snapshot = {
        'overall_percent': perfection.get('total_percent', 0),
        'obelisks': perfection.get('obelisks', {}).get('count', 0),
        'golden_clock': perfection.get('golden_clock', False),
        'produce_shipped': perfection.get('produce_shipped', {}).get('count', 0),
        'fish_caught': perfection.get('fish_caught', {}).get('count', 0),
        'recipes_cooked': perfection.get('recipes_cooked', {}).get('count', 0),
        'recipes_crafted': perfection.get('recipes_crafted', {}).get('count', 0),
        'stardrops_found': perfection.get('stardrops_found', {}).get('count', 0),
        'monster_goals': perfection.get('monster_goals', {}).get('count', 0)
    }

    snapshot = {
        'date': datetime.now().isoformat(),
        'game_date': state['game_date_str'],
        'money': state['money'],
        'total_earned': state['total_earned'],
        'animals': state['animals']['total'],
        'skills': {k: v['level'] for k, v in state['skills'].items()},
        'bundles_complete': state.get('bundles', {}).get('complete_count', 0),
        'perfection': perfection_snapshot
    }

    metrics['snapshots'].append(snapshot)
    metrics['meta']['total_snapshots'] = len(metrics['snapshots'])

    # Calculate trends if we have enough data
    if len(metrics['snapshots']) >= 2:
        metrics['trends'] = calculate_trends(metrics['snapshots'])

    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)

def calculate_trends(snapshots):
    """Calculate trend data from snapshots."""
    if len(snapshots) < 2:
        return {'daily_income_avg': 0, 'money_growth_rate': 0}

    # Simple trends from last two snapshots
    recent = snapshots[-1]
    previous = snapshots[-2]

    money_change = recent['money'] - previous['money']

    return {
        'daily_income_avg': money_change,
        'money_growth_rate': money_change / max(previous['money'], 1)
    }

def save_snapshot(state):
    """Save current state as snapshot for next comparison."""
    with open(SNAPSHOT_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def initialize_tracking_files():
    """Initialize empty tracking files on first run."""
    if not DIARY_PATH.exists():
        with open(DIARY_PATH, 'w') as f:
            json.dump({
                'entries': [],
                'meta': {
                    'created': datetime.now().isoformat(),
                    'total_sessions': 0,
                    'last_updated': None
                }
            }, f, indent=2)

    if not METRICS_PATH.exists():
        with open(METRICS_PATH, 'w') as f:
            json.dump({
                'snapshots': [],
                'trends': {},
                'meta': {
                    'tracking_started': datetime.now().isoformat(),
                    'total_snapshots': 0
                }
            }, f, indent=2)

def compute_time_rollups(entries):
    """
    Compute time-based aggregations for both game and real time.

    Args:
        entries (list): List of diary entries from diary.json

    Returns:
        dict: Rollup data structure with game_time and real_time aggregations
    """
    from collections import defaultdict
    from datetime import datetime as dt

    if not entries:
        return {
            'game_time': {},
            'real_time': {},
            'meta': {'total_entries': 0, 'generated_at': dt.now().isoformat()}
        }

    # Aggregate by different periods
    rollups = {
        'game_time': {
            'by_week': aggregate_by_game_weeks(entries),
            'by_season': aggregate_by_game_seasons(entries),
            'by_year': aggregate_by_game_years(entries)
        },
        'real_time': {
            'by_week': aggregate_by_real_weeks(entries),
            'by_month': aggregate_by_real_months(entries),
            'by_year': aggregate_by_real_years(entries)
        },
        'meta': {
            'total_entries': len(entries),
            'generated_at': dt.now().isoformat(),
            'game_date_range': get_game_date_range(entries),
            'real_date_range': get_real_date_range(entries)
        }
    }

    return rollups

def aggregate_by_game_weeks(entries):
    """Aggregate entries by 7-day game weeks."""
    from collections import defaultdict

    weeks = defaultdict(lambda: {
        'sessions': [],
        'money_change': 0,
        'xp_by_skill': defaultdict(int),
        'bundles_completed': 0,
        'days_played': 0
    })

    for entry in entries:
        end_parsed = entry.get('game_progress', {}).get('end_parsed')
        if not end_parsed:
            # Fall back to parsing the human-readable string
            end_str = entry.get('game_progress', {}).get('end')
            if end_str:
                end_parsed = parse_game_date(end_str)
            if not end_parsed:
                continue

        # Calculate week number: (year-1)*16 + (season_idx*4) + ((day-1)//7)
        season_idx = {'spring': 0, 'summer': 1, 'fall': 2, 'winter': 3}.get(end_parsed['season'], 0)
        week_in_season = (end_parsed['day'] - 1) // 7  # 0-3
        week_num = (end_parsed['year'] - 1) * 16 + season_idx * 4 + week_in_season

        # Create key: "Y{year}W{week}"
        key = f"Y{end_parsed['year']}W{week_in_season + 1}-{end_parsed['season'].title()}"

        # Aggregate data
        weeks[key]['sessions'].append(entry['session_id'])
        weeks[key]['money_change'] += entry.get('financial', {}).get('change', 0)
        weeks[key]['bundles_completed'] += entry.get('changes_detail', {}).get('bundles_completed', 0)
        weeks[key]['days_played'] += entry.get('game_progress', {}).get('days_played', 0)

        # Aggregate XP
        for skill, data in entry.get('changes_detail', {}).get('skill_changes', {}).items():
            weeks[key]['xp_by_skill'][skill] += data.get('xp_gained', 0)

    # Convert to list format
    result = []
    for key in sorted(weeks.keys()):
        data = weeks[key]
        result.append({
            'period': key,
            'sessions_count': len(data['sessions']),
            'money_change': data['money_change'],
            'xp_by_skill': dict(data['xp_by_skill']),
            'total_xp': sum(data['xp_by_skill'].values()),
            'bundles_completed': data['bundles_completed'],
            'days_played': data['days_played']
        })

    return result

def aggregate_by_game_seasons(entries):
    """Aggregate entries by 28-day game seasons."""
    from collections import defaultdict

    seasons = defaultdict(lambda: {
        'sessions': [],
        'money_change': 0,
        'xp_by_skill': defaultdict(int),
        'bundles_completed': 0,
        'days_played': 0
    })

    for entry in entries:
        end_parsed = entry.get('game_progress', {}).get('end_parsed')
        if not end_parsed:
            # Fall back to parsing the human-readable string
            end_str = entry.get('game_progress', {}).get('end')
            if end_str:
                end_parsed = parse_game_date(end_str)
            if not end_parsed:
                continue

        key = f"{end_parsed['season'].title()} Y{end_parsed['year']}"

        # Aggregate data
        seasons[key]['sessions'].append(entry['session_id'])
        seasons[key]['money_change'] += entry.get('financial', {}).get('change', 0)
        seasons[key]['bundles_completed'] += entry.get('changes_detail', {}).get('bundles_completed', 0)
        seasons[key]['days_played'] += entry.get('game_progress', {}).get('days_played', 0)

        for skill, data in entry.get('changes_detail', {}).get('skill_changes', {}).items():
            seasons[key]['xp_by_skill'][skill] += data.get('xp_gained', 0)

    # Convert to list
    result = []
    for key in sorted(seasons.keys(), key=lambda x: (int(x.split('Y')[1]), ['Spring', 'Summer', 'Fall', 'Winter'].index(x.split(' ')[0]))):
        data = seasons[key]
        result.append({
            'period': key,
            'sessions_count': len(data['sessions']),
            'money_change': data['money_change'],
            'xp_by_skill': dict(data['xp_by_skill']),
            'total_xp': sum(data['xp_by_skill'].values()),
            'bundles_completed': data['bundles_completed'],
            'days_played': data['days_played']
        })

    return result

def aggregate_by_game_years(entries):
    """Aggregate entries by game years."""
    from collections import defaultdict

    years = defaultdict(lambda: {
        'sessions': [],
        'money_change': 0,
        'xp_by_skill': defaultdict(int),
        'bundles_completed': 0,
        'days_played': 0
    })

    for entry in entries:
        end_parsed = entry.get('game_progress', {}).get('end_parsed')
        if not end_parsed:
            # Fall back to parsing the human-readable string
            end_str = entry.get('game_progress', {}).get('end')
            if end_str:
                end_parsed = parse_game_date(end_str)
            if not end_parsed:
                continue

        key = f"Year {end_parsed['year']}"

        years[key]['sessions'].append(entry['session_id'])
        years[key]['money_change'] += entry.get('financial', {}).get('change', 0)
        years[key]['bundles_completed'] += entry.get('changes_detail', {}).get('bundles_completed', 0)
        years[key]['days_played'] += entry.get('game_progress', {}).get('days_played', 0)

        for skill, data in entry.get('changes_detail', {}).get('skill_changes', {}).items():
            years[key]['xp_by_skill'][skill] += data.get('xp_gained', 0)

    result = []
    for key in sorted(years.keys(), key=lambda x: int(x.split()[1])):
        data = years[key]
        result.append({
            'period': key,
            'sessions_count': len(data['sessions']),
            'money_change': data['money_change'],
            'xp_by_skill': dict(data['xp_by_skill']),
            'total_xp': sum(data['xp_by_skill'].values()),
            'bundles_completed': data['bundles_completed'],
            'days_played': data['days_played']
        })

    return result

def aggregate_by_real_weeks(entries):
    """Aggregate entries by ISO calendar weeks."""
    from collections import defaultdict
    from datetime import datetime as dt

    weeks = defaultdict(lambda: {
        'sessions': [],
        'money_change': 0,
        'xp_by_skill': defaultdict(int),
        'bundles_completed': 0,
        'days_played': 0
    })

    for entry in entries:
        timestamp = entry.get('detected_at')
        if not timestamp:
            continue

        date = dt.fromisoformat(timestamp)
        iso_cal = date.isocalendar()
        key = f"{iso_cal[0]}-W{iso_cal[1]:02d}"  # "2025-W45"

        weeks[key]['sessions'].append(entry['session_id'])
        weeks[key]['money_change'] += entry.get('financial', {}).get('change', 0)
        weeks[key]['bundles_completed'] += entry.get('changes_detail', {}).get('bundles_completed', 0)
        weeks[key]['days_played'] += entry.get('game_progress', {}).get('days_played', 0)

        for skill, data in entry.get('changes_detail', {}).get('skill_changes', {}).items():
            weeks[key]['xp_by_skill'][skill] += data.get('xp_gained', 0)

    result = []
    for key in sorted(weeks.keys()):
        data = weeks[key]
        result.append({
            'period': key,
            'sessions_count': len(data['sessions']),
            'money_change': data['money_change'],
            'xp_by_skill': dict(data['xp_by_skill']),
            'total_xp': sum(data['xp_by_skill'].values()),
            'bundles_completed': data['bundles_completed'],
            'days_played': data['days_played']
        })

    return result

def aggregate_by_real_months(entries):
    """Aggregate entries by calendar months."""
    from collections import defaultdict
    from datetime import datetime as dt

    months = defaultdict(lambda: {
        'sessions': [],
        'money_change': 0,
        'xp_by_skill': defaultdict(int),
        'bundles_completed': 0,
        'days_played': 0
    })

    for entry in entries:
        timestamp = entry.get('detected_at')
        if not timestamp:
            continue

        date = dt.fromisoformat(timestamp)
        key = f"{date.year}-{date.month:02d}"  # "2025-11"

        months[key]['sessions'].append(entry['session_id'])
        months[key]['money_change'] += entry.get('financial', {}).get('change', 0)
        months[key]['bundles_completed'] += entry.get('changes_detail', {}).get('bundles_completed', 0)
        months[key]['days_played'] += entry.get('game_progress', {}).get('days_played', 0)

        for skill, data in entry.get('changes_detail', {}).get('skill_changes', {}).items():
            months[key]['xp_by_skill'][skill] += data.get('xp_gained', 0)

    result = []
    for key in sorted(months.keys()):
        data = months[key]
        result.append({
            'period': key,
            'sessions_count': len(data['sessions']),
            'money_change': data['money_change'],
            'xp_by_skill': dict(data['xp_by_skill']),
            'total_xp': sum(data['xp_by_skill'].values()),
            'bundles_completed': data['bundles_completed'],
            'days_played': data['days_played']
        })

    return result

def aggregate_by_real_years(entries):
    """Aggregate entries by calendar years."""
    from collections import defaultdict
    from datetime import datetime as dt

    years = defaultdict(lambda: {
        'sessions': [],
        'money_change': 0,
        'xp_by_skill': defaultdict(int),
        'bundles_completed': 0,
        'days_played': 0
    })

    for entry in entries:
        timestamp = entry.get('detected_at')
        if not timestamp:
            continue

        date = dt.fromisoformat(timestamp)
        key = str(date.year)

        years[key]['sessions'].append(entry['session_id'])
        years[key]['money_change'] += entry.get('financial', {}).get('change', 0)
        years[key]['bundles_completed'] += entry.get('changes_detail', {}).get('bundles_completed', 0)
        years[key]['days_played'] += entry.get('game_progress', {}).get('days_played', 0)

        for skill, data in entry.get('changes_detail', {}).get('skill_changes', {}).items():
            years[key]['xp_by_skill'][skill] += data.get('xp_gained', 0)

    result = []
    for key in sorted(years.keys()):
        data = years[key]
        result.append({
            'period': key,
            'sessions_count': len(data['sessions']),
            'money_change': data['money_change'],
            'xp_by_skill': dict(data['xp_by_skill']),
            'total_xp': sum(data['xp_by_skill'].values()),
            'bundles_completed': data['bundles_completed'],
            'days_played': data['days_played']
        })

    return result

def get_game_date_range(entries):
    """Get earliest and latest game dates from entries."""
    if not entries:
        return None

    dates = []
    for entry in entries:
        end_parsed = entry.get('game_progress', {}).get('end_parsed')
        if not end_parsed:
            # Fall back to parsing the human-readable string
            end_str = entry.get('game_progress', {}).get('end')
            if end_str:
                end_parsed = parse_game_date(end_str)
        if end_parsed:
            dates.append(end_parsed)

    if not dates:
        return None

    # Sort by year, season, day
    season_order = {'spring': 0, 'summer': 1, 'fall': 2, 'winter': 3}
    sorted_dates = sorted(dates, key=lambda d: (d['year'], season_order.get(d['season'], 0), d['day']))

    return {
        'earliest': sorted_dates[0],
        'latest': sorted_dates[-1]
    }

def get_real_date_range(entries):
    """Get earliest and latest real dates from entries."""
    if not entries:
        return None

    timestamps = [entry.get('detected_at') for entry in entries if entry.get('detected_at')]

    if not timestamps:
        return None

    return {
        'earliest': min(timestamps),
        'latest': max(timestamps)
    }

def generate_rollups_file():
    """Generate diary_rollups.json from current diary.json."""
    ROLLUPS_PATH = Path(r'C:\opt\stardew\diary_rollups.json')

    if not DIARY_PATH.exists():
        print("diary.json not found - cannot generate rollups")
        return False

    with open(DIARY_PATH, 'r') as f:
        diary = json.load(f)

    entries = diary.get('entries', [])

    if not entries:
        print("No entries in diary.json - skipping rollups generation")
        return False

    print(f"Generating rollups from {len(entries)} diary entries...")
    rollups = compute_time_rollups(entries)

    with open(ROLLUPS_PATH, 'w') as f:
        json.dump(rollups, f, indent=2)

    print(f"[OK] Generated diary_rollups.json:")
    print(f"  - Game weeks: {len(rollups['game_time']['by_week'])}")
    print(f"  - Game seasons: {len(rollups['game_time']['by_season'])}")
    print(f"  - Game years: {len(rollups['game_time']['by_year'])}")
    print(f"  - Real weeks: {len(rollups['real_time']['by_week'])}")
    print(f"  - Real months: {len(rollups['real_time']['by_month'])}")
    print(f"  - Real years: {len(rollups['real_time']['by_year'])}")

    return True

if __name__ == '__main__':
    result = track_session()
    print(f"\nStatus: {result['status']}")
    if result['status'] == 'session_recorded':
        print(f"Diary entry created successfully")
        # Generate rollups after recording session
        generate_rollups_file()
    sys.exit(0 if result['status'] != 'error' else 1)
