# Stardew Valley Wiki MCP - Detailed Execution Plan

## Purpose

This document provides detailed, step-by-step instructions for implementing each phase of the roadmap. Use this as a technical guide during development.

---

## Phase 2: High Priority Custom Parsers

### 2.1 Recipe Parser Implementation

**Objective**: Extract structured recipe data (ingredients, buffs, energy, sources)

#### Step 1: Analyze Recipe Page Structure
```bash
cd mcp_servers && python -c "
from stardew_wiki_mcp import WikiClient, WIKI_API_URL
from bs4 import BeautifulSoup

client = WikiClient(WIKI_API_URL)

# Test multiple recipe types
test_recipes = ['Algae Soup', 'Fried Egg', 'Coffee']  # Cooking recipes
test_recipes += ['Chest', 'Furnace', 'Scarecrow']     # Crafting recipes

for recipe in test_recipes:
    result = client.get_page(recipe)
    if result['success']:
        soup = BeautifulSoup(result['html'], 'lxml')

        # Find all tables
        tables = soup.find_all('table')
        print(f'\n{recipe}: {len(tables)} tables')

        # Look for ingredient tables
        for i, table in enumerate(tables[:3]):
            text = table.get_text(strip=True)[:200]
            print(f'  Table {i}: {text}')
"
```

#### Step 2: Identify Data Patterns
Look for:
- Ingredients table (usually labeled "Ingredients")
- Recipe source (how to unlock)
- Buff effects (if applicable)
- Energy/health restoration
- Sell price

#### Step 3: Create `parse_recipe_data()` Function

Add to `stardew_wiki_mcp.py` after existing parsers:

```python
def parse_recipe_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for cooking and crafting recipes.

    Extracts:
    - Recipe type (cooking or crafting)
    - Ingredients with quantities
    - Buff effects (cooking only)
    - Energy/health restoration
    - Source/unlock method
    - Sell price
    """
    data = {
        "type": "recipe",
        "name": page_title,
    }

    # Get main infobox
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                # Parse specific fields
                if "ingredient" in key:
                    # Parse ingredients table
                    # Format: "Item Name (Quantity)"
                    ingredients = []
                    for item_cell in cells[1].find_all("a"):
                        item_name = item_cell.get_text(strip=True)
                        # Look for quantity in nearby text
                        parent_text = item_cell.parent.get_text(strip=True)
                        qty_match = re.search(r'(\d+)', parent_text)
                        quantity = int(qty_match.group(1)) if qty_match else 1
                        ingredients.append({"item": item_name, "quantity": quantity})

                    if ingredients:
                        data["ingredients"] = ingredients

                elif "source" in key:
                    data["source"] = value

                elif "buff" in key:
                    data["buff"] = value

                elif "energy" in key or "health" in key:
                    # Extract numeric values
                    numbers = re.findall(r'(\d+)', value)
                    if len(numbers) >= 2:
                        data["energy"] = int(numbers[0])
                        data["health"] = int(numbers[1])

                elif "sell" in key and "price" in key:
                    match = re.search(r'(\d+)g', value.replace(',', ''))
                    if match:
                        data["sell_price"] = int(match.group(1))

    return data
```

#### Step 4: Integrate into Page Type Detection

Update `detect_page_type()`:
```python
def detect_page_type(categories: list[str], page_title: str = "") -> str:
    # ... existing code ...

    # Add recipe detection
    if any("recipe" in c for c in cat_lower) or any("cooking" in c for c in cat_lower):
        return "recipe"

    # ... rest of code ...
```

Update `parse_page_data()`:
```python
def parse_page_data(html: str, page_title: str, categories: list[str]) -> dict[str, Any]:
    # ... existing code ...

    elif page_type == "recipe":
        return parse_recipe_data(soup, page_title)

    # ... rest of code ...
```

#### Step 5: Test Recipe Parser
```bash
cd mcp_servers && python -c "
from stardew_wiki_mcp import WikiClient, parse_page_data, WIKI_API_URL

client = WikiClient(WIKI_API_URL)
test_recipes = ['Algae Soup', 'Chest', 'Coffee']

for recipe in test_recipes:
    result = client.get_page(recipe)
    if result['success']:
        parsed = parse_page_data(result['html'], recipe, result.get('categories', []))
        print(f'\n{recipe}:')
        print(f'  Ingredients: {parsed.get(\"ingredients\", \"N/A\")}')
        print(f'  Source: {parsed.get(\"source\", \"N/A\")}')
        print(f'  Buff: {parsed.get(\"buff\", \"N/A\")}')
"
```

---

### 2.2 NPC Schedule & Events Parser Implementation

**Objective**: Extract NPC schedules, heart events, and relationship data

