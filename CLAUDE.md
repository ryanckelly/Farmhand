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

## Wiki Integration (MCP Server)

**The Stardew Valley Wiki MCP server provides real-time wiki data to enhance recommendations.**

### When to Use MCP Tools

Use the MCP server tools proactively during strategy generation:

**1. Bundle Completion Strategy**
```
When recommending bundles to complete:
1. Check bundle_readiness in diary.json
2. For missing items, use get_page_data to fetch:
   - Crop: seasons, growth time, where to buy seeds
   - Fish: location, time, weather, difficulty
   - Forage: where to find, seasonal availability
3. Provide actionable guidance: "Plant Parsnips today (4 days to harvest, still time before Spring ends)"
```

**2. NPC Gift Recommendations**
```
When birthdays are approaching:
1. Use get_page_data({page_title: "NPC_Name"})
2. Extract loved_gifts from response
3. Cross-reference with player's inventory
4. Suggest best gift: "Sebastian's birthday is Winter 10 - give him a Frozen Tear (you have 2 in Chest #3)"
```

**3. Crop Planning**
```
When suggesting crops to plant:
1. Use get_page_data for each crop
2. Compare:
   - Growth time vs days remaining in season
   - Profit margin (sell_price - seed_price)
   - Regrowth potential
3. Recommend optimal crops: "Plant Strawberries on Spring 13+ (they regrow every 4 days)"
```

**4. Quest/Achievement Help**
```
When player asks about quests or missing items:
1. Use search_wiki to find relevant pages
2. Use get_page_data for detailed requirements
3. Provide structured guidance with locations and conditions
```

### Available MCP Tools

| Tool | Use Case | Example |
|------|----------|---------|
| `mcp__stardew-wiki__search_wiki` | Find page names, explore content | Find all Spring crops |
| `mcp__stardew-wiki__get_page_data` | Get structured data | Fetch Strawberry growing details |

### MCP Best Practices

- **Always use exact page titles** from search results
- **Cache-aware:** First request ~220ms, subsequent <1ms
- **Check parsing_warnings:** Some data may be incomplete
- **Graceful fallback:** Use local bundle_definitions.py if MCP unavailable

### Example MCP Workflow

```
User's save shows: Spring 15, Year 1, missing Spring Crops Bundle

1. Check bundle_readiness.ready_to_complete
   → Missing: Cauliflower, Green Bean

2. Query wiki for each item:
   get_page_data({page_title: "Cauliflower"})
   → seasons: ["Spring"], growth_time: 12, seed_price: 80g, seed_source: "Pierre's Shop"

   get_page_data({page_title: "Green Bean"})
   → seasons: ["Spring"], growth_time: 10, seed_source: "Pierre's Shop"

3. Calculate feasibility:
   - Today is Spring 15, 13 days left
   - Cauliflower: 12 days (✓ can harvest by Spring 27)
   - Green Bean: 10 days (✓ can harvest by Spring 25)

4. Recommendation:
   "You can still complete Spring Crops Bundle! Buy Cauliflower Seeds (80g) and
   Green Bean Seeds (60g) from Pierre's today. Plant immediately - you'll harvest
   just in time before Summer."
```

## Key Files

**Save Data & Tracking:**
- **diary.json**: Session history log (auto-generated, includes bundle readiness)
- **goals.md**: Your strategic objectives (user-editable)
- **metrics.json**: Trend data (auto-generated)
- **save_snapshot.json**: Last known save state (auto-generated)
- **save_analyzer.py**: Parses save files (inventory, chests, bundles)
- **session_tracker.py**: Tracks changes between sessions

**Game Data:**
- **bundle_checker.py**: Cross-references inventory with bundle requirements
- **bundle_definitions.py**: Community Center bundle data (local fallback)
- **item_database.py**: Item ID to name mappings (local fallback)
- **mcp_servers/stardew_wiki_mcp.py**: Wiki MCP server (primary data source)

**Dashboard:**
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

**2025-11-13:**
- ✅ **Stardew Valley Wiki MCP Server** - Production-ready wiki integration
  - Real-time data extraction for crops, NPCs, fish, recipes, bundles
  - 220x faster performance with intelligent caching
  - 92% parser success rate across 11 specialized parsers
  - Comprehensive error handling and retry logic
  - 76 automated tests (90.8% pass rate)
  - 2,200+ lines of professional documentation
- ✅ **CLAUDE.md Integration** - MCP tools now part of recommended workflow
  - Bundle completion strategy enhanced with live wiki data
  - NPC gift recommendations with real-time preferences
  - Crop planning with growth times and profit margins
  - Quest/achievement help with structured guidance

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

For detailed technical information, see the `/doc` and `/mcp_servers` directories:

**MCP Server Documentation:**
- **mcp_servers/API_REFERENCE.md** - Complete MCP tool documentation
- **mcp_servers/PARSER_COVERAGE.md** - What data each parser extracts
- **mcp_servers/CONTRIBUTING.md** - How to add new parsers
- **mcp_servers/TROUBLESHOOTING.md** - Common MCP issues and solutions

**Companion System Documentation:**
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

### Wiki Access

**Primary: MCP Server Tools (Preferred)**
- `mcp__stardew-wiki__search_wiki` - Search wiki by keyword
- `mcp__stardew-wiki__get_page_data` - Get structured data (crops, NPCs, fish, recipes, bundles, etc.)
- See "Wiki Integration (MCP Server)" section above for usage examples

**Fallback: Manual Links** (if MCP unavailable)
- [Stardew Valley Wiki](https://stardewvalleywiki.com)
- [Bundle Reference](https://stardewvalleywiki.com/Bundles)
- [Remixed Bundles](https://stardewvalleywiki.com/Remixed_Bundles)
- [Item IDs](https://stardewvalleywiki.com/Modding:Object_data)

## Automation Workflow

1. User opens Claude Code → session_tracker.py runs automatically
2. Changes detected → diary entry created
3. Claude reviews goals.md → drafts recommendations
4. **MCP server queries wiki for real-time data** (crops, NPCs, bundles, items)
5. **Validation subagent verifies recommendations against game data**
6. Corrected strategy with wiki-enhanced details presented to user
7. User plays Stardew Valley
8. Next session → cycle repeats

Everything is automated - no manual tracking needed!
