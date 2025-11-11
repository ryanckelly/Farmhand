# Unlockables Tracking System

## Overview

The Unlockables Tracking System provides comprehensive progress tracking for 45+ major unlockables in Stardew Valley, with dynamic display of the top 5 most relevant unlocks based on player goals and current progress.

### Key Features

- **Comprehensive Tracking**: 45+ unlockables across 8 categories
- **Progress Methodology**: Step-by-step completion tracking with granular percentages
- **Dynamic Selection**: Claude manually selects the top 5 most relevant unlocks each session
- **Goal Alignment**: Recommendations aligned with player's strategic objectives
- **Dashboard Integration**: Replaces static "Unlocks Progress" with dynamic "Top 5 Active Unlocks"

---

## System Architecture

### Components

1. **unlockables.csv** - Reference documentation listing all unlockables
2. **unlockables_config.json** - Detailed completion methodology for each unlockable
3. **save_analyzer.py** - Tracking engine that calculates progress
4. **dashboard_generator.py** - Displays top 5 selected unlocks
5. **.claude/commands/stardew.md** - Workflow for Claude's selection process
6. **dashboard/top5_unlocks.json** - Claude's manual selection (generated each session)

### Data Flow

```
Save File → save_analyzer.py → unlockables_status → save_snapshot.json
                                                              ↓
                               /stardew command → Claude reviews progress
                                                              ↓
                                            Claude selects top 5 manually
                                                              ↓
                                          top5_unlocks.json ← Written
                                                              ↓
                            dashboard_generator.py → Displays top 5
```

---

## Unlockables Configuration

### Structure of unlockables_config.json

Each unlockable is defined with:

```json
{
  "Unlockable Name": {
    "category": "Map Access | Progression | Island Features | Buildings | Skills | Collection | Social | Shops",
    "total_steps": 3,
    "prerequisites": [
      {
        "name": "Human-readable step description",
        "check_method": "flag | save_field | unlockable | game_date | tool_level | ...",
        "check_params": { ...method-specific parameters... }
      }
    ],
    "completion_check": "final_check_method",
    "hints": [
      "Helpful hint 1",
      "Helpful hint 2"
    ]
  }
}
```

### Check Methods

| Method | Description | Example |
|--------|-------------|---------|
| `flag` | Check bundle reward flags | `{"flag_name": "ccVault"}` |
| `save_field` | Check nested save data field | `{"field": "unlocks.rusty_key"}` |
| `unlockable` | Depends on another unlockable | `{"unlockable_name": "Ginger Island"}` |
| `game_date` | Check if date has passed | `{"min_season": "summer", "min_day": 3, "min_year": 1}` |
| `tool_level` | Check tool upgrade level | `{"tool": "axe", "min_level": 2}` |
| `room_complete` | Check CC room completion | `{"room_name": "Pantry"}` |
| `skill_level` | Check skill level | `{"skill": "combat", "level": 10}` |
| `museum_item` | Check museum donation | `{"item_id": "96"}` |
| `friendship` | Check NPC heart level | `{"npc": "Abigail", "min_hearts": 8}` |
| `walnuts_found` | Check total walnuts found | `{"count": 100}` |
| `museum_count` | Check total museum donations | `{"count": 60}` |

---

## Categories

### Map Access (12 unlockables)
- Calico Desert, Skull Cavern, Ginger Island, Railroad & Spa, Secret Woods
- Sewers & Krobus Shop, Quarry & Quarry Mine, Mutant Bug Lair, Witch's Swamp
- Beach Bridge, Volcano Dungeon, Island Farm

### Progression (8 unlockables)
- Casino (Club Card), Mastery Cave, Wizard Tower (Junimo Language)
- Movie Theater, Community Center, Museum Collection (60 & 95)
- Leo's Return to Town

### Island Features (13 unlockables)
- Island Farmhouse, Island Trader, Resort Rebuild, Professor Snail's Tent
- Island Field Office, Qi's Walnut Room, Pirate Cove, Parrot Express
- Volcano Forge Room, Obsidian Shortcut, Golden Walnuts (100 & 130)

