# Stardew Valley Companion - System Overview

## Introduction

The Stardew Valley Companion is an automated tracking system that monitors your game progress, analyzes achievements, and provides strategic recommendations for your play sessions.

## Core Concept

The system works by:
1. **Reading your save file** after you play
2. **Comparing it to the last known state** (saved snapshot)
3. **Generating a diary entry** documenting what changed
4. **Updating metrics** to track trends over time
5. **Providing recommendations** based on your goals

## Key Features

### Automatic Session Tracking
- Detects when you've played since last check
- Calculates exactly what changed (money, skills, bundles, relationships)
- Creates detailed diary entries automatically
- No manual input required

### Bundle Progress Monitoring
- Tracks Community Center bundle completion
- Shows exactly which items are still needed
- Detects both standard and remixed bundles
- Cross-references with room completion flags

### Skill & Profession Tracking
- Monitors all 6 skill levels (Farming, Fishing, Foraging, Mining, Combat, Luck)
- Tracks XP progress toward next level
- Records profession choices
- Identifies skill milestones

### Financial Analysis
- Total money on hand
- Total earned across all playtime
- Money gained per session
- Economic trends over time

### Relationship Tracking
- Friendship levels with all villagers
- Recently gifted NPCs
- Marriage status and children
- Upcoming birthdays

### Strategic Recommendations
- Reviews recent progress
- Suggests actions aligned with your goals
- Identifies time-sensitive opportunities (festivals, birthdays, last planting days)
- Provides economic projections

## File Structure

```
C:\opt\stardew\
├── session_tracker.py       # Main automation script
├── save_analyzer.py         # Save file parser
├── bundle_definitions.py    # Community Center bundles
├── item_database.py         # Item ID mappings
├── diary.json               # Session history
├── metrics.json             # Trend data
├── goals.md                 # Your strategic objectives
├── save_snapshot.json       # Last known save state
├── CLAUDE.md                # System instructions
└── doc\
    ├── system_overview.md   # This file
    ├── bundle_system.md     # Bundle tracking details
    ├── item_database.md     # Item lookup system
    └── session_workflow.md  # How sessions work
```

## Workflow

### 1. Before Playing Stardew Valley

```bash
# Open Claude Code - it automatically runs session_tracker.py
```

Claude will:
- Detect if you've played since last session
- Generate a diary entry if changes detected
- Review your goals.md
- Provide customized recommendations for today's session

### 2. While Playing Stardew Valley

Play normally! The system doesn't interfere with gameplay.

**Important:** When you're done playing, **sleep in-game** to save before exiting.

### 3. Next Time You Open Claude Code

The cycle repeats:
- `session_tracker.py` runs automatically
- Compares new save to previous snapshot
- Documents everything you accomplished
- Updates metrics.json with trends
- Provides new recommendations

## Data Files

### diary.json

Contains the complete history of all play sessions.

**Structure:**
```json
{
  "sessions": [
    {
      "id": "session_001",
      "date_recorded": "2024-11-02T10:30:00",
      "game_period": {
        "from": "Spring 1, Year 1",
        "to": "Spring 5, Year 1"
      },
      "accomplishments": [
        "Cleared 50 tiles on the farm",
        "Reached Farming Level 2",
        "Planted 20 Parsnip seeds"
      ],
      "changes": {
        "money": "+500g",
        "skills": ["Farming: 1 → 2"],
        "bundles": []
      }
    }
  ]
}
```

### metrics.json

Tracks trends and growth patterns over time.

**Structure:**
```json
{
  "last_updated": "2024-11-02T10:30:00",
  "snapshots": [
    {
      "date": "Spring 5, Year 1",
      "money": 1500,
      "total_earned": 2000,
      "bundles_complete": 2,
      "skills_maxed": 0,
      "friendships_10_hearts": 0
    }
  ],
  "milestones": [
    {
      "date": "Spring 2, Year 1",
      "type": "skill_level",
      "description": "Reached Farming Level 2"
    }
  ]
}
```

### goals.md

Your strategic objectives - **this file is user-editable**.

**Example:**
```markdown
# Current Goals

## Short-term (This Week)
- [ ] Complete Spring Crops Bundle
- [ ] Reach Fishing Level 4
- [ ] Upgrade watering can to copper

## Medium-term (This Season)
- [ ] Unlock Greenhouse by completing Pantry bundles
- [ ] Build a barn for animals
- [ ] Max friendship with Haley

## Long-term (This Year)
- [ ] Complete Community Center
- [ ] Earn 100,000g
- [ ] Reach Level 10 in all skills
```

### save_snapshot.json

Internal file - stores the last known save state for comparison.

**Do not edit manually.** Regenerated automatically by `session_tracker.py`.

## Key Functions

### session_tracker.py

**Primary Functions:**
- `detect_save_changes()`: Compares current save to snapshot
- `generate_diary_entry()`: Creates accomplishment log
- `update_metrics()`: Records trends
- `create_snapshot()`: Saves current state for next comparison

**Usage:**
```bash
python session_tracker.py
```

### save_analyzer.py

**Primary Functions:**
- `analyze_save()`: Parse save file and extract all data
- `get_detailed_bundle_info()`: Extract bundle progress
- `parse_skills()`: Get skill levels and XP
- `get_relationships()`: Get friendship levels

**Usage:**
```bash
python save_analyzer.py > current_state.json
```

### bundle_definitions.py

**Primary Functions:**
- `get_bundle_info(bundle_id)`: Look up bundle requirements
- `get_missing_items_for_bundle()`: Calculate what's still needed

**Data:**
- `BUNDLE_DEFINITIONS`: Complete mapping of all 36+ bundles

