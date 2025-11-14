# Stardew Valley Wiki MCP - API Reference

Complete reference documentation for the Stardew Valley Wiki MCP server tools.

---

## Overview

The Stardew Valley Wiki MCP server provides two tools for accessing wiki data:

1. **`search_wiki`** - Search for pages by keyword
2. **`get_page_data`** - Extract structured data from specific pages

Both tools use the MediaWiki API and include error handling, caching, and rate limiting.

---

## Tool: `search_wiki`

Search the Stardew Valley Wiki for items, NPCs, locations, mechanics, and more.

### Description

Returns a list of matching pages with titles and snippets. Best for finding page names, exploratory searches, festival information, achievements, seasonal overviews, and general game mechanics.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search term (e.g., 'apple', 'sebastian', 'community center') |
| `limit` | integer | No | 10 | Maximum results to return (min: 1, max: 50) |

### Returns

**Success Response:**
```json
{
  "success": true,
  "count": 5,
  "query": "strawberry",
  "results": [
    {
      "title": "Strawberry",
      "snippet": "Strawberry is a fruit crop that grows from <b>Strawberry</b> Seeds after 8 days...",
      "url": "https://stardewvalleywiki.com/Strawberry"
    },
    {
      "title": "Strawberry Seeds",
      "snippet": "<b>Strawberry</b> Seeds are a seed that can be planted to grow strawberries...",
      "url": "https://stardewvalleywiki.com/Strawberry_Seeds"
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to connect to wiki: Connection timeout"
}
```

### Usage Examples

**Basic Search:**
```json
{
  "query": "apple"
}
```

**Limited Results:**
```json
{
  "query": "spring crops",
  "limit": 5
}
```

**NPC Search:**
```json
{
  "query": "Sebastian"
}
```

### Best Practices

- Use general terms for exploratory searches
- Use specific names when you know what you're looking for
- Start with `search_wiki` to find the correct page title
- Then use `get_page_data` with the exact title for structured data

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "query parameter is required" | Missing query | Provide a search term |
| "Failed to connect" | Network error | Check connection, will auto-retry 3 times |
| "No results found" | No matches | Try different search terms |

---

## Tool: `get_page_data`

Extract structured data from a specific Stardew Valley Wiki page.

### Description

Returns structured JSON data extracted from wiki pages. Best for crops (seasons, growth time), fish (location, time, weather), NPCs (gift preferences, heart events), bundles (requirements), recipes (ingredients, buffs), animals (costs, produce), monsters (stats, drops), and items (prices, sources).

