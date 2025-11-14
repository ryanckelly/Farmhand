# Stardew Valley Wiki MCP Server

A comprehensive Model Context Protocol (MCP) server that allows Claude to search and retrieve structured data from the Stardew Valley Wiki.

## What is This?

This MCP server provides two powerful tools for Claude Code:
1. **`search_wiki`** - Search for pages with **intelligent natural language query preprocessing**
2. **`get_page_data`** - Extract structured data from specific pages

### Smart Search (NEW in Phase 3.7)
The `search_wiki` tool now includes intelligent query preprocessing that converts natural language queries into optimized search terms:
- "what does sebastian like" → Finds Sebastian's gift preferences
- "spring birthdays" → Finds the Calendar page
- "crops in summer" → Finds Summer Crops page
- **95.8% query success rate** with automatic fallback strategies

When you ask Claude questions about Stardew Valley, it can now search the wiki, extract structured data (crop growth times, NPC gift preferences, bundle requirements, etc.), and provide accurate answers.

## Current Features (Phase 1, 2, 3 ✅ Complete)

### Fully Supported Categories

| Category | Data Extracted | Example Query |
|----------|----------------|---------------|
| **Crops** | Seasons, growth time, regrowth, sell prices | "How long do strawberries take to grow?" |
| **Fish** | Location, time, seasons, weather, difficulty | "Where can I catch a salmon?" |
| **Bundles** | Required items, quantities | "What do I need for the Spring Crops Bundle?" |
| **NPCs** | Gift preferences, heart events, marriageable status, address, family, birthday | "What are Sebastian's heart events?" |
| **Recipes** | Ingredients, buffs, energy/health, unlock source, recipe type, **processing times & products** (for machines) | "What can I make in a Keg?" |
| **Skills** | Level progression (1-10), crafting recipes unlocked, profession choices (levels 5 & 10) | "What professions can I choose for Farming?" |
| **Quests** | Quest name, description, provider, requirements, rewards, timeframe (Story Quests, Special Orders, Qi's Orders) | "What are all the story quests?" |
| **Achievements** | Achievement name, description/requirements, unlocks (49 achievements total) | "What achievements are there?" |
| **Animals** | Building required, purchase price, produce | "How much does a cow cost?" |
| **Items** | Source, sell/purchase prices | "Where do I get hardwood?" |
| **Monsters** | HP, damage, defense, speed, XP, drops, locations | "What are skeleton stats?" |
| **Collections** | Item lists (artifacts, minerals) with descriptions, sell prices, locations | "What artifacts can I find?" |

### Coverage Statistics
- **12 major categories** with excellent data extraction
- **461 wiki categories** discovered (167 content categories)
- **2,003 content pages** in the wiki
- **Automatic page type detection** (crops, fish, NPCs, bundles, recipes, etc.)

### Smart Tool Selection
The tools include guidance to help Claude choose the right one:
- **Use `search_wiki`** for: finding pages, festivals, achievements, general info
- **Use `get_page_data`** for: crops, fish, NPCs, bundles, recipes, animals, items, monsters

## Architecture

```
User: "What gifts does Sebastian love?"
    ↓
Claude Code (decides to use get_page_data)
    ↓
MCP Protocol (stdio)
    ↓
stardew_wiki_mcp.py
    ↓
  1. Fetches page HTML via MediaWiki API
  2. Detects page type (NPC)
  3. Parses with NPC parser
  4. Extracts gift preferences
    ↓
Returns structured JSON: {"loved_gifts": [...]}
    ↓
Claude: "Sebastian loves Frog Egg, Obsidian, Pumpkin Soup..."
```

## Installation

### Step 1: Install Dependencies

```bash
cd C:\opt\stardew\mcp_servers
pip install -r requirements.txt
```

Dependencies:
- `mcp>=1.0.0` - MCP Python SDK
- `requests>=2.31.0` - HTTP library
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser

### Step 2: Test Before Configuring

Verify the server works standalone:

```bash
python test_wiki_client.py
```

### Step 3: Configure MCP

**Option A: Project-Specific (Recommended)**

Edit `.claude.json` in your project root (`C:\opt\stardew`):

```json
{
  "mcpServers": {
    "stardew-wiki": {
      "command": "python",
      "args": ["C:/opt/stardew/mcp_servers/stardew_wiki_mcp.py"]
    }
  }
}
```

**Option B: Global Configuration**

Edit `%USERPROFILE%\.claude\settings.json`:

```json
{
  "mcpServers": {
    "stardew-wiki": {
      "command": "python",
      "args": ["C:/opt/stardew/mcp_servers/stardew_wiki_mcp.py"]
    }
  }
}
```

**Important:**
- Use **forward slashes** (`/`) in paths (not backslashes)
- Project-level `.claude.json` overrides global settings

### Step 4: Restart Claude Code

Close and reopen Claude Code. The MCP server starts automatically.

## Usage Examples

### Search for Pages
```
User: "Tell me about the Egg Festival"
Claude: [Uses search_wiki("Egg Festival")]
→ Returns page snippets about the festival
```

### Extract Structured Data
```
User: "What's the best gift for Abigail?"
Claude: [Uses get_page_data("Abigail")]
→ Returns: {"loved_gifts": ["Amethyst", "Magic Rock Candy", ...]}
Claude: "Abigail loves Amethyst, Magic Rock Candy..."
```

```
User: "When can I catch catfish?"
Claude: [Uses get_page_data("Catfish")]
→ Returns: {"location": "River", "seasons": ["Spring", "Fall"], "weather": "Rain"}
Claude: "Catfish are found in rivers during Spring and Fall when it's raining."
```

## File Structure

```
mcp_servers/
├── stardew_wiki_mcp.py        # Main MCP server (heavily commented)
├── requirements.txt            # Python dependencies
├── test_wiki_client.py         # Standalone test script
├── wiki_category_analyzer.py   # Category discovery tool
├── README.md                   # This file
├── roadmap.md                  # Development roadmap
└── plan.md                     # Detailed implementation guide
```

## Parser Coverage Details

### Excellent Coverage (Full Structured Data)

**Crops**
- Fields: `seasons`, `growth_time`, `regrowth_time`, `sell_prices`
- Example: Strawberry → `{"growth_time": 8, "seasons": ["Spring"]}`

**Fish**
- Fields: `location`, `time`, `seasons`, `weather`
- Example: Salmon → `{"location": "River", "seasons": ["Fall"], "time": "6am-7pm"}`

**Bundles**
- Fields: `requirements` (items and quantities)
- Filters out rewards automatically
- Handles remixed bundles

**NPCs**
- Fields: `loved_gifts`, `liked_gifts`, `neutral_gifts`, `disliked_gifts`, `hated_gifts`
- Filters out wiki notes automatically

**Animals**
- Fields: `building`, `purchase_price`, `produce`
- Prices cleaned to integers (e.g., `1500` not `"1,500g"`)

**Items**
- Fields: `source`, `sell_price`, `purchase_price`
- Handles commas in prices

**Monsters**
- Fields: `base_hp`, `base_damage`, `base_def`, `speed`, `xp`, `drops`, `spawns_in`
- Quality varies by page structure

### Partial Coverage

**Skills** - Extracts some data but field names are concatenated
**Festivals** - Minimal extraction (informational pages)
**Achievements** - Basic data only

## Phase 2 Enhancements (New! ✨)

### Recipe Parser
- **Type detection**: Automatically distinguishes cooking vs. crafting recipes
- **Ingredients**: Parses concatenated format (e.g., "Wood(50)Coal(1)Fiber(20)")
- **Buffs & effects**: Extracts buff names, duration, energy/health restoration
- **Unlock sources**: How to obtain the recipe
- **Example**: Algae Soup → `{"ingredients": [{"item": "Green Algae", "quantity": 4}], "energy": 75, "health": 33}`

### Enhanced NPC Parser
- **Marriageable status**: Boolean field indicating marriage candidates
- **Address/residence**: Where the NPC lives
- **Family members**: Parents, siblings, spouse, children
- **Heart events**: Automatically extracts all heart events (2, 4, 6, 8, 10, 14 hearts)
  - Event titles and heart level requirements
  - Trigger conditions (when available)
- **Example**: Sebastian → `{"marriageable": true, "address": "24 Mountain Road", "heart_events": [{"heart_level": 2, "title": "Two Hearts"}, ...]}`

### Monster Stats Enhancement
- **Integer conversion**: Stats (HP, damage, defense, speed, XP) now returned as integers instead of strings
- **Cleaner data**: `{"base_hp": 140}` instead of `{"base_hp": "140"}`
- **Example**: Skeleton → `{"base_hp": 140, "base_damage": 10, "xp": 8}`

## Roadmap

See `roadmap.md` for the complete development plan.

### Phase 2 (Complete ✅)
- [x] Recipe parser (ingredients, buffs, energy)
- [x] Enhanced NPC parser (heart events, marriageable status, address, family)
- [x] Standardized monster parser (integer stats conversion)
- [ ] Skills & professions parser (deferred to Phase 3)

### Phase 3 (Complete ✅)
- [x] Skills & professions parser (5 skills with profession trees)
- [x] Quest parser (82 quests: Story, Special Orders, Qi)
- [x] Achievement tracker (49 achievements)
- [x] Collections parser (Artifacts, Minerals)
- [x] Building enhancements (Processing machines with products/times)
- [x] **Comprehensive parser QA testing** (94.7% pass rate, 36/38 tests)
- [ ] Location shop inventory (deferred to Phase 4)
- [ ] Search query preprocessing (optional enhancement)

### Phase 4 (Production Ready)
- [ ] Comprehensive error handling
- [ ] Performance optimization
- [ ] Test suite
- [ ] Full API documentation

## Development

### Running Tests

Test individual parsers:
```bash
cd mcp_servers
python -c "
from stardew_wiki_mcp import WikiClient, parse_page_data, WIKI_API_URL

client = WikiClient(WIKI_API_URL)
result = client.get_page('Strawberry')
parsed = parse_page_data(result['html'], 'Strawberry', result.get('categories', []))
print(parsed)
"
```

Discover wiki categories:
```bash
python wiki_category_analyzer.py
```

### Adding New Parsers

See `plan.md` for detailed implementation instructions. Basic pattern:

1. **Analyze page structure** - Use BeautifulSoup to examine HTML
2. **Create parser function** - Extract data to structured dict
3. **Add to page type detection** - Update `detect_page_type()`
4. **Integrate into routing** - Update `parse_page_data()`
5. **Test thoroughly** - Multiple example pages

### Code Style

- **Heavily commented** - Every function explains what/why/how
- **Type hints** - Use `dict[str, Any]` for clarity
- **Error handling** - Graceful degradation, don't fail entire parse
- **Consistent naming** - `parse_X_data()` for parsers

## Troubleshooting

### MCP Server Not Loading

Check `/doctor` in Claude Code:
```bash
# Should show:
# ✓ stardew-wiki: Connected
```

If not:
1. Verify path in `.claude.json` is correct
2. Check Python is in PATH: `python --version`
3. Verify dependencies: `pip list | grep mcp`
4. Check logs in Claude Code console

### No Data Extracted

Some pages may not have structured infoboxes:
```bash
# Test manually
python test_wiki_client.py "page name"
```

If returns minimal data (`type` and `name` only), the page may be:
- An informational overview page (use `search_wiki` instead)
- Missing proper infobox structure
- Needs a custom parser (see `roadmap.md`)

### Import Errors

```bash
# Fix missing dependencies
pip install -r requirements.txt

# Or install individually
pip install mcp requests beautifulsoup4 lxml
```

### Performance Issues

- Wiki API has rate limits (be respectful)
- Large pages take longer to parse
- Consider caching for frequently accessed pages (Phase 4)

## Contributing

Want to add a parser? See `plan.md` for detailed instructions.

Priority areas:
1. Recipe parser (Phase 2.1)
2. NPC schedules/events (Phase 2.2)
3. Quest parser (Phase 3)

## Resources

- [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page)
- [Stardew Valley Wiki](https://stardewvalleywiki.com)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Documentation](https://modelcontextprotocol.io/introduction)

## License

This is a learning project built collaboratively. The code is heavily commented to help you understand how MCP servers work.

---

**Status**: Phase 1 & 2 Complete ✅ | Ready for Phase 3 Development