### item_database.py

**Primary Functions:**
- `get_item_info(item_id)`: Look up item name and details
- `get_item_acquisition_guide(item_id)`: How to obtain item
- `get_wiki_url(item_id)`: Generate wiki link for item

**Data:**
- `ITEM_DATABASE`: 150+ items with complete metadata

## Automation

### CLAUDE.md Instructions

When you open Claude Code in this directory, it automatically:

1. Runs `session_tracker.py`
2. Reads `diary.json` for recent history
3. Reads `goals.md` for your objectives
4. Reads `metrics.json` for trends

Then provides:
- Progress review (if you've played)
- Tactical recommendations aligned with goals
- Economic analysis
- Time-sensitive opportunities
- Specific action items for today

### Customization

You can customize the system by:

1. **Editing goals.md** - Set your own objectives
2. **Adding bundle definitions** - Support modded bundles
3. **Expanding item_database.py** - Add more items
4. **Modifying CLAUDE.md** - Change automation behavior

## Technical Details

### Save File Location

```
Windows: C:\Users\{username}\AppData\Roaming\StardewValley\Saves\{farmname}_{id}\{farmname}_{id}
Mac: ~/.config/StardewValley/Saves/{farmname}_{id}/{farmname}_{id}
Linux: ~/.config/StardewValley/Saves/{farmname}_{id}/{farmname}_{id}
```

The system automatically detects your save file location.

### Save File Format

Stardew Valley saves are XML files containing:
- Player data (stats, skills, inventory)
- Farm layout (buildings, crops, objects)
- World state (relationships, bundles, quests)
- Game progression (days played, money, achievements)

### Parsing Strategy

1. **XML Parsing**: Use Python's `xml.etree.ElementTree`
2. **XPath Queries**: Navigate to specific data elements
3. **Type Conversion**: Convert string values to appropriate types
4. **Error Handling**: Gracefully handle missing or malformed data

### Performance

- **Parse Time**: ~1-2 seconds for typical save file
- **Comparison**: ~0.5 seconds to detect changes
- **Diary Generation**: ~0.1 seconds
- **Total Runtime**: 2-3 seconds per session_tracker.py execution

## Limitations

### Current Limitations

1. **Save File Updates**: Must sleep in-game for changes to save
2. **Real-Time Tracking**: Cannot monitor during gameplay
3. **Modded Content**: Limited support for modded items/bundles
4. **Manual Goals**: goals.md must be updated manually

### Known Issues

1. **Bundle Slot Alignment**: Some bundles may show incorrect item counts (under investigation)
2. **Remixed Bundle Detection**: Some IDs (11, 15, 16, 17) marked as "unknown" need definitions
3. **Quality Items**: Silver/Gold/Iridium quality detection needs refinement

## Future Roadmap

### Planned Features (Phase 2)

- Inventory cross-reference (detect bundle items in chests)
- Seasonal alerts (last day to plant crops, festivals)
- Economic projections (income forecasts)
- Bundle prioritization by reward value

### Planned Features (Phase 3)

- XNB extraction (auto-load bundle definitions from game files)
- Modded bundle support
- Visual progress charts
- Web dashboard (optional)

### Planned Features (Phase 4)

- Multi-farm tracking
- Co-op session support
- Achievement tracking
- Fishing/cooking/crafting recipe completion

## Troubleshooting

### Problem: session_tracker.py says "No changes detected" but I played

**Solutions:**
1. Verify you slept in-game before exiting
2. Check save file modified timestamp
3. Run `python save_analyzer.py` to see current state
4. Verify save_snapshot.json exists

### Problem: Diary entry is missing accomplishments

**Solutions:**
1. Check if accomplishments were significant enough to log
2. Review thresholds in session_tracker.py (e.g., money change > 100g)
3. Verify save file is being parsed correctly

### Problem: Bundle progress not updating

**Solutions:**
1. Ensure you slept in-game after submitting bundle items
2. Check bundle_definitions.py has correct bundle ID
3. Review doc/bundle_system.md for slot calculation details

### Problem: "Unknown Item" in diary

**Solutions:**
1. Add item to item_database.py
2. Reference https://stardewvalleywiki.com/Modding:Object_data for item IDs
3. Check if item is from a mod (may need custom entry)

## Getting Help

### Resources

- **Stardew Valley Wiki**: https://stardewvalleywiki.com
- **Modding Wiki**: https://wiki.stardewvalley.net
- **Community Forums**: https://forums.stardewvalley.net

### Documentation Files

- `doc/bundle_system.md` - Bundle tracking deep dive
- `doc/item_database.md` - Item lookup reference
- `doc/session_workflow.md` - Session tracking details
- `dev/roadmap.md` - Development plans and known issues

### Debugging

Enable detailed output:
```bash
python session_tracker.py --verbose
python save_analyzer.py --debug
```

## Best Practices

### For Optimal Results

1. **Always sleep before exiting** - Ensures save file is up to date
2. **Review goals.md regularly** - Keep objectives current
3. **Check diary.json after each session** - Verify tracking accuracy
4. **Update CLAUDE.md if needed** - Customize recommendations

### Maintenance

- **Weekly**: Review goals.md, update objectives
- **Monthly**: Check metrics.json for trends
- **As Needed**: Add new items to item_database.py
- **Major Updates**: Check for new bundle definitions after game patches

## Philosophy

This system is designed to be:
- **Automatic**: Minimal manual intervention
- **Unobtrusive**: Doesn't affect gameplay
- **Informative**: Provides actionable insights
- **Extensible**: Easy to customize and expand

The goal is to enhance your Stardew Valley experience by providing strategic guidance without taking away from the joy of discovery and exploration.
