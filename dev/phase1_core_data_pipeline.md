# Phase 1: Core Data Pipeline

**Status:** ✅ COMPLETE
**Estimated Time:** 2-3 hours
**Dependencies:** None

## Goals

- Create the basic data extraction and transformation pipeline
- Generate `dashboard_state.json` from existing game files
- Set up core architecture for all future phases

## Tasks

### 1.1 Create Main Generator File
- [ ] Create `dashboard_generator.py` with basic structure
- [ ] Add JSON loading utilities with error handling
- [ ] Set up logging for debugging

### 1.2 Build UnlocksExtractor
- [ ] Extract Community Center bundle completion (from `bundles.complete_count`)
- [ ] Extract Museum donations (from `museum.total_donated`)
- [ ] Extract cooking recipes count
- [ ] Extract high friendship count (8+ hearts)
- [ ] Extract maxed skills count (level 10)
- [ ] Calculate percentages for each category

### 1.3 Build FinancialExtractor
- [ ] Calculate current balance from `save_snapshot.json`
- [ ] Calculate daily average from `diary.json` entries
- [ ] Calculate 7-day trend
- [ ] Calculate 30-day trend
- [ ] Find best earning day
- [ ] Generate sparkline data for trends

### 1.4 Create dashboard_state.json Schema
- [ ] Define JSON structure
- [ ] Add timestamp and metadata
- [ ] Include current game date
- [ ] Placeholder for momentum data (Phase 3)

### 1.5 Basic Testing
- [ ] Test with current save files
- [ ] Verify JSON output is valid
- [ ] Handle missing data gracefully

## Technical Details

### Core Class Structure
```python
class DashboardGenerator:
    def __init__(self):
        self.snapshot = self.load_json('save_snapshot.json')
        self.diary = self.load_json('diary.json')
        self.metrics = self.load_json('metrics.json')

    def load_json(self, filename):
        """Load JSON with error handling"""

    def extract_unlocks(self):
        """Extract unlock percentages"""

    def extract_financials(self):
        """Extract financial metrics"""

    def generate_state(self):
        """Generate dashboard_state.json"""
```

### Expected dashboard_state.json Structure
```json
{
  "generated_at": "2025-11-03T18:45:23",
  "game_date": "Fall 26, Year 2",
  "unlocks": {
    "community_center": {"completed": 30, "total": 31, "percent": 0.97},
    "museum": {"donated": 64, "total": 95, "percent": 0.67},
    "cooking": {"known": 22, "total": 74, "percent": 0.30},
    "friendships_8plus": {"count": 3, "total": 32, "percent": 0.09},
    "skills_maxed": {"count": 4, "total": 5, "percent": 0.80}
  },
  "financials": {
    "current_balance": 517664,
    "daily_average": 40160,
    "weekly_trend": 0.23,
    "best_day": {"amount": 158733, "date": "Fall 7, Year 2"},
    "sparkline_data": [0.1, 0.2, 0.3, 0.5, 0.6, 0.8, 1.0]
  },
  "momentum_3session": {},
  "momentum_7session": {}
}
```

## Completion Criteria

- [ ] `dashboard_generator.py` exists and runs without errors
- [ ] `dashboard_state.json` is generated with valid data
- [ ] All unlock categories calculated correctly
- [ ] All financial metrics calculated correctly
- [ ] Code is documented and readable

## Notes

- Keep all calculations as pure functions for testability
- Use existing data structures from `save_analyzer.py` where possible
- Don't modify any existing files yet

---

**Status:** ⏳ Pending
**Last Updated:** 2025-11-03