#### Step 1: Analyze NPC Page Structure
```bash
cd mcp_servers && python -c "
from stardew_wiki_mcp import WikiClient, WIKI_API_URL
from bs4 import BeautifulSoup

client = WikiClient(WIKI_API_URL)
result = client.get_page('Abigail')

if result['success']:
    soup = BeautifulSoup(result['html'], 'lxml')

    # Find Schedule section
    for h2 in soup.find_all('h2'):
        if 'schedule' in h2.get_text().lower():
            print('Found Schedule section')
            # Get next table or div
            sibling = h2.find_next_sibling()
            print(f'Next sibling: {sibling.name if sibling else None}')

    # Find Heart Events section
    for h2 in soup.find_all('h2'):
        if 'heart event' in h2.get_text().lower():
            print('\nFound Heart Events section')
            # Find all h3 subheadings (Two Hearts, Four Hearts, etc.)
            next_h2 = h2.find_next('h2')
            current = h2.find_next('h3')
            while current and (not next_h2 or current.sourceline < next_h2.sourceline):
                print(f'  Event: {current.get_text(strip=True)}')
                current = current.find_next('h3')
"
```

#### Step 2: Create Schedule Parser

Complex due to:
- Seasonal variations
- Weather conditions
- Day-of-week variations
- Marriage status changes

**Recommendation**: Start simple, enhance later
```python
def parse_npc_schedule(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse NPC schedule information.

    Note: Schedules are complex with many conditional variations.
    This parser extracts basic structure.
    """
    schedules = {}

    # Find Schedule heading
    for h2 in soup.find_all('h2'):
        if 'schedule' in h2.get_text().lower():
            # Look for schedule tables or lists
            # Implementation depends on wiki format
            pass

    return schedules
```

#### Step 3: Create Heart Event Parser
```python
def parse_heart_events(soup: BeautifulSoup) -> list[dict]:
    """
    Extract heart event information.

    Returns list of events with:
    - heart_level (2, 4, 6, 8, 10, 14)
    - trigger conditions
    - location
    """
    events = []

    # Find Heart Events section
    for h2 in soup.find_all('h2'):
        if 'heart event' in h2.get_text().lower():
            # Find all h3 subheadings
            next_h2 = h2.find_next('h2')
            current = h2.find_next('h3')

            while current and (not next_h2 or current != next_h2):
                event_title = current.get_text(strip=True)

                # Extract heart level from title
                match = re.search(r'(\w+)\s+Heart', event_title)
                if match:
                    heart_word = match.group(1).lower()
                    heart_map = {'two': 2, 'four': 4, 'six': 6, 'eight': 8, 'ten': 10, 'fourteen': 14}
                    heart_level = heart_map.get(heart_word)

                    if heart_level:
                        events.append({
                            "heart_level": heart_level,
                            "title": event_title
                        })

                current = current.find_next('h3')
                if current and next_h2 and current.sourceline >= next_h2.sourceline:
                    break

    return events
```

#### Step 4: Update NPC Parser

Enhance existing `parse_npc_data()`:
```python
def parse_npc_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    data = {
        "type": "npc",
        "name": page_title,
    }

    # ... existing gift preference code ...

    # Add birthday
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if "birthday" in key:
                    data["birthday"] = value
                elif "marriage" in key:
                    data["marriageable"] = "yes" in value.lower()
                elif "address" in key:
                    data["address"] = value

    # Add heart events
    heart_events = parse_heart_events(soup)
    if heart_events:
        data["heart_events"] = heart_events

    # Add schedule (if implemented)
    # schedules = parse_npc_schedule(soup)
    # if schedules:
    #     data["schedule"] = schedules

    return data
```

---

### 2.3 Monster Combat Parser Implementation

**Objective**: Standardize monster stat extraction

#### Step 1: Analyze Well-Structured vs Poorly-Structured Pages

Already did this - Skeleton has excellent structure, Green Slime has minimal.

Strategy: Enhance generic parser to handle monster-specific fields better.

#### Step 2: Add Monster-Specific Field Handling

In `parse_generic_item()`, add special cases for monster stats:

```python
def parse_generic_item(soup: BeautifulSoup, page_title: str, item_type: str) -> dict[str, Any]:
    # ... existing code ...

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)

                clean_key = re.sub(r'[^\w\s]', '', key).lower().replace(' ', '_')
                if clean_key:
                    # Special handling for prices
                    if clean_key in ['sell_price', 'purchase_price', 'buy_price']:
                        # ... existing price code ...

                    # Special handling for monster stats (numeric fields)
                    elif clean_key in ['base_hp', 'base_damage', 'base_def', 'speed', 'xp']:
                        match = re.search(r'(\d+)', value)
                        if match:
                            data[clean_key] = int(match.group(1))
                        else:
                            data[clean_key] = value

                    # Special handling for drop tables
                    elif clean_key == 'drops':
                        # Parse drop table (complex - may need custom parser)
                        data[clean_key] = value  # Store raw for now

                    else:
                        data[clean_key] = value

    return data
```

