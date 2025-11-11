# Stardew Valley Companion System

## Quick Start for Claude

When this project is opened:

1. **Run session tracker**:
   ```bash
   python session_tracker.py
   ```

2. **Generate and display Farmhand Dashboard**:
   ```bash
   python dashboard/dashboard_generator.py --terminal
   ```
   **CRITICAL - DISPLAY IN RESPONSE**:
   - **COPY the entire dashboard output into your response text** (not just tool results)
   - Users cannot see collapsed tool results - the dashboard MUST appear in the response body
   - Display the dashboard as a code block at the very top of your response
   - Preserve ANSI escape codes (they will render as green in the terminal)
   - Example format:
     ```
     [Dashboard output here with ANSI codes]
     ```
   - Then below the dashboard, continue with other text/questions

   **ASK USER FOR PERMISSION** to proceed: "Would you like me to proceed to generate recommendations for your session today?"
   - If user declines, stop here (they may just want a quick status check)

3. **Read core files** (only if user grants permission):
   - `diary.json` - Recent play sessions and accomplishments
   - `goals.md` - Current strategic objectives
   - `metrics.json` - Trends and growth patterns
   - `dashboard/dashboard_state.json` - Progress, financials, momentum

4. **Provide customized session strategy**:
   - Progress review (if played since last check)
   - **Bundle readiness check** (what can be completed RIGHT NOW)
   - Tactical recommendations aligned with goals.md
   - Economic analysis and projections
   - Time-sensitive opportunities (birthdays, festivals, last planting days)
   - Specific action items for today's play session

   **NEW: Bundle Recommendations**
   - Check `bundle_readiness.ready_to_complete` in diary.json
   - Provide specific locations: "Collect X from Chest #Y"
   - Prioritize by completion percentage
   - Suggest next items to gather

5. **VALIDATE recommendations using a subagent** (only if proceeding with full analysis):
   - **BEFORE presenting strategy to user**, launch a validation subagent
   - Use `Task` tool with `subagent_type="general-purpose"` or `"debugger"`
   - **Use haiku model** for fast validation: set `model="haiku"` in Task call
   - **Why subagent?** Avoids confirmation bias - you may have already made incorrect assumptions
   - **Validation checks:**
     - If recommending CC bundles → verify `ccIsComplete` flag NOT present
     - If mentioning marriage status → verify against `marriage.married` field
     - If suggesting goals → cross-check with actual `save_snapshot.json` data
     - If claiming achievements → verify against unlocks/professions/skills
   - **Output:** Subagent returns "VALID" or list of errors to correct
   - **Only then** present the corrected strategy to user

## Key Files

- **diary.json**: Session history log (auto-generated, includes bundle readiness)
- **goals.md**: Your strategic objectives (user-editable)
- **metrics.json**: Trend data (auto-generated)
- **save_snapshot.json**: Last known save state (auto-generated)
- **save_analyzer.py**: Parses save files (inventory, chests, bundles)
- **session_tracker.py**: Tracks changes between sessions
- **bundle_checker.py**: Cross-references inventory with bundle requirements
- **bundle_definitions.py**: Community Center bundle data
- **item_database.py**: Item ID to name mappings
- **dashboard/dashboard_generator.py**: Focus Flow Dashboard generator
- **dashboard/dashboard_state.json**: Dashboard analytics (auto-generated)
- **dashboard/dashboard.html**: Visual dashboard (auto-generated)
- **dashboard/trends.html**: Trends page with Chart.js visualizations (auto-generated)
- **app.py**: Flask web server for Railway deployment

## Important Notes

### Critical: Read Data Carefully

**ALWAYS verify data before making claims:**

1. **Marriage Status**
   - Dating cap: 10 hearts (cannot exceed without marriage)
   - **11+ hearts = ALREADY MARRIED** (heart cap increases to 14 after marriage)
   - Check `marriage.married` and `marriage.spouse` in save_snapshot.json
   - Cross-reference with friendship hearts (spouse should have 10+ hearts)

2. **Community Center Completion**
   - Check `bundles.bundle_reward_flags` for `ccIsComplete` flag
   - **If ccIsComplete is present, Community Center is DONE**
   - CC requires 30 bundles (not 31) - The Missing Bundle (ID 36) is post-CC content
   - Bundle count shows 30/30 when complete
   - Also check `completed_rooms` list

3. **Professions**
   - Read the full `professions` list in save_snapshot.json
   - Don't assume professions - **verify they exist in the list**
   - Example: "Botanist" appears in professions array if unlocked

4. **Museum Donations**
   - Check `museum.total_donated` for total items
   - Check `museum.dwarf_scrolls.can_trade_with_dwarf` for Dwarf trading access
   - Individual scroll status: `scroll_i`, `scroll_ii`, `scroll_iii`, `scroll_iv`