**NOT recommended for:** Festivals, achievements, skills, or seasonal overview pages (use `search_wiki` instead).

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_title` | string | Yes | Exact title of wiki page (e.g., 'Strawberry', 'Sebastian', 'Spring Crops Bundle') |

### Returns

**Success Response Structure:**

The response structure varies by page type. All responses include:

```json
{
  "success": true,
  "page_title": "Strawberry",
  "page_url": "https://stardewvalleywiki.com/Strawberry",
  "categories": ["Crops", "Spring Crops", "Fruits"],
  "data": {
    // Type-specific structured data
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Page 'InvalidName' not found on the wiki. Try using the search_wiki tool first to find the correct page name."
}
```

### Supported Page Types

The parser automatically detects page type and extracts relevant data:

#### 1. Crops

**Example Request:**
```json
{
  "page_title": "Strawberry"
}
```

**Response Data:**
```json
{
  "type": "crop",
  "name": "Strawberry",
  "seasons": ["Spring"],
  "growth_time": 8,
  "regrowth": 4,
  "sell_price": 120,
  "seed_price": 100,
  "seed_source": "Egg Festival",
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `seasons` - Which seasons the crop grows in
- `growth_time` - Days to maturity
- `regrowth` - Days between harvests (if applicable)
- `sell_price` - Base sell price
- `seed_price` - Cost to purchase seeds
- `seed_source` - Where to buy seeds

#### 2. NPCs

**Example Request:**
```json
{
  "page_title": "Sebastian"
}
```

**Response Data:**
```json
{
  "type": "npc",
  "name": "Sebastian",
  "birthday": "Winter 10",
  "address": "Mountain",
  "family": ["Robin (Mother)", "Maru (Half-sister)", "Demetrius (Step-father)"],
  "marriageable": true,
  "best_gifts": ["Frozen Tear", "Obsidian", "Pumpkin Soup", "Sashimi", "Void Egg"],
  "gift_tastes": {
    "love": ["Frozen Tear", "Obsidian", "..."],
    "like": ["Quartz", "..."],
    "neutral": ["..."],
    "dislike": ["..."],
    "hate": ["..."]
  },
  "heart_events": [
    {
      "hearts": 2,
      "time": "3:00pm - 11:00pm",
      "location": "Sebastian's room",
      "conditions": "Not raining"
    }
  ],
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `birthday` - NPC's birthday
- `address` - Where they live
- `family` - Family members
- `marriageable` - Can they be married?
- `best_gifts` - Loved gifts
- `gift_tastes` - Full gift preference breakdown
- `heart_events` - Friendship event details

#### 3. Fish

**Example Request:**
```json
{
  "page_title": "Catfish"
}
```

**Response Data:**
```json
{
  "type": "fish",
  "name": "Catfish",
  "locations": ["River (Town + Forest)", "Secret Woods (pond)"],
  "seasons": ["Spring", "Fall"],
  "time": "6am - 12am",
  "weather": "Rainy",
  "difficulty": 75,
  "sell_price": 200,
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `locations` - Where to catch it
- `seasons` - When it's available
- `time` - Time of day
- `weather` - Weather requirement
- `difficulty` - Fishing difficulty (1-100)
- `sell_price` - Base sell price

#### 4. Recipes

**Example Request:**
```json
{
  "page_title": "Fried Egg"
}
```

**Response Data:**
```json
{
  "type": "recipe",
  "name": "Fried Egg",
  "source": "Cooking Channel (Queen of Sauce Year 1 Spring 21)",
  "ingredients": [
    {"name": "Egg", "quantity": 1}
  ],
  "produces": [
    {"name": "Fried Egg", "quantity": 1}
  ],
  "energy": 50,
  "health": 22,
  "buffs": [],
  "sell_price": 35,
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `source` - How to obtain recipe
- `ingredients` - Required items
- `produces` - Output items
- `energy` - Energy restored
- `health` - Health restored
- `buffs` - Status effects
- `sell_price` - Cooked item value

#### 5. Bundles

**Example Request:**
```json
{
  "page_title": "Spring Crops Bundle"
}
```

**Response Data:**
```json
{
  "type": "bundle",
  "name": "Spring Crops Bundle",
  "room": "Pantry",
  "requirements": [
    {"name": "Parsnip", "quantity": 1, "quality": "normal"},
    {"name": "Green Bean", "quantity": 1, "quality": "normal"},
    {"name": "Cauliflower", "quantity": 1, "quality": "normal"},
    {"name": "Potato", "quantity": 1, "quality": "normal"}
  ],
  "required_items": 4,
  "reward": "20 Speed-Gro",
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `room` - Community Center room
- `requirements` - Items needed
- `required_items` - How many to complete
- `reward` - Bundle reward

#### 6. Collections (Artifacts, Minerals)

**Example Request:**
```json
{
  "page_title": "Artifacts"
}
```

**Response Data:**
```json
{
  "type": "collection",
  "name": "Artifacts",
  "collection_type": "artifact",
  "items": [
    {
      "name": "Dwarf Scroll I",
      "description": "A yellowed scroll of parchment...",
      "locations": ["Mines (floors 1-40)"],
      "sell_price": 1
    }
  ],
  "total_items": 42,
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `collection_type` - Type of collection
- `items` - Collection items with details
- `total_items` - Count of items

#### 7. Generic Items

**Example Request:**
```json
{
  "page_title": "Wood"
}
```

**Response Data:**
```json
{
  "type": "item",
  "name": "Wood",
  "description": "A sturdy, yet flexible plant material with a wide variety of uses.",
  "sell_price": 2,
  "sources": ["Chopping Trees", "Driftwood"],
  "used_in": ["Crafting", "Construction"],
  "parsing_warnings": []
}
```

**Fields Extracted:**
- `description` - Item description
- `sell_price` - Base value
- `sources` - How to obtain
- `used_in` - Uses

### Graceful Degradation

All parsers include graceful degradation:

- If some data is missing, partial results are returned
- Malformed sections are skipped without failing
- `parsing_warnings` array contains any issues encountered

**Example with Warnings:**
```json
{
  "type": "crop",
  "name": "Strange Crop",
  "seasons": ["Spring"],
  "parsing_warnings": [
    "Failed to extract growth_time: Missing infobox row",
    "Failed to extract sell_price: Price table not found"
  ]
}
```

### Usage Examples

**Get Crop Data:**
```json
{
  "page_title": "Strawberry"
}
```

**Get NPC Data:**
```json
{
  "page_title": "Sebastian"
}
```

**Get Bundle Data:**
```json
{
  "page_title": "Spring Crops Bundle"
}
```

### Best Practices

1. **Use Exact Titles:** Page titles are case-sensitive and must match exactly
2. **Search First:** Use `search_wiki` to find the correct title
3. **Handle Warnings:** Check `parsing_warnings` for incomplete data
4. **Cache Results:** Results are cached for 1 hour by default
5. **Type Detection:** Parser auto-detects page type from categories

### Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Page not found" | Invalid page title | Use `search_wiki` to find correct title |
| "Failed to connect" | Network error | Auto-retries 3 times with exponential backoff |
| "Failed to parse page" | Unusual page format | Check `parsing_warnings`, report if recurring |
| "Page redirects to" | Page is a redirect | Use the target page instead |

---

## Performance Features

### Caching

- **TTL:** 1 hour (3600 seconds)
- **Max Size:** 100 entries
- **Eviction:** FIFO (First In, First Out)
- **Key:** Case-insensitive page titles

**Cache Statistics:**
```python
{
  "size": 15,
  "hits": 42,
  "misses": 15,
  "hit_rate_percent": 73.7,
  "ttl_seconds": 3600
}
```

### Rate Limiting

- **Default Rate:** 5 requests/second
- **Algorithm:** Token bucket
- **Thread-Safe:** Yes
- **Automatic:** Waits between requests as needed

### Retry Logic

- **Max Retries:** 3
- **Backoff:** Exponential (1s → 2s → 4s)
- **Retries On:** Network timeouts, connection errors
- **No Retry:** Page not found, parse errors

---

## Error Types

### Custom Exceptions

All errors are wrapped in custom exception types for better handling:

#### `WikiError`
Base exception for all wiki operations.

#### `PageNotFoundError`
```python
PageNotFoundError("NonExistentPage")
# Message: "Page 'NonExistentPage' not found on the wiki.
# Try using the search_wiki tool first to find the correct page name."
```

#### `NetworkError`
```python
NetworkError("https://wiki.com/api.php", ConnectionTimeout())
# Message: "Failed to connect to https://wiki.com/api.php: Connection timeout.
# Please check your internet connection and try again."
```

#### `ParseError`
```python
ParseError("StrangePage", "Missing required infobox")
# Message: "Failed to parse page 'StrangePage': Missing required infobox.
# The page may have an unusual format. Please report this issue."
```

#### `RedirectError`
```python
RedirectError("Starfruit", "Starfruit (crop)")
# Message: "Page 'Starfruit' redirects to 'Starfruit (crop)'.
# Use 'Starfruit (crop)' instead for better results."
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug logging |

**Enable Debug Mode:**
```bash
DEBUG=true python stardew_wiki_mcp.py
```

### WikiClient Configuration

```python
WikiClient(
    api_url="https://stardewvalleywiki.com/mediawiki/api.php",
    cache_ttl=3600,          # Cache TTL in seconds
    cache_max_size=100,      # Max cached entries
    rate_limit=5.0           # Requests per second
)
```

---

## Rate Limits

**MediaWiki API Limits:**
- Typical limit: 10-20 requests/second
- Our default: 5 requests/second (conservative)
- Burst protection: Token bucket algorithm

**Recommendations:**
- Use caching to minimize API calls
- Batch similar requests together
- Don't disable rate limiting (risk of ban)

---

## Response Times

**Typical Performance:**

| Operation | First Request | Cached Request |
|-----------|--------------|----------------|
| `search_wiki` | ~200-300ms | <1ms |
| `get_page_data` (simple) | ~220ms | <1ms |
| `get_page_data` (complex) | ~350ms | <1ms |

**Performance Improvement:** ~220x faster for cached requests

---

## Version Information

**API Version:** 1.0
**MCP Protocol:** 1.0
**MediaWiki API:** 1.39
**Last Updated:** 2025-11-13

---

## Support

**Issues:** Report bugs or request features on the project repository
**Documentation:** See PARSER_COVERAGE.md for detailed parser capabilities
**Contributing:** See CONTRIBUTING.md for development guidelines
**Troubleshooting:** See TROUBLESHOOTING.md for common issues

---

## Quick Reference

### Workflow

1. **Search** → Use `search_wiki` to find page titles
2. **Extract** → Use `get_page_data` with exact title
3. **Handle** → Check `success` and `parsing_warnings`
4. **Cache** → Repeated requests are instant

### Common Patterns

**Find and Extract:**
```javascript
// 1. Search for the page
search_wiki({query: "strawberry"})
// → Found: "Strawberry" (exact match)

// 2. Get structured data
get_page_data({page_title: "Strawberry"})
// → Returns: crop data with seasons, growth time, etc.
```

**Handle Errors:**
```javascript
if (!result.success) {
  console.error(result.error);
  // Check if page not found → try searching
  // Check if network error → will auto-retry
}
```

**Check Data Quality:**
```javascript
if (result.data.parsing_warnings.length > 0) {
  console.warn("Partial data:", result.data.parsing_warnings);
  // Data is still usable, just incomplete
}
```

---

## See Also

- **PARSER_COVERAGE.md** - Detailed parser capabilities and field extraction
- **CONTRIBUTING.md** - How to add new parsers and improve existing ones
- **TROUBLESHOOTING.md** - Common issues and solutions
- **tests/README.md** - Test suite documentation