#### Step 3: Test Monster Parser
```bash
cd mcp_servers && python -c "
from stardew_wiki_mcp import WikiClient, parse_page_data, WIKI_API_URL

client = WikiClient(WIKI_API_URL)
monsters = ['Skeleton', 'Green Slime', 'Frost Bat']

for monster in monsters:
    result = client.get_page(monster)
    if result['success']:
        parsed = parse_page_data(result['html'], monster, result.get('categories', []))
        print(f'\n{monster}:')
        print(f'  HP: {parsed.get(\"base_hp\", \"N/A\")}')
        print(f'  Damage: {parsed.get(\"base_damage\", \"N/A\")}')
        print(f'  Defense: {parsed.get(\"base_def\", \"N/A\")}')
        print(f'  XP: {parsed.get(\"xp\", \"N/A\")}')
"
```

---

### 2.4 Skills & Professions Parser Implementation

**Objective**: Extract level progression and profession trees

This is the most complex parser due to nested table structures.

#### Step 1: Analyze Skill Page Structure
```bash
cd mcp_servers && python -c "
from stardew_wiki_mcp import WikiClient, WIKI_API_URL
from bs4 import BeautifulSoup

client = WikiClient(WIKI_API_URL)
result = client.get_page('Farming')

if result['success']:
    soup = BeautifulSoup(result['html'], 'lxml')

    # Look for level progression table
    for table in soup.find_all('table'):
        caption = table.find('caption')
        if caption and 'level' in caption.get_text().lower():
            print('Found level progression table')
            print(f'Rows: {len(table.find_all(\"tr\"))}')

    # Look for profession sections
    for h3 in soup.find_all('h3'):
        if 'profession' in h3.get_text().lower():
            print(f'Found profession section: {h3.get_text(strip=True)}')
"
```

#### Step 2: Create Skills Parser

Due to complexity, recommend Phase 3 implementation. For Phase 2, document the structure and create placeholder.

```python
def parse_skill_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract skill level progression and profession trees.

    TODO: Complex implementation needed for:
    - Level 1-10 progression table
    - Profession choices at levels 5 and 10
    - XP requirements
    - Unlocked recipes per level
    """
    data = {
        "type": "skill",
        "name": page_title,
    }

    # Placeholder: Extract basic info from infobox
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    # Mark as TODO for Phase 3
    data["_parser_status"] = "basic_only_full_implementation_pending"

    return data
```

---

## Phase 3: Medium Priority Implementation

### 3.1 Quest Parser

#### Discovery Phase
```bash
# Find quest pages
cd mcp_servers && python -c "
from stardew_wiki_mcp import WikiClient, WIKI_API_URL

client = WikiClient(WIKI_API_URL)
result = client.search('quest', limit=20)

if result['success']:
    print('Quest-related pages:')
    for item in result['results']:
        print(f'  - {item[\"title\"]}')
"
```

#### Implementation
Similar pattern to recipes:
1. Analyze page structure
2. Create `parse_quest_data()`
3. Extract requirements, rewards, triggers
4. Add to page type detection
5. Test

### 3.2 Achievement Parser

Achievements page is a list/table format. Need to:
1. Parse achievement table
2. Extract requirements per achievement
3. Return array of achievement objects

### 3.3 Collections Parser

Collections span multiple page types:
- Museum (artifacts/minerals)
- Fishing (all fish caught)
- Cooking (all recipes cooked)
- Shipping (all items shipped)

May need multiple sub-parsers or a unified collection tracker.

---

## Testing Strategy

### Unit Tests
For each parser, create tests:
```python
def test_recipe_parser():
    # Test with known good pages
    test_cases = [
        ('Algae Soup', {'ingredients': [...], 'energy': 38}),
        ('Chest', {'ingredients': [...]}),
    ]

    for page_title, expected in test_cases:
        result = parse_page(page_title)
        assert result['ingredients'] == expected['ingredients']
```

### Integration Tests
Test full MCP tool flow:
```python
async def test_get_page_data_tool():
    result = await call_tool('get_page_data', {'page_title': 'Strawberry'})
    assert 'growth_time' in result
    assert result['growth_time'] == 8
```

### Regression Tests
Save known-good parser outputs:
```bash
# Capture current state
python capture_parser_outputs.py > baseline.json

# After changes, compare
python capture_parser_outputs.py > current.json
diff baseline.json current.json
```

---

## Error Handling Patterns

### Graceful Degradation
```python
try:
    ingredients = parse_ingredients(table)
    data['ingredients'] = ingredients
except Exception as e:
    logger.warning(f"Failed to parse ingredients for {page_title}: {e}")
    # Don't fail entire parse, just skip this field
```

### Validation
```python
def validate_recipe_data(data: dict) -> bool:
    """Ensure critical fields are present."""
    required = ['type', 'name']
    return all(field in data for field in required)
```

---

## Documentation Updates

After each phase:
1. Update README with new supported categories
2. Update tool descriptions with new capabilities
3. Add examples to documentation
4. Update CHANGELOG

---

## Deployment Checklist

Before considering "production ready":
- [ ] All Phase 2 parsers implemented and tested
- [ ] Error handling comprehensive
- [ ] Performance acceptable (<500ms avg)
- [ ] Documentation complete
- [ ] Test coverage >80%
- [ ] Known limitations documented
- [ ] MCP server stable across Claude Code restarts

---

## Next Action

Start with Phase 2.1 (Recipe Parser) - follow steps above in order.