5. **Goals.md Synchronization**
   - goals.md is **user-editable** and may become outdated
   - **Trust save_snapshot.json data over goals.md**
   - If discrepancy found, offer to update goals.md
   - Never make recommendations based on stale goals

### Save File Behavior

**The save file only updates when you sleep (end the day) in Stardew Valley.**

For accurate tracking:
1. Submit items to bundles in-game
2. **Sleep to save**
3. Exit Stardew Valley
4. Run `session_tracker.py`

### Bundle Detection

- Supports standard and remixed bundles
- Uses item-based counting (not slot-based)
- Detects bundle completion via dual-state validation
- See `/doc/bundle_system.md` for technical details

### Web Deployment

**Live Dashboard**: https://farmhand-production.up.railway.app

The dashboard is deployed on Railway and accessible from any device:
- **Main Dashboard**: `/dashboard` - Progress overview, financials, momentum
- **Trends Page**: `/trends` - Interactive Chart.js visualizations

**Key Features:**
- Mobile-responsive CSS design (works on phones, tablets, desktops)
- Auto-deploys when you push to GitHub
- HTTPS enabled by default
- Free tier hosting on Railway

**Updating the Deployment:**
1. Play Stardew Valley and end session
2. Run `python session_tracker.py` locally
3. Regenerate dashboard: `python dashboard/dashboard_generator.py --with-trends`
4. Commit and push to GitHub (Railway auto-deploys in ~60 seconds)

See `/doc/deployment.md` for full deployment guide.

### Recent Improvements

**2025-11-05:**
- ✅ **Railway Deployment** - Dashboard accessible via web from any device
- ✅ **Mobile Responsiveness** - Replaced ASCII borders with CSS for proper mobile scaling
- ✅ **Consistent Container Widths** - All divs dynamically sized with matching widths
- ✅ **Chart.js Integration** - Interactive trends charts with session filtering

**2025-11-02:**
- ✅ **Subagent Validation Step** - All session strategies must be validated by independent subagent before presentation
- ✅ **Marriage Status Detection** - Automatically detects marriage via spouse field and 11+ hearts
- ✅ **Museum Donation Tracking** - Tracks total donations and Dwarf Scroll status
- ✅ **Data Interpretation Guidelines** - Added critical checks to prevent misreading save data
- ✅ **Fixed Deprecation Warning** - Improved XML element checking in save_analyzer.py

**2025-01-02:**
- ✅ **Inventory Cross-Reference System** - Tracks which bundles can be completed RIGHT NOW
- ✅ Player inventory parsing (all items with IDs, quality, quantity)
- ✅ Enhanced chest parsing (all items from all chests)
- ✅ Bundle readiness checker (matches inventory to bundle requirements)
- ✅ Priority ranking (shows bundles closest to completion)
- ✅ Location tracking (tells you which chest has needed items)

**2024-11-02:**
- ✅ Fixed bundle completion logic (discovered 1:1 slot mapping)
- ✅ Added comprehensive item database (150+ items)
- ✅ Implemented remixed bundle detection
- ✅ Added dual-state validation (slots + room flags + mail)
- ✅ Resolved Fodder Bundle slot alignment issue
- ✅ Universal logic works across all bundles (no special cases)

## Documentation

For detailed technical information, see the `/doc` directory:

- **doc/system_overview.md** - Complete system architecture and workflow
- **doc/bundle_system.md** - Bundle tracking deep dive and slot mechanics
- **doc/item_database.md** - Item lookup system and database structure
- **doc/common_mistakes.md** - Data interpretation errors and how to avoid them
- **doc/deployment.md** - Railway deployment guide and web hosting setup
- **dev/roadmap.md** - Development plans and known issues

## Quick Reference

### Common Commands
```bash
python session_tracker.py                           # Detect changes and update diary
python save_analyzer.py                             # Analyze current save file
python dashboard/dashboard_generator.py --terminal  # Generate terminal dashboard
python dashboard/dashboard_generator.py --with-trends  # Generate HTML dashboard + trends
```

### Web Resources
- [Stardew Valley Wiki](https://stardewvalleywiki.com)
- [Bundle Reference](https://stardewvalleywiki.com/Bundles)
- [Remixed Bundles](https://stardewvalleywiki.com/Remixed_Bundles)
- [Item IDs](https://stardewvalleywiki.com/Modding:Object_data)

## Automation Workflow

1. User opens Claude Code → session_tracker.py runs automatically
2. Changes detected → diary entry created
3. Claude reviews goals.md → drafts recommendations
4. **Validation subagent verifies recommendations against game data**
5. Corrected strategy presented to user
6. User plays Stardew Valley
7. Next session → cycle repeats

Everything is automated - no manual tracking needed!
