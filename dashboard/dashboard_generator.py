#!/usr/bin/env python3
"""
Farmhand Dashboard Generator

Generates an ASCII-style dashboard showing progress, financials, and momentum.
Part of the Stardew Valley Companion System.

Usage:
    python dashboard_generator.py              # Generate dashboard
    python dashboard_generator.py --preview    # Show preview in terminal
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from villager_aggregator import get_all_villagers_summary, get_villager_chart_data
from villager_database import get_all_villagers


class ASCIIRenderer:
    """Utilities for rendering ASCII art and terminal-style visualizations."""

    @staticmethod
    def progress_bar(percent, width=20):
        """
        Generate ASCII progress bar using simple ASCII characters.
        Example: [============........]  60%
        """
        filled = int(percent * width)
        empty = width - filled
        bar = '=' * filled + '.' * empty
        return f"[{bar}] {int(percent * 100):>3}%"

    @staticmethod
    def sparkline(values, width=None):
        """
        Generate Unicode sparkline chart using block characters.
        Example: ▂▃▅▆▇█▇▅
        """
        if not values:
            return ''

        # Unicode block characters for sparklines (8 levels)
        chars = '▁▂▃▄▅▆▇█'
        max_val = max(values) if max(values) > 0 else 1
        min_val = min(values)

        # Normalize to 0-7 range (8 levels)
        normalized = []
        for v in values:
            if max_val == min_val:
                norm = 3  # Middle value
            else:
                norm = int(((v - min_val) / (max_val - min_val)) * 7)
            normalized.append(norm)

        return ''.join(chars[n] for n in normalized)

    @staticmethod
    def format_number(num):
        """Format large numbers with commas."""
        return f"{int(num):,}g"

    @staticmethod
    def format_percent(value):
        """Format percent change with arrow."""
        if value > 0:
            return f"+{int(value*100)}%"
        elif value < 0:
            return f"{int(value*100)}%"
        else:
            return "0%"

    @staticmethod
    def box_line(text, width=50, align='left'):
        """Create a line within a box with padding.

        Dynamically adjusts spacing without truncation - CSS handles overflow.
        """
        # Calculate maximum text length based on alignment
        if align == 'left':
            max_length = width - 4  # Account for "║  " and "║"
            actual_length = len(text)

            # No truncation - calculate padding
            if actual_length <= max_length:
                padding = max_length - actual_length
                return f"║  {text}{' ' * padding}║"
            else:
                # Content too long, just add border without padding
                return f"║  {text}║"

        elif align == 'center':
            max_length = width - 2  # Account for "║" on both sides
            actual_length = len(text)

            # No truncation - calculate padding for centering
            if actual_length <= max_length:
                total_padding = max_length - actual_length
                left_padding = total_padding // 2
                right_padding = total_padding - left_padding
                return f"║{' ' * left_padding}{text}{' ' * right_padding}║"
            else:
                # Content too long, just center with borders
                return f"║{text}║"

        else:  # right
            max_length = width - 2  # Account for "║" on both sides
            actual_length = len(text)

            # No truncation - calculate padding
            if actual_length <= max_length:
                padding = max_length - actual_length
                return f"║{' ' * padding}{text}║"
            else:
                # Content too long, just add border
                return f"║{text}║"

    @staticmethod
    def separator(width=50):
        """Create a box separator line."""
        return f"╠{'═' * (width-2)}╣"

    @staticmethod
    def box_top(width=50):
        """Create top of box."""
        return f"╔{'═' * (width-2)}╗"

    @staticmethod
    def box_bottom(width=50):
        """Create bottom of box."""
        return f"╚{'═' * (width-2)}╝"

    @staticmethod
    def empty_line(width=50):
        """Create empty line in box."""
        return f"║{' ' * (width-2)}║"


class MomentumAnalyzer:
    """Analyzes session momentum and detects hot/cold streaks."""

    # Thresholds for hot/cold classification
    THRESHOLDS = {
        'bundles': {'hot': 1.5, 'cold': 0.0},
        'skills_xp': {'hot': 500, 'cold': 100},
        'money': {'hot': 40000, 'cold': 10000},
        'social': {'hot': 200, 'cold': 0},
        'museum': {'hot': 2, 'cold': 0}
    }

    def __init__(self, diary_entries):
        """Initialize with diary entries."""
        self.diary = diary_entries

    def calculate_momentum(self, window_size):
        """Calculate momentum for N most recent sessions."""
        if len(self.diary) < window_size:
            return {
                'error': f'Need at least {window_size} sessions',
                'available': len(self.diary),
                'hot_streaks': [],
                'cold_streaks': [],
                'rising_trends': [],
                'stalled_areas': []
            }

        recent = self.diary[-window_size:]

        momentum = {
            'window_size': window_size,
            'hot_streaks': [],
            'cold_streaks': [],
            'rising_trends': [],
            'stalled_areas': []
        }

        # Analyze different categories
        self._analyze_bundles(recent, momentum)
        self._analyze_skills(recent, momentum)
        self._analyze_money(recent, momentum)
        self._analyze_social(recent, momentum)
        self._analyze_museum(recent, momentum)

        return momentum

    def _analyze_bundles(self, sessions, momentum):
        """Analyze bundle completion momentum."""
        bundles = [s.get('changes_detail', {}).get('bundles_completed', 0) for s in sessions]
        avg_rate = sum(bundles) / len(sessions)

        if avg_rate >= self.THRESHOLDS['bundles']['hot']:
            momentum['hot_streaks'].append({
                'category': 'Bundles',
                'icon': '[HOT]',
                'description': f'Bundle completion (+{avg_rate:.1f}/session)'
            })
        elif avg_rate == self.THRESHOLDS['bundles']['cold']:
            momentum['cold_streaks'].append({
                'category': 'Bundles',
                'icon': '[COLD]',
                'description': f'No bundle progress in {len(sessions)} sessions'
            })

        # Check for rising trend
        if len(bundles) >= 3:
            first_half = sum(bundles[:len(bundles)//2])
            second_half = sum(bundles[len(bundles)//2:])
            if second_half > first_half and second_half > 0:
                momentum['rising_trends'].append({
                    'category': 'Bundles',
                    'icon': '[RISING]',
                    'description': f'Bundle momentum building ({first_half}->{second_half})'
                })

    def _analyze_skills(self, sessions, momentum):
        """Analyze skill progression momentum."""
        # Track total XP gained
        total_xp = 0
        skill_levels = {}

        for session in sessions:
            skill_changes = session.get('changes_detail', {}).get('skill_changes', {})
            for skill, data in skill_changes.items():
                if isinstance(data, dict):
                    xp = data.get('xp_gained', 0)
                    total_xp += xp

                    # Track level changes
                    old_level = data.get('old_level', 0)
                    new_level = data.get('new_level', 0)
                    if new_level > old_level:
                        if skill not in skill_levels:
                            skill_levels[skill] = []
                        skill_levels[skill].append((old_level, new_level))

        avg_xp = total_xp / len(sessions)

        if avg_xp >= self.THRESHOLDS['skills_xp']['hot']:
            momentum['hot_streaks'].append({
                'category': 'Skills',
                'icon': '[HOT]',
                'description': f'High XP gains (+{int(avg_xp)}/session)'
            })
        elif avg_xp < self.THRESHOLDS['skills_xp']['cold']:
            momentum['cold_streaks'].append({
                'category': 'Skills',
                'icon': '[COLD]',
                'description': f'Low skill progress ({int(avg_xp)} XP/session)'
            })

        # Report level ups
        for skill, levels in skill_levels.items():
            if len(levels) > 0:
                momentum['rising_trends'].append({
                    'category': skill.capitalize(),
                    'icon': '[RISING]',
                    'description': f'{skill.capitalize()} leveling up (gained {len(levels)} levels)'
                })

    def _analyze_money(self, sessions, momentum):
        """Analyze financial momentum."""
        money_changes = [s.get('financial', {}).get('change', 0) for s in sessions]
        avg_earnings = sum(money_changes) / len(sessions)

        if avg_earnings >= self.THRESHOLDS['money']['hot']:
            momentum['hot_streaks'].append({
                'category': 'Money',
                'icon': '[HOT]',
                'description': f'Strong earnings (+{int(avg_earnings):,}g/session)'
            })
        elif avg_earnings < self.THRESHOLDS['money']['cold']:
            if avg_earnings < 0:
                momentum['cold_streaks'].append({
                    'category': 'Money',
                    'icon': '[COLD]',
                    'description': f'Net losses ({int(avg_earnings):,}g/session)'
                })
            else:
                momentum['stalled_areas'].append({
                    'category': 'Money',
                    'icon': '[STALLED]',
                    'description': f'Low income ({int(avg_earnings):,}g/session)'
                })

    def _analyze_social(self, sessions, momentum):
        """Analyze social/friendship momentum."""
        total_heart_points = 0
        new_milestones = []

        for session in sessions:
            friendship_changes = session.get('changes_detail', {}).get('friendship_changes', {})
            for npc, data in friendship_changes.items():
                if isinstance(data, dict):
                    points = data.get('points_gained', 0)
                    total_heart_points += points

                    # Check for heart milestones
                    old_hearts = data.get('old_hearts', 0)
                    new_hearts = data.get('new_hearts', 0)
                    if new_hearts >= 8 and new_hearts > old_hearts:
                        new_milestones.append(f"{npc} ({new_hearts} hearts)")

        avg_points = total_heart_points / len(sessions)

        if avg_points >= self.THRESHOLDS['social']['hot']:
            momentum['hot_streaks'].append({
                'category': 'Social',
                'icon': '[HOT]',
                'description': f'Strong relationships (+{int(avg_points)} pts/session)'
            })
        elif avg_points <= self.THRESHOLDS['social']['cold']:
            momentum['cold_streaks'].append({
                'category': 'Social',
                'icon': '[COLD]',
                'description': f'No relationship progress'
            })

        # Report milestones
        for milestone in new_milestones[:3]:  # Top 3
            momentum['rising_trends'].append({
                'category': 'Friendship',
                'icon': '[RISING]',
                'description': f'{milestone}'
            })

    def _analyze_museum(self, sessions, momentum):
        """Analyze museum donation momentum."""
        # Check for museum donations in accomplishments
        total_donations = 0

        for session in sessions:
            accomplishments = session.get('key_accomplishments', [])
            for acc in accomplishments:
                if isinstance(acc, str) and 'museum' in acc.lower():
                    # Try to extract number
                    import re
                    match = re.search(r'(\d+)', acc)
                    if match:
                        total_donations += int(match.group(1))

        avg_donations = total_donations / len(sessions)

        if avg_donations >= self.THRESHOLDS['museum']['hot']:
            momentum['hot_streaks'].append({
                'category': 'Museum',
                'icon': '[HOT]',
                'description': f'Active collecting (+{avg_donations:.1f}/session)'
            })
        elif avg_donations == 0:
            momentum['stalled_areas'].append({
                'category': 'Museum',
                'icon': '[STALLED]',
                'description': f'No museum donations in {len(sessions)} sessions'
            })


class DashboardGenerator:
    """Main dashboard generator - extracts data and renders HTML."""

    def __init__(self, base_path=None):
        """Initialize generator with path to save files."""
        # Default to parent directory (where save files are located)
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Dashboard is in dashboard/ subdirectory, data files are in parent
            self.base_path = Path(__file__).parent.parent
        self.snapshot = None
        self.diary = None
        self.metrics = None

    def load_json(self, filename):
        """Load JSON file with error handling."""
        filepath = self.base_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Required file not found: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in {filename}: {e.msg}",
                e.doc,
                e.pos
            )

    def save_json(self, filename, data):
        """Save JSON file with pretty formatting."""
        # Save output files in the dashboard directory
        output_dir = Path(__file__).parent
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_all_data(self):
        """Load all required JSON files."""
        print("[*] Loading save data...")
        self.snapshot = self.load_json('save_snapshot.json')
        self.diary = self.load_json('diary.json')
        self.metrics = self.load_json('metrics.json')
        print("[+] All files loaded successfully")

    def extract_unlocks(self):
        """Extract unlock completion percentages."""
        unlocks = {}

        # Community Center bundles
        bundles = self.snapshot.get('bundles', {})
        complete = bundles.get('complete_count', 0)
        total = bundles.get('total_count', 31)
        unlocks['community_center'] = {
            'completed': complete,
            'total': total,
            'percent': complete / total if total > 0 else 0
        }

        # Museum donations
        museum = self.snapshot.get('museum', {})
        donated = museum.get('total_donated', 0)
        total_artifacts = 95  # Total museum items in base game
        unlocks['museum'] = {
            'donated': donated,
            'total': total_artifacts,
            'percent': donated / total_artifacts
        }

        # Cooking recipes (approximate - may not be in save)
        # Total recipes in game: 74 (as of 1.6)
        recipes_known = len(self.snapshot.get('cooking_recipes', []))
        total_recipes = 74
        unlocks['cooking'] = {
            'known': recipes_known,
            'total': total_recipes,
            'percent': recipes_known / total_recipes if total_recipes > 0 else 0
        }

        # Friendships at 8+ hearts
        friendships = self.snapshot.get('friendships', {})
        high_friendship_count = sum(
            1 for npc_data in friendships.values()
            if isinstance(npc_data, dict) and npc_data.get('hearts', 0) >= 8
        )
        total_npcs = 32  # Marriageable + non-marriageable NPCs
        unlocks['friendships_8plus'] = {
            'count': high_friendship_count,
            'total': total_npcs,
            'percent': high_friendship_count / total_npcs
        }

        # Skills at level 10
        skills = self.snapshot.get('skills', {})
        maxed_skills = sum(
            1 for skill_name, skill_data in skills.items()
            if isinstance(skill_data, dict) and skill_data.get('level', 0) >= 10
        )
        total_skills = 5  # Farming, Fishing, Foraging, Mining, Combat
        unlocks['skills_maxed'] = {
            'count': maxed_skills,
            'total': total_skills,
            'percent': maxed_skills / total_skills
        }

        # Golden Walnuts (Ginger Island)
        unlock_data = self.snapshot.get('unlocks', {})
        walnuts_found = unlock_data.get('golden_walnuts_found', 0)
        total_walnuts = 130  # Total Golden Walnuts in game
        unlocks['golden_walnuts'] = {
            'found': walnuts_found,
            'total': total_walnuts,
            'percent': walnuts_found / total_walnuts if total_walnuts > 0 else 0
        }

        # Skull Cavern deepest level
        skull_depth = unlock_data.get('skull_cavern_level', 0)
        unlocks['skull_cavern_depth'] = {
            'deepest': skull_depth,
            'milestone_100': skull_depth >= 100,
            'milestone_200': skull_depth >= 200
        }

        return unlocks

    def extract_financials(self):
        """Extract financial metrics and trends."""
        financials = {}

        # Current balance
        financials['current_balance'] = self.snapshot.get('money', 0)

        # Get diary entries
        entries = self.diary.get('entries', [])

        if not entries:
            # No history - return minimal data
            return {
                'current_balance': financials['current_balance'],
                'daily_average': 0,
                'weekly_trend': 0,
                'best_day': {'amount': 0, 'date': 'N/A'},
                'sparkline_data': []
            }

        # Calculate daily average from recent sessions
        recent_7 = entries[-7:] if len(entries) >= 7 else entries
        total_money_change = sum(
            entry.get('financial', {}).get('change', 0)
            for entry in recent_7
        )
        total_days = sum(
            entry.get('game_progress', {}).get('days_played', 0)
            for entry in recent_7
        )

        daily_avg = total_money_change / total_days if total_days > 0 else 0
        financials['daily_average'] = int(daily_avg)

        # Weekly trend (compare last 7 sessions to previous 7)
        if len(entries) >= 14:
            prev_7 = entries[-14:-7]
            recent_7 = entries[-7:]

            prev_avg = sum(e.get('financial', {}).get('change', 0) for e in prev_7) / 7
            recent_avg = sum(e.get('financial', {}).get('change', 0) for e in recent_7) / 7

            if prev_avg != 0:
                financials['weekly_trend'] = (recent_avg - prev_avg) / prev_avg
            else:
                financials['weekly_trend'] = 0
        else:
            financials['weekly_trend'] = 0

        # Find best earning day
        best_day = max(
            entries,
            key=lambda e: e.get('financial', {}).get('change', 0),
            default={}
        )

        financials['best_day'] = {
            'amount': best_day.get('financial', {}).get('change', 0),
            'date': best_day.get('game_progress', {}).get('end', 'N/A')
        }

        # Generate sparkline data (last 7 sessions)
        money_changes = [
            entry.get('financial', {}).get('change', 0)
            for entry in recent_7
        ]

        # Normalize to 0-1 range for sparkline
        if money_changes and max(money_changes) > 0:
            max_val = max(money_changes)
            financials['sparkline_data'] = [
                change / max_val for change in money_changes
            ]
        else:
            financials['sparkline_data'] = [0] * len(money_changes)

        return financials

    def render_compact_dashboard(self, state):
        """Render a compact plain-text dashboard for terminal display with ANSI colors."""
        lines = []

        # ANSI color codes
        GREEN = '\033[92m'
        RESET = '\033[0m'

        # Header - simple equals signs, no fancy box chars
        lines.append("=" * 75)
        lines.append("FARMHAND".center(70))
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Game Date: {state['game_date']}")
        lines.append(f"Balance: {ASCIIRenderer.format_number(state['financials']['current_balance'])}")
        lines.append("")

        # PROGRESSION - with ALL items and visual progress bars
        lines.append("PROGRESSION")
        lines.append("-" * 70)
        unlocks = state['unlocks']

        # Community Center
        cc = unlocks['community_center']
        bar = ASCIIRenderer.progress_bar(cc['percent'], width=20)
        lines.append(f"  Community Center: {cc['completed']}/{cc['total']}  {bar}")

        # Museum
        mus = unlocks['museum']
        bar = ASCIIRenderer.progress_bar(mus['percent'], width=20)
        lines.append(f"  Museum Donations: {mus['donated']}/{mus['total']}  {bar}")

        # Cooking
        cook = unlocks['cooking']
        bar = ASCIIRenderer.progress_bar(cook['percent'], width=20)
        lines.append(f"  Cooking Recipes:  {cook['known']}/{cook['total']}  {bar}")

        # Friendships
        friends = unlocks['friendships_8plus']
        bar = ASCIIRenderer.progress_bar(friends['percent'], width=20)
        lines.append(f"  Friendships 8+:   {friends['count']}/{friends['total']}  {bar}")

        # Skills
        skills = unlocks['skills_maxed']
        bar = ASCIIRenderer.progress_bar(skills['percent'], width=20)
        lines.append(f"  Skills Maxed:     {skills['count']}/{skills['total']}  {bar}")
        lines.append("")

        # FINANCIAL TRENDS - new section
        lines.append("FINANCIAL TRENDS")
        lines.append("-" * 70)
        fin = state['financials']

        # Daily average with trend
        daily_avg = ASCIIRenderer.format_number(fin['daily_average'])
        trend = ASCIIRenderer.format_percent(fin['weekly_trend'])
        if fin['weekly_trend'] > 0:
            arrow = "^"
        elif fin['weekly_trend'] < 0:
            arrow = "v"
        else:
            arrow = "-"
        lines.append(f"  Daily Average:    {daily_avg}/day {arrow} {trend}")

        # Best day
        best = ASCIIRenderer.format_number(fin['best_day']['amount'])
        lines.append(f"  Best Day:         {best} on {fin['best_day']['date']}")
        lines.append("")

        # MOMENTUM - 3 session
        lines.append("MOMENTUM (Last 3 Sessions)")
        lines.append("-" * 70)
        mom3 = state['momentum_3session']
        if mom3.get('error'):
            lines.append(f"  {mom3['error']} (have {mom3['available']})")
        else:
            shown = False
            for streak in mom3.get('hot_streaks', [])[:2]:
                lines.append(f"  [HOT] {streak['category']}: {streak['description']}")
                shown = True
            for streak in mom3.get('cold_streaks', [])[:2]:
                lines.append(f"  [COLD] {streak['category']}: {streak['description']}")
                shown = True
            if not shown:
                lines.append("  Moderate progress")
        lines.append("")

        # TRENDS - 7 session
        lines.append("TRENDS (Last 7 Sessions)")
        lines.append("-" * 70)
        mom7 = state['momentum_7session']
        if mom7.get('error'):
            lines.append(f"  {mom7['error']} (have {mom7['available']})")
        else:
            shown = False
            for trend in mom7.get('rising_trends', [])[:2]:
                lines.append(f"  [RISING] {trend['category']}: {trend['description']}")
                shown = True
            for stall in mom7.get('stalled_areas', [])[:2]:
                lines.append(f"  [STALLED] {stall['category']}: {stall['description']}")
                shown = True
            if not shown:
                lines.append("  Steady progress")
        lines.append("")

        lines.append("=" * 70)

        # Join all lines, then wrap in color codes
        output = '\n'.join(lines)
        output = GREEN + output + RESET

        return output

    def render_ascii_dashboard(self, state, colored=False):
        """Render the complete ASCII dashboard as text.

        Args:
            state: Dashboard state data
            colored: If True, wrap output in ANSI green color codes for terminal display
        """
        r = ASCIIRenderer()
        lines = []

        # ANSI color codes (only used if colored=True)
        GREEN = '\033[92m' if colored else ''
        RESET = '\033[0m' if colored else ''

        # Header
        lines.append(r.box_top())
        lines.append(r.box_line("FARMHAND", align='center'))

        timestamp = datetime.fromisoformat(state['generated_at']).strftime('%Y-%m-%d %H:%M:%S')
        header_info = f"Generated: {timestamp} | {state['game_date']}"
        lines.append(r.box_line(header_info, align='center'))
        lines.append(r.separator())
        lines.append(r.empty_line())

        # UNLOCKS SECTION
        lines.append(r.box_line("UNLOCKS PROGRESS"))
        lines.append(r.box_line("─" * 16))

        unlocks = state['unlocks']

        # Community Center
        cc = unlocks['community_center']
        bar = r.progress_bar(cc['percent'])
        line = f"Community Center  {bar} ({cc['completed']}/{cc['total']})"
        lines.append(r.box_line(line))

        # Museum
        mus = unlocks['museum']
        bar = r.progress_bar(mus['percent'])
        line = f"Museum Collection {bar} ({mus['donated']}/{mus['total']})"
        lines.append(r.box_line(line))

        # Cooking
        cook = unlocks['cooking']
        bar = r.progress_bar(cook['percent'])
        line = f"Cooking Recipes   {bar} ({cook['known']}/{cook['total']})"
        lines.append(r.box_line(line))

        # Friendships
        friends = unlocks['friendships_8plus']
        bar = r.progress_bar(friends['percent'])
        line = f"Max Friendships   {bar} ({friends['count']}/{friends['total']})"
        lines.append(r.box_line(line))

        # Skills
        skills = unlocks['skills_maxed']
        bar = r.progress_bar(skills['percent'])
        line = f"Master Skills     {bar} ({skills['count']}/{skills['total']})"
        lines.append(r.box_line(line))

        # Golden Walnuts
        walnuts = unlocks['golden_walnuts']
        bar = r.progress_bar(walnuts['percent'])
        line = f"Golden Walnuts    {bar} ({walnuts['found']}/{walnuts['total']})"
        lines.append(r.box_line(line))

        # Skull Cavern
        skull = unlocks['skull_cavern_depth']
        milestone = "✓ 200+" if skull['milestone_200'] else "✓ 100+" if skull['milestone_100'] else ""
        line = f"Skull Cavern      Floor {skull['deepest']} {milestone}".strip()
        lines.append(r.box_line(line))

        lines.append(r.empty_line())

        # FINANCIALS SECTION
        lines.append(r.box_line("FINANCIAL TRENDS"))
        lines.append(r.box_line("─" * 16))

        fin = state['financials']

        # Current balance
        balance = r.format_number(fin['current_balance'])
        lines.append(r.box_line(f"Current Balance:  {balance}"))

        # Daily average
        daily_avg = r.format_number(fin['daily_average'])
        trend = r.format_percent(fin['weekly_trend'])
        if fin['weekly_trend'] > 0:
            arrow = "^"
        elif fin['weekly_trend'] < 0:
            arrow = "v"
        else:
            arrow = "-"
        lines.append(r.box_line(f"Daily Average:    {daily_avg}/day {arrow} {trend}"))

        # Best day
        best = r.format_number(fin['best_day']['amount'])
        lines.append(r.box_line(f"Best Day:         {best} on {fin['best_day']['date']}"))

        lines.append(r.empty_line())

        # MOMENTUM SECTION
        lines.append(r.box_line("MOMENTUM ANALYSIS"))
        lines.append(r.box_line("─" * 17))

        # 3-session momentum
        mom3 = state['momentum_3session']
        lines.append(r.box_line(""))
        lines.append(r.box_line("=== 3-SESSION MOMENTUM ==="))

        if mom3.get('error'):
            lines.append(r.box_line(f"  {mom3['error']} (have {mom3['available']})"))
        else:
            # Hot streaks
            if mom3['hot_streaks']:
                for streak in mom3['hot_streaks'][:3]:  # Top 3
                    icon = streak['icon']
                    desc = streak['description']
                    lines.append(r.box_line(f"  {icon} {desc}"))

            # Cold streaks
            if mom3['cold_streaks']:
                for streak in mom3['cold_streaks'][:3]:  # Top 3
                    icon = streak['icon']
                    desc = streak['description']
                    lines.append(r.box_line(f"  {icon} {desc}"))

            if not mom3['hot_streaks'] and not mom3['cold_streaks']:
                lines.append(r.box_line("  Moderate progress across all areas"))

        # 7-session momentum
        mom7 = state['momentum_7session']
        lines.append(r.box_line(""))
        lines.append(r.box_line("=== 7-SESSION MOMENTUM ==="))

        if mom7.get('error'):
            lines.append(r.box_line(f"  {mom7['error']} (have {mom7['available']})"))
        else:
            # Rising trends
            if mom7['rising_trends']:
                for trend in mom7['rising_trends'][:3]:  # Top 3
                    icon = trend['icon']
                    desc = trend['description']
                    lines.append(r.box_line(f"  {icon} {desc}"))

            # Stalled areas
            if mom7['stalled_areas']:
                for stalled in mom7['stalled_areas'][:3]:  # Top 3
                    icon = stalled['icon']
                    desc = stalled['description']
                    lines.append(r.box_line(f"  {icon} {desc}"))

            if not mom7['rising_trends'] and not mom7['stalled_areas']:
                lines.append(r.box_line("  Steady progress - no major changes"))

        lines.append(r.box_line(""))

        # Footer
        lines.append(r.box_bottom())

        # If colored, prepend GREEN to each line and append RESET at the very end
        if colored:
            lines = [GREEN + line for line in lines]
            return '\n'.join(lines) + RESET
        else:
            return '\n'.join(lines)

    def render_navigation(self, current_page='dashboard'):
        """Render vintage terminal-style navigation."""
        dashboard_style = 'active' if current_page == 'dashboard' else ''
        trends_style = 'active' if current_page == 'trends' else ''

        return f"""
    <div class="nav-container">
        <span class="nav-bracket">[</span>
        <a href="/dashboard" class="nav-link {dashboard_style}">DASHBOARD</a>
        <span class="nav-separator">|</span>
        <a href="/trends" class="nav-link {trends_style}">TRENDS</a>
        <span class="nav-bracket">]</span>
    </div>
