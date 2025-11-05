# Phase 5: Polish & Edge Cases

**Status:** ✅ COMPLETE
**Estimated Time:** 2 hours
**Dependencies:** Phase 1-4 complete

## Goals

- Handle edge cases and incomplete data
- Optimize performance for large save files
- Add configuration options
- Final testing and validation

## Tasks

### 5.1 Edge Case Handling
- [ ] Handle empty diary.json (new game)
- [ ] Handle incomplete save data
- [ ] Handle missing momentum data (< 3 sessions)
- [ ] Graceful degradation for all missing fields
- [ ] Validate data types and ranges

### 5.2 Performance Optimization
- [ ] Profile with large diary.json (100+ sessions)
- [ ] Optimize JSON parsing
- [ ] Cache calculations where possible
- [ ] Reduce memory footprint

### 5.3 Configuration Options
- [ ] Create optional `dashboard_config.json`
- [ ] Configurable momentum thresholds
- [ ] Configurable display preferences
- [ ] Color scheme options

### 5.4 Enhanced ASCII Art
- [ ] Improve progress bar rendering
- [ ] Better sparkline normalization
- [ ] Consistent box drawing
- [ ] Emoji fallbacks for terminal compatibility

### 5.5 Testing & Validation
- [ ] Test with Year 1 save
- [ ] Test with Year 2+ save
- [ ] Test with minimal progress
- [ ] Test with max progress (endgame)
- [ ] Cross-browser HTML testing

### 5.6 Documentation
- [ ] Add docstrings to all functions
- [ ] Create usage examples
- [ ] Document configuration options
- [ ] Add troubleshooting guide

## Technical Details

### Edge Case Examples

```python
def safe_get(data, *keys, default=None):
    """Safely navigate nested dictionaries"""
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return default

def calculate_momentum_safe(diary_entries, window_size):
    """Calculate momentum with minimum session requirement"""
    if len(diary_entries) < window_size:
        return {
            'error': f'Need at least {window_size} sessions',
            'available': len(diary_entries),
            'hot_streaks': [],
            'cold_streaks': [],
            'insights': [
                'Play more sessions to unlock momentum tracking!'
            ]
        }

    return calculate_momentum(diary_entries, window_size)
```

### Configuration Schema

```json
{
  "thresholds": {
    "bundles": {"hot": 2.0, "cold": 0.0},
    "skills": {"hot": 500, "cold": 100},
    "money": {"hot": 50000, "cold": 10000}
  },
  "display": {
    "progress_bar_width": 20,
    "sparkline_height": 8,
    "color_scheme": "terminal_green"
  },
  "momentum": {
    "windows": [3, 7],
    "min_sessions_required": 3
  }
}
```

### Performance Considerations

```python
class DashboardGenerator:
    def __init__(self):
        # Load files once
        self._snapshot = None
        self._diary = None

    @property
    def snapshot(self):
        if self._snapshot is None:
            self._snapshot = self.load_json('save_snapshot.json')
        return self._snapshot

    def generate_state(self, force_refresh=False):
        """Generate state with optional caching"""
        cache_file = 'dashboard_state.json'

        # Check if cache is fresh
        if not force_refresh and os.path.exists(cache_file):
            cache_time = os.path.getmtime(cache_file)
            snapshot_time = os.path.getmtime('save_snapshot.json')

            if cache_time > snapshot_time:
                return self.load_json(cache_file)

        # Generate fresh state
        state = self._generate_fresh_state()
        self.save_json(cache_file, state)
        return state
```

### Enhanced Progress Bar

```python
def generate_progress_bar(percent, width=20, style='blocks'):
    """
    Enhanced progress bar with multiple styles

    Styles:
    - 'blocks': [████████░░░░░░░░] (default)
    - 'dots': [••••••••········]
    - 'equals': [========........]
    """
    filled = int(percent * width)
    empty = width - filled

    styles = {
        'blocks': ('█', '░'),
        'dots': ('•', '·'),
        'equals': ('=', '.')
    }

    fill_char, empty_char = styles.get(style, styles['blocks'])
    bar = fill_char * filled + empty_char * empty

    return f"[{bar}] {int(percent*100):>3}%"
```

### Validation Tests

```python
def validate_dashboard_output(dashboard_html):
    """Validate generated dashboard meets quality standards"""

    checks = []

    # Check 1: Valid HTML
    checks.append(('Valid HTML', '<html>' in dashboard_html and '</html>' in dashboard_html))

    # Check 2: ASCII art present
    checks.append(('ASCII art', '╔' in dashboard_html or '║' in dashboard_html))

    # Check 3: All sections present
    required_sections = ['UNLOCKS', 'FINANCIAL', 'MOMENTUM']
    checks.append(('All sections', all(s in dashboard_html for s in required_sections)))

    # Check 4: No placeholder text
    checks.append(('No placeholders', '{{' not in dashboard_html))

    return all(passed for _, passed in checks), checks
```

## Completion Criteria

- [ ] All edge cases handled gracefully
- [ ] Performance acceptable with 100+ sessions
- [ ] Configuration file works correctly
- [ ] All ASCII art renders properly
- [ ] Comprehensive tests pass
- [ ] Documentation complete

## Testing Checklist

### Data Scenarios
- [ ] Fresh save (0-5 sessions)
- [ ] Early game (Year 1)
- [ ] Mid game (Year 2)
- [ ] Late game (Year 3+)
- [ ] Missing diary.json
- [ ] Corrupted JSON
- [ ] Empty bundle completion
- [ ] All skills maxed

### Visual Tests
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Terminal preview output
- [ ] Different screen sizes

## Notes

- Prioritize user experience over perfection
- Error messages should never crash - always recover
- Keep configuration optional - sane defaults
- Document any known limitations

---

**Status:** ⏳ Pending
**Last Updated:** 2025-11-03
