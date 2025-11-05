# Phase 3: Momentum Analysis Engine

**Status:** ✅ COMPLETE
**Estimated Time:** 3-4 hours
**Dependencies:** Phase 1 & 2 complete

## Goals

- Implement sophisticated momentum tracking (3-session and 7-session windows)
- Detect hot/cold streaks across multiple categories
- Generate actionable efficiency insights

## Tasks

### 3.1 MomentumAnalyzer Core
- [ ] Create `MomentumAnalyzer` class
- [ ] Implement 3-session rolling window calculator
- [ ] Implement 7-session rolling window calculator
- [ ] Define momentum categories to track

### 3.2 Category Tracking
- [ ] Bundle completion velocity
- [ ] Skill progression rate (XP gains per session)
- [ ] Social momentum (hearts gained)
- [ ] Financial growth (money change patterns)
- [ ] Museum donation rate
- [ ] Collection completions

### 3.3 Hot/Cold Streak Detection
- [ ] Define thresholds for "hot" (rapid growth)
- [ ] Define thresholds for "cold" (stagnant)
- [ ] Compare current rate to historical average
- [ ] Generate human-readable descriptions

### 3.4 Pattern Recognition
- [ ] Detect day-of-week efficiency patterns
- [ ] Identify activity correlations (e.g., mining → money)
- [ ] Find seasonal efficiency trends
- [ ] Calculate ROI for different activities

### 3.5 Insight Generation
- [ ] Generate top 3 actionable tips
- [ ] Prioritize by impact potential
- [ ] Make suggestions specific and measurable

## Technical Details

### MomentumAnalyzer Class

```python
class MomentumAnalyzer:
    def __init__(self, diary_entries):
        self.diary = diary_entries

    def calculate_momentum(self, window_size):
        """
        Calculate momentum for N most recent sessions
        Returns: {hot_streaks, cold_streaks, insights}
        """
        recent_sessions = self.diary[-window_size:]

        momentum = {
            'window_size': window_size,
            'hot_streaks': [],
            'cold_streaks': [],
            'rising_trends': [],
            'stalled_areas': [],
            'efficiency_insights': []
        }

        # Track each category
        self._analyze_bundles(recent_sessions, momentum)
        self._analyze_skills(recent_sessions, momentum)
        self._analyze_social(recent_sessions, momentum)
        self._analyze_financials(recent_sessions, momentum)

        return momentum

    def _analyze_bundles(self, sessions, momentum):
        """Track bundle completion velocity"""
        bundles_completed = [s['changes_detail']['bundles_completed']
                             for s in sessions]

        avg_rate = sum(bundles_completed) / len(sessions)

        if avg_rate > 2:  # More than 2 bundles per session
            momentum['hot_streaks'].append({
                'category': 'Bundles',
                'rate': avg_rate,
                'description': f'Bundle completion (+{avg_rate:.1f}/session)'
            })
        elif avg_rate == 0:
            momentum['cold_streaks'].append({
                'category': 'Bundles',
                'description': f'No bundle progress in {len(sessions)} sessions'
            })
```

### Thresholds for Classification

```python
THRESHOLDS = {
    'bundles': {
        'hot': 2.0,      # bundles per session
        'cold': 0.0
    },
    'skills': {
        'hot': 500,      # XP per session
        'cold': 100
    },
    'money': {
        'hot': 50000,    # gold per session
        'cold': 10000
    },
    'social': {
        'hot': 250,      # friendship points per session
        'cold': 0
    },
    'museum': {
        'hot': 3,        # donations per session
        'cold': 0
    }
}
```

### Insight Generation

```python
def generate_insights(self, diary_entries):
    """Generate top 3 actionable insights"""

    insights = []

    # Pattern 1: Activity correlations
    mining_sessions = [s for s in diary_entries if self._has_mining(s)]
    if mining_sessions:
        avg_earnings_after_mining = self._avg_next_day_earnings(mining_sessions)
        if avg_earnings_after_mining > overall_avg * 1.5:
            insights.append({
                'type': 'correlation',
                'icon': '💡',
                'text': f'Your earnings spike {avg_earnings_after_mining/overall_avg:.1f}x after mining sessions'
            })

    # Pattern 2: Seasonal efficiency
    current_season_efficiency = self._calculate_season_efficiency()
    last_year_same_season = self._get_last_year_season_efficiency()

    if current_season_efficiency > last_year_same_season * 1.2:
        insights.append({
            'type': 'progress',
            'icon': '📈',
            'text': f'This {season} is {improvement}% more efficient than last year'
        })

    return sorted(insights, key=lambda x: x.get('impact', 0), reverse=True)[:3]
```

### Example Output

```
MOMENTUM ANALYSIS
─────────────────

=== 3-SESSION MOMENTUM ===
🔥 HOT:  Combat (+1.0 level/session)
🔥 HOT:  Money (+80,090g average)
❄️ COLD: Fishing (0 XP gained)
❄️ COLD: Social (1 heart in 3 sessions)

=== 7-SESSION MOMENTUM ===
📈 RISING:  Bundle completion (18→26→30)
📈 RISING:  Abigail relationship (8→10→11 hearts)
📉 STALLED: Museum donations (stuck at 64)
📉 STALLED: Cooking recipes (no new unlocks)

EFFICIENCY INSIGHTS
───────────────────
💡 Your best earning days follow mining sessions (3.2x multiplier)
💡 Bundle progress peaks when you focus 2+ consecutive days
💡 Social momentum highest during festival weeks (+40%)
```

## Completion Criteria

- [ ] Both 3-session and 7-session momentum calculated
- [ ] Hot/cold streaks detected accurately
- [ ] At least 3 efficiency insights generated
- [ ] Momentum data added to `dashboard_state.json`
- [ ] ASCII rendering integrated into dashboard

## Notes

- Keep thresholds configurable (could move to config.json later)
- Use relative comparisons (vs. historical average) not just absolute
- Insights should be actionable and specific
- Test with real diary data across multiple playthroughs

---

**Status:** ⏳ Pending
**Last Updated:** 2025-11-03
