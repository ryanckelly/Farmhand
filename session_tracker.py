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

def generate_diary_entry(changes, old_state, new_state, bundle_readiness=None):
    """Generate a detailed diary entry from the changes detected."""
    entry = {
        'session_id': f"{datetime.now().strftime('%Y-%m-%d-%H%M')}",
        'detected_at': datetime.now().isoformat(),
        'game_progress': {
            'start': old_state['game_date_str'],
            'end': new_state['game_date_str'],
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

    # Days progression
    if changes['days_passed'] > 0:
        accomplishments.append(f"Progressed {changes['days_passed']} in-game day(s)")

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

    with open(DIARY_PATH, 'w') as f:
        json.dump(diary, f, indent=2)

def update_metrics(state):
    """Update metrics.json with new snapshot data."""
    with open(METRICS_PATH, 'r') as f:
        metrics = json.load(f)

    snapshot = {
        'date': datetime.now().isoformat(),
        'game_date': state['game_date_str'],
        'money': state['money'],
        'total_earned': state['total_earned'],
        'animals': state['animals']['total'],
        'skills': {k: v['level'] for k, v in state['skills'].items()},
        'bundles_complete': state.get('bundles', {}).get('complete_count', 0)
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

if __name__ == '__main__':
    result = track_session()
    print(f"\nStatus: {result['status']}")
    if result['status'] == 'session_recorded':
        print(f"Diary entry created successfully")
    sys.exit(0 if result['status'] != 'error' else 1)