### Skills (5 unlockables)
- Combat Level 10, Fishing Level 10, Farming Level 10
- Mining Level 10, Foraging Level 10

### Collection (2 unlockables)
- Cooking Recipes (All 74), Friendships (8+ Hearts with all 32 NPCs)

### Buildings (3 unlockables)
- Witch's Hut, Greenhouse, Island Farm

### Shops (2 unlockables)
- Dwarf Merchant, Wizard Tower

---

## Claude Selection Process

### When Does Selection Occur?

The `/stardew` command triggers Claude to select the top 5 unlockables after:
1. Running session tracker
2. Displaying dashboard
3. User grants permission to proceed
4. Reading core files (goals.md, diary.json, save_snapshot.json)

### Selection Criteria

Claude manually evaluates all 45+ unlockables based on:

1. **Proximity to Completion** (40% weight)
   - 80-99%: High priority (nearly complete)
   - 50-79%: Medium priority (actively progressing)
   - 0-49%: Low priority (early stages)

2. **Goal Alignment** (30% weight)
   - Mentioned explicitly in goals.md
   - Related to current objectives
   - Part of dependency chain for goals

3. **Recent Activity** (20% weight)
   - Worked on in last 3 sessions (diary.json)
   - Related to recent XP gains
   - Part of current focus area

4. **Dependency Chains** (10% weight)
   - Blocks other high-value unlocks
   - Critical path for multiple objectives
   - Gateway unlocks (e.g., Ginger Island)

### Selection Strategy

**Always include a mix of:**
- 2-3 near-completion unlocks (for motivation and quick wins)
- 1-2 long-term unlocks (for strategic planning)
- 0-1 blocker unlocks (for dependency resolution)

**Example Selection:**
```json
{
  "selected_at": "2025-11-11T01:23:45",
  "reasoning": "Combat Level 10 is 85% complete (active goal). The Missing Bundle blocks CC completion (critical). Golden Walnuts enable island upgrades (dependency). Museum 95 provides Stardrop (long-term). Ginger Island unlocks island content (blocker).",
  "unlocks": [
    {
      "name": "Combat Level 10",
      "completion_percent": 85,
      "next_step": "Gain 5,070 more Combat XP",
      "category": "Skills"
    },
    {
      "name": "Community Center",
      "completion_percent": 97,
      "next_step": "Complete The Missing Bundle (need Dinosaur Egg + Gold Ancient Fruit)",
      "category": "Progression"
    },
    {
      "name": "Golden Walnuts (100)",
      "completion_percent": 31,
      "next_step": "Find 69 more Golden Walnuts",
      "category": "Island Features"
    },
    {
      "name": "Museum Collection (95 Items)",
      "completion_percent": 79,
      "next_step": "Donate 20 more items",
      "category": "Progression"
    },
    {
      "name": "Ginger Island",
      "completion_percent": 50,
      "next_step": "Repair Willy's boat",
      "category": "Map Access"
    }
  ]
}
```

---

## Adding New Unlockables

### Step 1: Add to unlockables.csv

Add a row with:
- Name
- Unlock Requirement
- Unlock Method
- Key Item/Quest
- Main Rewards

### Step 2: Define in unlockables_config.json

```json
{
  "New Unlockable Name": {
    "category": "Choose from: Map Access, Progression, Island Features, Buildings, Skills, Collection, Social, Shops",
    "total_steps": 2,
    "prerequisites": [
      {
        "name": "First prerequisite description",
        "check_method": "Choose appropriate method",
        "check_params": { ...params... }
      },
      {
        "name": "Second prerequisite description",
        "check_method": "Choose appropriate method",
        "check_params": { ...params... }
      }
    ],
    "completion_check": "method_name",
    "hints": [
      "Helpful hint for players"
    ]
  }
}
```

### Step 3: Test Tracking

```bash
python save_analyzer.py > test.json
python -c "import json; data = json.load(open('test.json')); print(json.dumps(data['unlockables_status']['New Unlockable Name'], indent=2))"
```

### Step 4: Verify Integration

Run `/stardew` command and verify:
- Unlockable appears in available pool
- Progress percentage calculates correctly
- Can be selected for top 5

---

## Technical Details