"""

    def render_html(self, state, output_filename='dashboard.html', with_nav=True):
        """Render dashboard as HTML file."""
        # Get ASCII content
        ascii_content = self.render_ascii_dashboard(state)

        # Strip ASCII box characters since CSS provides border
        box_chars = ['╔', '╗', '╚', '╝', '║', '╠', '╣', '═']
        for char in box_chars:
            ascii_content = ascii_content.replace(char, '')

        # Clean up extra spaces and empty lines from removed borders
        lines = ascii_content.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        ascii_content = '\n'.join(lines)

        # Escape for HTML
        html_content = ascii_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Determine current page for navigation
        current_page = 'dashboard' if 'dashboard' in output_filename else 'trends'

        # Add navigation if enabled
        nav_html = self.render_navigation(current_page) if with_nav else ''

        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farmhand Dashboard</title>
    <style>
        body {{
            background: #1e1e1e;
            color: #00ff00;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            padding: 20px;
            margin: 0;
            line-height: 1.4;
        }}
        .nav-container {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 16px;
            font-weight: bold;
        }}
        .nav-bracket {{
            color: #00ff00;
        }}
        .nav-separator {{
            color: #00ff00;
            margin: 0 10px;
        }}
        .nav-link {{
            color: #00ff00;
            text-decoration: none;
            padding: 5px 10px;
            transition: all 0.2s;
        }}
        .nav-link:hover {{
            color: #ffd700;
            text-shadow: 0 0 10px #ffd700;
        }}
        .nav-link.active {{
            color: #ffd700;
            font-weight: bold;
        }}
        .dashboard-container {{
            margin: 0 auto;
            max-width: 800px;
            width: 95%;
            padding: 20px;
            box-sizing: border-box;
            border: 3px solid #00ff00;
            border-radius: 8px;
            font-size: clamp(10px, 2.5vw, 14px);
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            text-align: left;
        }}
        @media (max-width: 768px) {{
            .dashboard-container {{
                font-size: clamp(8px, 3vw, 12px);
            }}
        }}
        .header {{
            color: #ffd700;
            font-weight: bold;
        }}
        .chart-container {{
            text-align: center;
            margin: 20px auto;
            max-width: 90%;
        }}
        .chart-image {{
            max-width: 100%;
            height: auto;
            border: 2px solid #00ff00;
            border-radius: 4px;
        }}
        .chart-title {{
            color: #ffd700;
            font-size: 16px;
            font-weight: bold;
            margin: 15px 0 10px 0;
        }}
    </style>
</head>
<body>
    {nav_html}
    <div class="dashboard-container">{html_content}</div>
</body>
</html>"""

        # Save file in dashboard directory
        output_dir = Path(__file__).parent
        output_path = output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)

    def render_trends_page(self, state, use_chartjs=True):
        """Generate trends page with charts."""
        # Create text header (CSS border replaces ASCII box)
        lines = []
        lines.append("TRENDS & ANALYTICS")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {state['game_date']}")
        lines.append("")
        lines.append("Session-by-session analysis of your farm progress")

        ascii_header = '\n'.join(lines)
        html_header = ascii_header.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Build trends HTML with navigation
        nav_html = self.render_navigation('trends')

        if use_chartjs:
            # Load diary data to embed
            diary_data = json.dumps(self.diary)

            # Load rollup data if available
            rollups_path = Path(r'C:\opt\stardew\diary_rollups.json')
            if rollups_path.exists():
                with open(rollups_path, 'r') as f:
                    rollups_data = json.load(f)
                rollups_data_json = json.dumps(rollups_data)
            else:
                # Fallback to empty rollups structure
                rollups_data_json = json.dumps({
                    'game_time': {},
                    'real_time': {},
                    'meta': {'total_entries': 0}
                })

            # Get villager data for chip bar
            villagers_summary = get_all_villagers_summary()
            villagers_data_json = json.dumps(villagers_summary)

            # Generate villager chip bar HTML
            villager_chips_html = ""
            for villager in villagers_summary:
                is_active = "active" if villager['name'] == "Abigail" else ""
                villager_chips_html += f"""
        <div class="villager-chip {is_active}" data-villager="{villager['name']}">
            <img src="/portraits/{villager['name']}.png" alt="{villager['name']}" class="villager-portrait" />
            <div class="villager-name">{villager['name']}</div>
            <div class="villager-hearts">{villager['hearts']}♥</div>
        </div>"""

            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farmhand Dashboard - Trends</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            background: #1e1e1e;
            color: #00ff00;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            padding: 20px;
            margin: 0;
            line-height: 1.4;
        }}
        .nav-container {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 16px;
            font-weight: bold;
        }}
        .nav-bracket {{
            color: #00ff00;
        }}
        .nav-separator {{
            color: #00ff00;
            margin: 0 10px;
        }}
        .nav-link {{
            color: #00ff00;
            text-decoration: none;
            padding: 5px 10px;
            transition: all 0.2s;
        }}
        .nav-link:hover {{
            color: #ffd700;
            text-shadow: 0 0 10px #ffd700;
        }}
        .nav-link.active {{
            color: #ffd700;
            font-weight: bold;
        }}
        .dashboard-container {{
            margin: 0 auto 20px auto;
            max-width: 800px;
            width: 95%;
            padding: 20px;
            box-sizing: border-box;
            border: 3px solid #00ff00;
            border-radius: 8px;
            font-size: clamp(10px, 2.5vw, 14px);
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .dashboard-container {{
                font-size: clamp(8px, 3vw, 12px);
            }}
        }}
        .filter-container {{
            max-width: 800px;
            width: 95%;
            box-sizing: border-box;
            margin: 0 auto 20px auto;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 4px;
        }}
        .filter-primary {{
            display: flex;
            align-items: center;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}
        .filter-label {{
            color: #ffd700;
            font-weight: bold;
            font-size: 14px;
        }}
        .quick-filter-select {{
            background: rgba(0, 255, 0, 0.2);
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px 40px 8px 12px;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            min-width: 180px;
            transition: all 0.2s;
        }}
        .quick-filter-select:hover {{
            background: rgba(0, 255, 0, 0.3);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }}
        .quick-filter-select:focus {{
            outline: 2px solid #ffd700;
            outline-offset: 2px;
        }}
        .filter-button {{
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
            border: 2px solid #00ff00;
            padding: 8px 16px;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s;
        }}
        .filter-button:hover {{
            background: rgba(0, 255, 0, 0.3);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }}
        .filter-button.active {{
            background: rgba(255, 215, 0, 0.2);
            border-color: #ffd700;
            color: #ffd700;
        }}
        .filter-advanced {{
            margin-top: 10px;
        }}
        .advanced-toggle {{
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid rgba(0, 255, 0, 0.3);
            color: #00ff00;
            padding: 8px 12px;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            cursor: pointer;
            border-radius: 4px;
            width: 100%;
            text-align: left;
            transition: all 0.2s;
        }}
        .advanced-toggle:hover {{
            background: rgba(0, 255, 0, 0.2);
        }}
        .advanced-toggle .toggle-icon {{
            display: inline-block;
            transition: transform 0.3s;
        }}
        .advanced-toggle[aria-expanded="true"] .toggle-icon {{
            transform: rotate(180deg);
        }}
        .advanced-content {{
            margin-top: 10px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(0, 255, 0, 0.2);
            border-radius: 4px;
        }}
        .aggregation-controls {{
            border: none;
            padding: 0;
            margin: 0;
        }}
        .aggregation-controls legend {{
            color: #ffd700;
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .aggregation-buttons {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
            margin-bottom: 10px;
        }}
        .agg-btn {{
            background: rgba(0, 255, 0, 0.1);
            border: 2px solid rgba(0, 255, 0, 0.3);
            color: #00ff00;
            padding: 8px 16px;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 20px;
            transition: all 0.2s;
            min-width: 80px;
        }}
        .agg-btn:hover {{
            background: rgba(0, 255, 0, 0.2);
            border-color: rgba(0, 255, 0, 0.5);
        }}
        .agg-btn.active {{
            background: rgba(255, 215, 0, 0.2);
            border-color: #ffd700;
            color: #ffd700;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }}
        .agg-help-text {{
            color: rgba(0, 255, 0, 0.7);
            font-size: 11px;
            text-align: center;
            margin: 0;
            font-style: italic;
        }}
        .chart-grid {{
            display: flex;
            flex-direction: column;
            gap: 30px;
            max-width: 800px;
            width: 95%;
            margin: 30px auto;
            box-sizing: border-box;
        }}
        .chart-container {{
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 4px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            width: 100%;
            margin: 0 auto;
            box-sizing: border-box;
        }}
        .chart-container canvas {{
            max-width: 100%;
            height: auto;
        }}
        .chart-title {{
            color: #ffd700;
            font-size: 16px;
            font-weight: bold;
            margin: 0 0 15px 0;
            text-transform: uppercase;
            text-align: center;
        }}
        .villager-chip-bar {{
            display: flex;
            overflow-x: auto;
            gap: 12px;
            padding: 15px 10px;
            margin: 20px auto;
            max-width: 800px;
            width: 95%;
            box-sizing: border-box;
            background: rgba(0, 0, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 4px;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }}
        .villager-chip-bar::-webkit-scrollbar {{
            height: 8px;
        }}
        .villager-chip-bar::-webkit-scrollbar-track {{
            background: rgba(0, 255, 0, 0.1);
            border-radius: 4px;
        }}
        .villager-chip-bar::-webkit-scrollbar-thumb {{
            background: #00ff00;
            border-radius: 4px;
        }}
        .villager-chip {{
            flex-shrink: 0;
            width: 80px;
            text-align: center;
            cursor: pointer;
            opacity: 0.5;
            transition: all 0.3s ease;
            padding: 5px;
        }}
        .villager-chip:hover {{
            opacity: 0.8;
            transform: scale(1.05);
        }}
        .villager-chip.active {{
            opacity: 1;
            filter: drop-shadow(0 0 10px #ffd700);
        }}
        .villager-portrait {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: 3px solid #00ff00;
            display: block;
            margin: 0 auto 5px auto;
            transition: all 0.3s ease;
            object-fit: cover;
            background: rgba(0, 0, 0, 0.5);
        }}
        .villager-chip.active .villager-portrait {{
            border-color: #ffd700;
            border-width: 4px;
        }}
        .villager-name {{
            font-size: 11px;
            color: #00ff00;
            margin-top: 3px;
        }}
        .villager-hearts {{
            font-size: 12px;
            color: #ffd700;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    {nav_html}
    <div class="dashboard-container">{html_header}</div>

    <div class="filter-container">
        <div class="filter-primary">
            <label class="filter-label">Filter:</label>
            <select id="quickFilter" class="quick-filter-select">
                <option value="all">All Sessions</option>
                <option value="5">Last 5 Sessions</option>
                <option value="10" selected>Last 10 Sessions</option>
                <option value="20">Last 20 Sessions</option>
                <option value="this-week-real">This Week (real)</option>
                <option value="this-month-real">This Month (real)</option>
                <option value="this-season-game">This Season (game)</option>
                <option value="this-year-game">This Year (game)</option>
                <option value="custom">Custom Range...</option>
            </select>
            <button id="resetFilter" class="filter-button">Reset</button>
            <button id="xAxisToggle" class="filter-button">X-Axis: Game Dates</button>
        </div>

        <div class="filter-advanced" id="advancedPanel">
            <button class="advanced-toggle" id="advancedToggle" aria-expanded="false">
                <span class="toggle-icon">▼</span> Advanced Filters
            </button>

            <div class="advanced-content" id="advancedContent" hidden>
                <fieldset class="aggregation-controls">
                    <legend>Group by Time Period:</legend>
                    <div class="aggregation-buttons" id="aggregationButtons">
                        <button class="agg-btn active" data-level="session">Session</button>
                        <button class="agg-btn" data-level="day">Day</button>
                        <button class="agg-btn" data-level="week">Week</button>
                        <button class="agg-btn" data-level="period" data-game="season" data-real="month">Season/Month</button>
                        <button class="agg-btn" data-level="year">Year</button>
                    </div>
                    <p class="agg-help-text" id="aggHelpText">
                        💡 Currently grouping by GAME time. Switch X-Axis for real-world time.
                    </p>
                </fieldset>
            </div>
        </div>
    </div>

    <div class="chart-grid">
        <div class="chart-container">
            <div class="chart-title">Net Money Change</div>
            <canvas id="moneyChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">XP Gains by Skill</div>
            <canvas id="xpBySkillChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Total XP Per Session</div>
            <canvas id="totalXPChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Villager Relationships</div>
            <div class="villager-chip-bar" id="villagerChipBar">
{villager_chips_html}
            </div>
            <canvas id="relationshipChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Community Center Bundles</div>
            <canvas id="bundlesChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Total Money Over Sessions</div>
            <canvas id="cumulativeMoneyChart"></canvas>
        </div>
    </div>

    <script>
        // Embed diary data
        const diaryData = {diary_data};

        // Embed rollup data
        const rollupData = {rollups_data_json};

        // Embed villager data
        const villagersData = {villagers_data_json};

        // Store selected villager (default: Abigail)
        let selectedVillager = localStorage.getItem('selectedVillager') || 'Abigail';

        // Villager chip selection handler
        document.addEventListener('DOMContentLoaded', function() {{
            const chips = document.querySelectorAll('.villager-chip');

            chips.forEach(chip => {{
                chip.addEventListener('click', function() {{
                    const villagerName = this.dataset.villager;

                    // Update active state
                    chips.forEach(c => c.classList.remove('active'));
                    this.classList.add('active');

                    // Save selection
                    selectedVillager = villagerName;
                    localStorage.setItem('selectedVillager', villagerName);

                    // Scroll chip into view
                    this.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});

                    // Update relationship chart using window function
                    if (window.refreshRelationshipChart) {{
                        window.refreshRelationshipChart(villagerName);
                    }}
                }});
            }});

            // Set initial selection from localStorage
            if (selectedVillager !== 'Abigail') {{
                const savedChip = document.querySelector(`[data-villager="${{selectedVillager}}"]`);
                if (savedChip) {{
                    document.querySelector('.villager-chip.active')?.classList.remove('active');
                    savedChip.classList.add('active');
                    savedChip.scrollIntoView({{ behavior: 'auto', block: 'nearest', inline: 'center' }});
                }}
            }}
        }});

        // ============================================================
        // ADVANCED DATE FILTERING SYSTEM
        // Handles quick filters, aggregation controls, and context-aware UI
        // ============================================================

        // Global aggregation state
        const aggregationState = {{
            currentLevel: 'session',  // session, day, week, period, year
            currentMode: 'game',      // game or real (follows xAxisMode)
            cachedRollups: {{}},      // Cache processed data to avoid recomputation
            originalData: null        // Store original chart data
        }};

        /**
         * Initialize advanced filtering system
         */
        document.addEventListener('DOMContentLoaded', function() {{
            // Check if rollupData exists
            if (typeof rollupData === 'undefined') {{
                console.warn('Rollup data not available - advanced filtering disabled');
                return;
            }}

            console.log('Initializing advanced filtering system');

            setupQuickFilter();
            setupAdvancedPanel();
            setupAggregationButtons();
            syncAggregationMode(); // Initial sync with xAxisMode
        }});

        /**
         * Setup quick filter dropdown handler
         */
        function setupQuickFilter() {{
            const quickFilter = document.getElementById('quickFilter');
            if (!quickFilter) return;

            quickFilter.addEventListener('change', function() {{
                const value = this.value;
                console.log('Quick filter changed:', value);

                // Handle numeric values (session count)
                if (!isNaN(value) || value === 'all') {{
                    const count = value === 'all' ? maxSessions : parseInt(value);
                    filterChartsByCount(count);
                    return;
                }}

                // Handle time-based filters
                switch(value) {{
                    case 'this-week-real':
                        filterByRealTimeRange('week');
                        break;
                    case 'this-month-real':
                        filterByRealTimeRange('month');
                        break;
                    case 'this-season-game':
                        filterByGameTimeRange('season');
                        break;
                    case 'this-year-game':
                        filterByGameTimeRange('year');
                        break;
                    case 'custom':
                        openAdvancedPanel();
                        break;
                }}
            }});
        }}

        /**
         * Filter charts by session count
         */
        function filterChartsByCount(count) {{
            if (aggregationState.currentLevel === 'session') {{
                // Use existing filterCharts function
                filterCharts(count);
            }} else {{
                // For aggregated data, filter the rollup entries
                const aggregatedData = getAggregatedChartData(
                    aggregationState.currentLevel,
                    aggregationState.currentMode
                );

                if (!aggregatedData) return;

                // Apply count filter to aggregated data
                const totalEntries = aggregatedData.sessionLabels.length;
                const startIndex = Math.max(0, totalEntries - count);

                const filteredData = sliceChartData(aggregatedData, startIndex);
                updateAllCharts(filteredData);
            }}
        }}

        /**
         * Filter by real-world time range
         */
        function filterByRealTimeRange(period) {{
            console.log('Filtering by real time range:', period);

            const now = new Date();
            const entries = diaryData.entries || [];

            let filteredEntries = entries;

            if (period === 'week') {{
                // Last 7 days
                const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                filteredEntries = entries.filter(e => {{
                    const entryDate = new Date(e.detected_at);
                    return entryDate >= weekAgo;
                }});
            }} else if (period === 'month') {{
                // Current month
                const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
                filteredEntries = entries.filter(e => {{
                    const entryDate = new Date(e.detected_at);
                    return entryDate >= monthStart;
                }});
            }}

            if (filteredEntries.length === 0) {{
                console.warn('No entries found in selected time range');
                return;
            }}

            // Update session count to match filtered entries
            const filterInput = document.getElementById('sessionFilter');
            const sessionCount = document.getElementById('sessionCount');
            if (filterInput) {{
                filterInput.value = filteredEntries.length;
                sessionCount.textContent = filteredEntries.length;
            }}

            filterCharts(filteredEntries.length);
        }}

        /**
         * Filter by game time range
         */
        function filterByGameTimeRange(period) {{
            console.log('Filtering by game time range:', period);

            const entries = diaryData.entries || [];
            if (entries.length === 0) return;

            // Get the most recent game date
            const lastEntry = entries[entries.length - 1];
            const lastGameDate = lastEntry.game_progress?.end;
            if (!lastGameDate) {{
                console.warn('Cannot determine current game date');
                return;
            }}

            // Parse last game date (e.g., "Winter 23, Year 2")
            const match = lastGameDate.match(/(\\w+)\\s+(\\d+),\\s+Year\\s+(\\d+)/);
            if (!match) return;

            const [, lastSeason, lastDay, lastYear] = match;

            let filteredEntries = entries;

            if (period === 'season') {{
                // Filter to current season
                filteredEntries = entries.filter(e => {{
                    const endDate = e.game_progress?.end;
                    if (!endDate) return false;
                    const m = endDate.match(/(\\w+)\\s+(\\d+),\\s+Year\\s+(\\d+)/);
                    if (!m) return false;
                    return m[1] === lastSeason && m[3] === lastYear;
                }});
            }} else if (period === 'year') {{
                // Filter to current year
                filteredEntries = entries.filter(e => {{
                    const endDate = e.game_progress?.end;
                    if (!endDate) return false;
                    const m = endDate.match(/Year\\s+(\\d+)/);
                    if (!m) return false;
                    return m[1] === lastYear;
                }});
            }}

            if (filteredEntries.length === 0) {{
                console.warn('No entries found in selected game time range');
                return;
            }}

            // Update session count
            const filterInput = document.getElementById('sessionFilter');
            const sessionCount = document.getElementById('sessionCount');
            if (filterInput) {{
                filterInput.value = filteredEntries.length;
                sessionCount.textContent = filteredEntries.length;
            }}

            filterCharts(filteredEntries.length);
        }}

        /**
         * Setup advanced panel toggle
         */
        function setupAdvancedPanel() {{
            const advancedToggle = document.getElementById('advancedToggle');
            const advancedContent = document.getElementById('advancedContent');

            if (!advancedToggle || !advancedContent) return;

            advancedToggle.addEventListener('click', function() {{
                const isExpanded = this.getAttribute('aria-expanded') === 'true';
                const newState = !isExpanded;

                this.setAttribute('aria-expanded', newState);
                advancedContent.hidden = !newState;

                // Update icon
                const icon = this.querySelector('.toggle-icon');
                if (icon) {{
                    icon.textContent = newState ? '▲' : '▼';
                }}

                console.log('Advanced panel toggled:', newState ? 'open' : 'closed');
            }});
        }}

        /**
         * Open advanced panel programmatically
         */
        function openAdvancedPanel() {{
            const advancedToggle = document.getElementById('advancedToggle');
            const advancedContent = document.getElementById('advancedContent');

            if (!advancedToggle || !advancedContent) return;

            advancedToggle.setAttribute('aria-expanded', 'true');
            advancedContent.hidden = false;

            const icon = advancedToggle.querySelector('.toggle-icon');
            if (icon) icon.textContent = '▲';

            // Scroll into view
            advancedToggle.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }}

        /**
         * Setup aggregation button handlers
         */
        function setupAggregationButtons() {{
            const buttons = document.querySelectorAll('.agg-btn');
            if (buttons.length === 0) return;

            buttons.forEach(button => {{
                button.addEventListener('click', function() {{
                    const level = this.dataset.level;
                    console.log('Aggregation button clicked:', level);

                    // Update active state
                    buttons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');

                    // Update aggregation state
                    aggregationState.currentLevel = level;

                    // Apply aggregation
                    applyAggregation(level);
                }});
            }});
        }}

        /**
         * Sync aggregation mode with X-axis mode
         * Called when xAxisMode changes
         */
        function syncAggregationMode() {{
            // Detect current xAxisMode
            const mode = (typeof xAxisMode !== 'undefined' && xAxisMode === 'dates') ? 'real' : 'game';
            aggregationState.currentMode = mode;

            console.log('Aggregation mode synced to:', mode);

            // Update help text
            updateAggregationHelpText(mode);

            // Update period button text
            updatePeriodButtonText(mode);
        }}

        /**
         * Update help text based on current mode
         */
        function updateAggregationHelpText(mode) {{
            const helpText = document.getElementById('aggHelpText');
            if (!helpText) return;

            if (mode === 'game') {{
                helpText.textContent = '💡 Currently grouping by GAME time. Switch X-Axis for real-world time.';
            }} else {{
                helpText.textContent = '💡 Currently grouping by REAL time. Switch X-Axis for game time.';
            }}
        }}

        /**
         * Update period button text (Season/Month)
         */
        function updatePeriodButtonText(mode) {{
            const periodBtn = document.querySelector('[data-level="period"]');
            if (!periodBtn) return;

            if (mode === 'game') {{
                periodBtn.textContent = 'Season';
            }} else {{
                periodBtn.textContent = 'Month';
            }}
        }}

        /**
         * Apply aggregation to charts
         */
        function applyAggregation(level) {{
            console.log('Applying aggregation:', level, 'mode:', aggregationState.currentMode);

            if (level === 'session') {{
                // Reset to session-level view
                const quickFilter = document.getElementById('quickFilter');
                const filterValue = quickFilter ? quickFilter.value : '10';

                // Extract count from filter value (handle numeric or 'all')
                let count = 10; // Default to 10 if time-based filter is active
                if (filterValue === 'all') {{
                    count = maxSessions;
                }} else if (!isNaN(filterValue)) {{
                    count = parseInt(filterValue);
                }}

                filterCharts(count >= maxSessions ? maxSessions : count);
                return;
            }}

            // Get aggregated data
            const aggregatedData = getAggregatedChartData(level, aggregationState.currentMode);

            if (!aggregatedData || aggregatedData.sessionLabels.length === 0) {{
                console.warn('No aggregated data available for:', level, aggregationState.currentMode);
                return;
            }}

            // Update all charts with aggregated data
            updateAllCharts(aggregatedData);
        }}

        /**
         * Get aggregated chart data from rollup data
         */
        function getAggregatedChartData(level, mode) {{
            // Check cache first
            const cacheKey = `${{level}}_${{mode}}`;
            if (aggregationState.cachedRollups[cacheKey]) {{
                console.log('Using cached rollup data:', cacheKey);
                return aggregationState.cachedRollups[cacheKey];
            }}

            console.log('Computing aggregated data:', level, mode);

            // Determine which rollup source to use
            let rollupArray = null;
            const timeMode = mode === 'real' ? 'real_time' : 'game_time';

            if (level === 'day') {{
                // Day-level: use session data grouped by day (not in rollups, use entries)
                return computeDayLevelData(mode);
            }} else if (level === 'week') {{
                rollupArray = rollupData[timeMode]?.by_week;
            }} else if (level === 'period') {{
                // Season for game, Month for real
                rollupArray = mode === 'real'
                    ? rollupData.real_time?.by_month
                    : rollupData.game_time?.by_season;
            }} else if (level === 'year') {{
                rollupArray = rollupData[timeMode]?.by_year;
            }}

            if (!rollupArray || rollupArray.length === 0) {{
                console.warn('No rollup data found for:', level, mode);
                return null;
            }}

            // Convert rollup data to chart-compatible format
            const chartData = {{
                sessionLabels: [],
                dateLabels: [],
                moneyChanges: [],
                farmingXP: [],
                fishingXP: [],
                foragingXP: [],
                miningXP: [],
                combatXP: [],
                totalXP: [],
                bundlesCompleted: [],
                cumulativeBundles: [],
                villagerHearts: {{}},
                cumulativeMoney: []
            }};

            // Initialize villager hearts
            if (typeof villagersData !== 'undefined') {{
                villagersData.forEach(villager => {{
                    chartData.villagerHearts[villager.name] = [];
                }});
            }}

            let cumulativeBundles = 0;
            let cumulativeMoney = 0;

            rollupArray.forEach((entry, index) => {{
                // Extract label (period name)
                const label = entry.period || `Entry ${{index}}`;
                chartData.sessionLabels.push(label);
                chartData.dateLabels.push(label); // Same for both in aggregated view

                // Money change
                const moneyChange = entry.money_change || 0;
                chartData.moneyChanges.push(moneyChange);
                cumulativeMoney += moneyChange;
                chartData.cumulativeMoney.push(cumulativeMoney);

                // XP by skill
                const xpBySkill = entry.xp_by_skill || {{}};
                chartData.farmingXP.push(xpBySkill.farming || 0);
                chartData.fishingXP.push(xpBySkill.fishing || 0);
                chartData.foragingXP.push(xpBySkill.foraging || 0);
                chartData.miningXP.push(xpBySkill.mining || 0);
                chartData.combatXP.push(xpBySkill.combat || 0);
                chartData.totalXP.push(entry.total_xp || 0);

                // Bundles
                const bundles = entry.bundles_completed || 0;
                chartData.bundlesCompleted.push(bundles);
                cumulativeBundles += bundles;
                chartData.cumulativeBundles.push(cumulativeBundles);

                // Villager hearts (use zeros for aggregated view - not tracked in rollups)
                for (const villagerName in chartData.villagerHearts) {{
                    chartData.villagerHearts[villagerName].push(0);
                }}
            }});

            // Cache the result
            aggregationState.cachedRollups[cacheKey] = chartData;

            return chartData;
        }}

        /**
         * Compute day-level aggregation from session entries
         */
        function computeDayLevelData(mode) {{
            const entries = diaryData.entries || [];
            if (entries.length === 0) return null;

            // Group entries by day
            const dayGroups = {{}};

            entries.forEach(entry => {{
                let dayKey;

                if (mode === 'real') {{
                    // Group by real-world date (YYYY-MM-DD)
                    if (!entry.detected_at) return;
                    const date = new Date(entry.detected_at);
                    dayKey = date.toISOString().split('T')[0];
                }} else {{
                    // Group by game date (Season Day, Year)
                    const gameDate = entry.game_progress?.end;
                    if (!gameDate) return;
                    dayKey = gameDate; // Use full date as key
                }}

                if (!dayGroups[dayKey]) {{
                    dayGroups[dayKey] = [];
                }}
                dayGroups[dayKey].push(entry);
            }});

            // Convert to chart data
            const chartData = {{
                sessionLabels: [],
                dateLabels: [],
                moneyChanges: [],
                farmingXP: [],
                fishingXP: [],
                foragingXP: [],
                miningXP: [],
                combatXP: [],
                totalXP: [],
                bundlesCompleted: [],
                cumulativeBundles: [],
                villagerHearts: {{}},
                cumulativeMoney: []
            }};

            // Initialize villager hearts
            if (typeof villagersData !== 'undefined') {{
                villagersData.forEach(villager => {{
                    chartData.villagerHearts[villager.name] = [];
                }});
            }}

            let cumulativeBundles = 0;
            let cumulativeMoney = 0;

            // Process each day
            Object.keys(dayGroups).sort().forEach(dayKey => {{
                const dayEntries = dayGroups[dayKey];

                // Format label
                let label = dayKey;
                if (mode === 'real') {{
                    const date = new Date(dayKey);
                    label = date.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }});
                }} else {{
                    // Remove year from game date
                    label = dayKey.replace(/, Year \\d+/, '');
                }}

                chartData.sessionLabels.push(label);
                chartData.dateLabels.push(label);

                // Aggregate values for all entries in this day
                let dayMoney = 0;
                let dayFarming = 0;
                let dayFishing = 0;
                let dayForaging = 0;
                let dayMining = 0;
                let dayCombat = 0;
                let dayBundles = 0;

                dayEntries.forEach(entry => {{
                    dayMoney += entry.financial?.change || 0;

                    const skills = entry.changes_detail?.skill_changes || {{}};
                    dayFarming += skills.farming?.xp_gained || 0;
                    dayFishing += skills.fishing?.xp_gained || 0;
                    dayForaging += skills.foraging?.xp_gained || 0;
                    dayMining += skills.mining?.xp_gained || 0;
                    dayCombat += skills.combat?.xp_gained || 0;

                    dayBundles += entry.changes_detail?.bundles_completed || 0;
                }});

                chartData.moneyChanges.push(dayMoney);
                cumulativeMoney += dayMoney;
                chartData.cumulativeMoney.push(cumulativeMoney);

                chartData.farmingXP.push(dayFarming);
                chartData.fishingXP.push(dayFishing);
                chartData.foragingXP.push(dayForaging);
                chartData.miningXP.push(dayMining);
                chartData.combatXP.push(dayCombat);
                chartData.totalXP.push(dayFarming + dayFishing + dayForaging + dayMining + dayCombat);

                chartData.bundlesCompleted.push(dayBundles);
                cumulativeBundles += dayBundles;
                chartData.cumulativeBundles.push(cumulativeBundles);

                // Villager hearts (use last entry's values)
                const lastEntry = dayEntries[dayEntries.length - 1];
                const friendships = lastEntry.changes_detail?.friendship_changes || {{}};

                for (const villagerName in chartData.villagerHearts) {{
                    const hearts = friendships[villagerName]?.new_hearts || 0;
                    chartData.villagerHearts[villagerName].push(hearts);
                }}
            }});

            return chartData;
        }}

        /**
         * Slice chart data from startIndex
         */
        function sliceChartData(data, startIndex) {{
            const sliced = {{
                sessionLabels: data.sessionLabels.slice(startIndex),
                dateLabels: data.dateLabels.slice(startIndex),
                moneyChanges: data.moneyChanges.slice(startIndex),
                farmingXP: data.farmingXP.slice(startIndex),
                fishingXP: data.fishingXP.slice(startIndex),
                foragingXP: data.foragingXP.slice(startIndex),
                miningXP: data.miningXP.slice(startIndex),
                combatXP: data.combatXP.slice(startIndex),
                totalXP: data.totalXP.slice(startIndex),
                bundlesCompleted: data.bundlesCompleted.slice(startIndex),
                cumulativeBundles: data.cumulativeBundles.slice(startIndex),
                villagerHearts: {{}},
                cumulativeMoney: data.cumulativeMoney.slice(startIndex)
            }};

            for (const villagerName in data.villagerHearts) {{
                sliced.villagerHearts[villagerName] = data.villagerHearts[villagerName].slice(startIndex);
            }}

            return sliced;
        }}

        /**
         * Update all charts with new data
         */
        function updateAllCharts(chartData) {{
            updateMoneyChart(chartData);
            updateXPBySkillChart(chartData);
            updateTotalXPChart(chartData);
            updateRelationshipChart(chartData);
            updateBundlesChart(chartData);
            updateCumulativeMoneyChart(chartData);
        }}

        /**
         * Hook into existing xAxisToggle to sync aggregation mode
         */
        (function() {{
            // Wait for chart_renderer.js to load
            const checkInterval = setInterval(() => {{
                const toggleButton = document.getElementById('xAxisToggle');
                if (!toggleButton) return;

                clearInterval(checkInterval);

                // Add event listener to sync aggregation mode
                toggleButton.addEventListener('click', function() {{
                    // Wait for xAxisMode to update
                    setTimeout(() => {{
                        syncAggregationMode();

                        // Re-apply current aggregation (including session level)
                        // Clear cache since mode changed
                        aggregationState.cachedRollups = {{}};
                        applyAggregation(aggregationState.currentLevel);
                    }}, 50);
                }});
            }}, 100);
        }})();
    </script>
    <script src="chart_config.js"></script>
    <script src="chart_renderer.js"></script>
</body>
</html>"""
        else:
            # PNG version (fallback)
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farmhand Dashboard - Trends</title>
    <style>
        body {{
            background: #1e1e1e;
            color: #00ff00;
            font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
            padding: 20px;
            margin: 0;
            line-height: 1.4;
        }}
        .nav-container {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 16px;
            font-weight: bold;
        }}
        .nav-bracket {{
            color: #00ff00;
        }}
        .nav-separator {{
            color: #00ff00;
            margin: 0 10px;
        }}
        .nav-link {{
            color: #00ff00;
            text-decoration: none;
            padding: 5px 10px;
            transition: all 0.2s;
        }}
        .nav-link:hover {{
            color: #ffd700;
            text-shadow: 0 0 10px #ffd700;
        }}
        .nav-link.active {{
            color: #ffd700;
            font-weight: bold;
        }}
        .dashboard-container {{
            margin: 0 auto;
            max-width: 800px;
            width: 95%;
            padding: 20px;
            box-sizing: border-box;
            border: 3px solid #00ff00;
            border-radius: 8px;
            font-size: clamp(10px, 2.5vw, 14px);
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .dashboard-container {{
                font-size: clamp(8px, 3vw, 12px);
            }}
        }}
        .chart-container {{
            text-align: center;
            margin: 30px auto;
            max-width: 90%;
        }}
        .chart-image {{
            max-width: 100%;
            height: auto;
            border: 2px solid #00ff00;
            border-radius: 4px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }}
        .chart-title {{
            color: #ffd700;
            font-size: 18px;
            font-weight: bold;
            margin: 20px 0 15px 0;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    {nav_html}
    <div class="dashboard-container">{html_header}</div>

    <div class="chart-title">SESSION TRENDS</div>
    <div class="chart-container">
        <img src="stardew_trends.png" alt="Session Trends" class="chart-image">
    </div>

    <div class="chart-title">BUNDLE & FINANCIAL OVERVIEW</div>
    <div class="chart-container">
        <img src="stardew_bundles_money.png" alt="Bundle and Money Trends" class="chart-image">
    </div>
</body>
</html>"""

        # Save trends page
        output_dir = Path(__file__).parent
        output_path = output_dir / 'trends.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)

    def generate_state(self):
        """Generate complete dashboard state."""
        print("\n[*] Analyzing game data...")

        # Extract all data
        unlocks = self.extract_unlocks()
        print("[+] Unlocks calculated")

        financials = self.extract_financials()
        print("[+] Financials analyzed")

        # Calculate momentum
        entries = self.diary.get('entries', [])
        analyzer = MomentumAnalyzer(entries)

        momentum_3 = analyzer.calculate_momentum(3)
        print("[+] 3-session momentum calculated")

        momentum_7 = analyzer.calculate_momentum(7)
        print("[+] 7-session momentum calculated")

        # Get current game date from latest metrics snapshot
        snapshots = self.metrics.get('snapshots', [])
        if snapshots:
            game_date = snapshots[-1].get('game_date', 'Unknown')
        else:
            game_date = 'Unknown'

        # Build state object
        state = {
            'generated_at': datetime.now().isoformat(),
            'game_date': game_date,
            'unlocks': unlocks,
            'financials': financials,
            'momentum_3session': momentum_3,
            'momentum_7session': momentum_7
        }

        # Save state to JSON
        self.save_json('dashboard_state.json', state)
        print("[+] State saved to dashboard_state.json")

        return state


def main():
    """Main entry point for dashboard generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate Farmhand Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dashboard_generator.py              # Generate dashboard
  python dashboard_generator.py --preview    # Show preview in terminal
  python dashboard_generator.py --output my_dashboard.html
        """
    )

    parser.add_argument('--preview', action='store_true',
                        help='Show ASCII preview in terminal after generation')
    parser.add_argument('--terminal', action='store_true',
                        help='Output colored ASCII dashboard to terminal (for Claude display)')
    parser.add_argument('--output', default='dashboard.html',
                        help='Output HTML filename (default: dashboard.html)')
    parser.add_argument('--with-trends', action='store_true',
                        help='Generate trends page with charts')

    args = parser.parse_args()

    print("=" * 65)
    print("  FARMHAND DASHBOARD")
    print("=" * 65)
    print()

    try:
        generator = DashboardGenerator()
        generator.load_all_data()
        state = generator.generate_state()

        # If --terminal flag is set, output colored ASCII and exit
        if args.terminal:
            import sys
            print("\n[*] Rendering colored terminal dashboard...")
            colored_dashboard = generator.render_ascii_dashboard(state, colored=True)
            print()
            # Use UTF-8 encoding to handle box-drawing characters on Windows
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            print(colored_dashboard)
            print()
            return 0

        # Generate HTML dashboard
        print("\n[*] Rendering HTML dashboard...")
        html_path = generator.render_html(state, args.output)
        print(f"[+] Dashboard saved to: {html_path}")

        # Generate trends page if requested
        if args.with_trends:
            print("\n[*] Rendering trends page with Chart.js...")
            trends_path = generator.render_trends_page(state, use_chartjs=True)
            print(f"[+] Trends page saved to: {trends_path}")

        print()
        print("=" * 65)
        print("[SUCCESS] Dashboard generated successfully!")
        print()
        print(f"Open {html_path} in your browser to view!")
        print()
        print("Files generated:")
        print("  - dashboard_state.json  (raw data)")
        print(f"  - {args.output.ljust(22)} (visual dashboard)")
        print("=" * 65)

        # Show preview if requested
        if args.preview:
            print()
            print("=" * 65)
            print("TERMINAL PREVIEW:")
            print("=" * 65)
            print()
            ascii_content = generator.render_ascii_dashboard(state)
            try:
                print(ascii_content)
            except UnicodeEncodeError:
                # Windows console can't handle box-drawing characters
                # Show simplified version
                print("[NOTE] Your terminal doesn't support box-drawing characters.")
                print("Open dashboard.html in your browser for the full visualization.")

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print()
        print("[TIP] Make sure you've run session_tracker.py first")
        return 1

    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Invalid JSON in save files")
        print(f"  {e}")
        return 1

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