### Progress Calculation

Progress is calculated as:
```python
completion_percent = (completed_steps / total_steps) * 100
```

Where `completed_steps` is the number of prerequisites that evaluate to True.

### Dependency Handling

Unlockables can depend on other unlockables using the `unlockable` check method. The system uses a two-pass algorithm:
1. **First pass**: Calculate all unlockables without dependencies
2. **Second pass**: Recalculate unlockables that reference other unlockables

### Performance

- Config loading: ~5ms
- Single unlockable calculation: ~1-2ms
- All 45+ unlockables: ~100-200ms
- Total save analysis (including unlockables): ~1-2 seconds

---

## Dashboard Display

### Terminal Dashboard

The terminal dashboard displays:
```
TOP 5 ACTIVE UNLOCKS
────────────────────
Combat Level 10   [████████████████░░░░]  85%
Community Center  [███████████████████░]  97%
Golden Walnuts (1 [███████░░░░░░░░░░░░░]  31%
Museum Collection [███████████████░░░░░]  79%
Ginger Island     [██████████░░░░░░░░░░]  50%
```

### HTML Dashboard (Railway)

The web dashboard displays the same data with:
- Responsive CSS styling
- Mobile-friendly layout
- Dynamic font sizing
- Progress bars with percentage

---

## Troubleshooting

### Unlockable Shows 0% When It Should Be Complete

**Cause**: XML path or mail_received check is incorrect

**Solution**: Verify the prerequisite check matches the actual save file structure:
```bash
grep -i "keyword" "path/to/save/file"
```

### Unlockable Missing from save_snapshot.json

**Cause**: Not added to unlockables_config.json or config has syntax error

**Solution**: Validate JSON syntax:
```bash
python -c "import json; json.load(open('unlockables_config.json'))"
```

### top5_unlocks.json Not Generated

**Cause**: /stardew command didn't complete step 5

**Solution**: Check that:
1. User granted permission to proceed
2. save_snapshot.json exists and contains `unlockables_status`
3. Claude completed the selection step

---

## Future Enhancements

Potential improvements:
- Automated scoring algorithm as alternative to manual selection
- Historical tracking of top 5 changes over time
- Unlockable recommendations based on season/weather
- Integration with bundle_readiness for item-based unlocks
- Visual dependency graph showing unlock chains
- Estimated time-to-completion based on play patterns

---

## Example Workflows

### Scenario 1: New Player (Year 1)

**Top 5 Selection:**
1. Community Center (25%) - Primary early-game goal
2. Secret Woods (0%) - Need Steel Axe upgrade
3. Skull Cavern (0%) - Long-term goal (need Desert + Skull Key)
4. Sewers & Krobus Shop (42%) - Museum donation progress
5. Greenhouse (17%) - Pantry bundles in progress

**Reasoning**: Focus on CC and immediate upgrades while introducing long-term goals.

### Scenario 2: Mid-Game Player (Year 2)

**Top 5 Selection:**
1. Community Center (97%) - One bundle remaining
2. Combat Level 10 (85%) - Nearly maxed
3. Ginger Island (50%) - CC complete, need boat repair
4. Museum Collection 95 (79%) - Close to Stardrop
5. Golden Walnuts 100 (31%) - Island progression

**Reasoning**: Finish near-complete goals, unlock island content, progress toward perfection.

### Scenario 3: End-Game Player (Year 3+)

**Top 5 Selection:**
1. Mastery Cave (80%) - 4/5 skills maxed
2. Qi's Walnut Room (77%) - 77/100 walnuts
3. Museum Collection 95 (95%) - 90/95 items
4. Cooking Recipes All (45%) - Long-term collection
5. Friendships 8+ Hearts (41%) - 13/32 NPCs

**Reasoning**: Perfection tracking, collection completion, social goals.

---

## References

- `/doc/system_overview.md` - Overall system architecture
- `/doc/bundle_system.md` - Bundle tracking details
- `/doc/common_mistakes.md` - Data interpretation guidelines
- `CLAUDE.md` - Main project documentation
- `unlockables.csv` - Full unlockable reference list
- `unlockables_config.json` - Complete tracking configuration
