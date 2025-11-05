# Item Database Documentation

## Overview

The item_database.py module provides a comprehensive mapping of Stardew Valley item IDs to their names, categories, sources, and acquisition methods.

## Core Functions

### get_item_info(item_id)

Returns complete information about an item.

**Usage:**
```python
from item_database import get_item_info

item = get_item_info('725')
# Returns:
# {
#     'name': 'Oak Resin',
#     'category': 'artisan_goods',
#     'source': 'tapper',
#     'season': 'any',
#     'location': 'farm',
#     'sell_price': 150,
#     'acquisition': 'Place a Tapper on an Oak Tree, collect every 6-7 days'
# }
```

**Parameters:**
- `item_id` (str|int): The item ID to look up

**Returns:**
- dict: Item information including name, category, source, acquisition guide
- If item not found, returns placeholder with 'Unknown Item (ID)'

### get_item_name(item_id)

Returns just the item name.

**Usage:**
```python
from item_database import get_item_name

name = get_item_name('637')
# Returns: 'Pomegranate'
```

### get_item_acquisition_guide(item_id)

Returns detailed instructions on how to obtain an item.

**Usage:**
```python
from item_database import get_item_acquisition_guide

guide = get_item_acquisition_guide('613')
# Returns: 'Plant an Apple Sapling (4,000g from Pierre's), wait 28 days, harvest in fall'
```

### get_wiki_url(item_id)

Generates a Stardew Valley Wiki URL for the item.

**Usage:**
```python
from item_database import get_wiki_url

url = get_wiki_url('725')
# Returns: 'https://stardewvalleywiki.com/Oak_Resin'
```

### get_quality_name(quality_level)

Converts quality level integer to readable name.

**Usage:**
```python
from item_database import get_quality_name

quality = get_quality_name(2)
# Returns: 'Gold'
```

**Quality Levels:**
- 0: Normal
- 1: Silver
- 2: Gold
- 4: Iridium

### get_items_by_category(category)

Returns all items in a specific category.

**Usage:**
```python
from item_database import get_items_by_category

crops = get_items_by_category('crop')
# Returns: Dictionary of all crop items
```

**Available Categories:**
- `crop`: Farmable crops
- `foraging`: Foraged items
- `fish`: Catchable fish
- `fruit`: Fruit tree products
- `animal_product`: Items from animals
- `artisan_goods`: Processed items (wine, cheese, etc.)
- `metal_bar`: Smelted bars
- `mineral`: Gems and minerals
- `currency`: Gold

### get_items_by_season(season)

Returns all items available in a specific season.

**Usage:**
```python
from item_database import get_items_by_season

spring_items = get_items_by_season('spring')
# Returns: All items obtainable in spring
```

**Seasons:**
- `spring`, `summer`, `fall`, `winter`, `any`

## Item Database Structure

### Format

```python
ITEM_DATABASE = {
    'item_id': {
        'name': str,              # Display name
        'category': str,          # Item category
        'source': str,            # How it's obtained
        'season': str,            # When available
        'location': str,          # Where to find/create
        'sell_price': int,        # Base sell price
        'acquisition': str        # Detailed how-to-get guide
    }
}
```

### Example Entry

```python
'725': {
    'name': 'Oak Resin',
    'category': 'artisan_goods',
    'source': 'tapper',
    'season': 'any',
    'location': 'farm',
    'sell_price': 150,
    'acquisition': 'Place a Tapper on an Oak Tree, collect every 6-7 days'
}
```

## Coverage

### Currently Supported Items

The database includes **150+ essential items**:

**Crops:**
- Spring: Parsnip, Green Bean, Cauliflower, Potato
- Summer: Melon, Tomato, Blueberry, Hot Pepper, Wheat, Radish
- Fall: Corn, Eggplant, Artichoke, Pumpkin, Bok Choy, Yam

**Foraging:**
- Spring: Wild Horseradish, Daffodil, Leek, Dandelion, Morel
- Summer: Spice Berry, Grape, Sweet Pea
- Fall: Common Mushroom, Wild Plum, Hazelnut, Blackberry, Chanterelle
- Winter: Winter Root, Crystal Fruit, Snow Yam, Crocus
- Special: Red Mushroom, Purple Mushroom

**Fruits:**
- Apple, Apricot, Orange, Peach, Pomegranate, Cherry

**Animal Products:**
- Eggs (regular, brown, large), Milk, Goat Milk, Wool, Duck Egg, Duck Feather, Rabbit's Foot, Hay

**Artisan Goods:**
- Honey, Cheese, Goat Cheese, Cloth, Truffle Oil, Mayonnaise, Duck Mayonnaise, Wine, Juice
- Oak Resin, Pine Tar, Maple Syrup

**Fish:**
- Ocean: Pufferfish, Anchovy, Tuna, Sardine, Red Mullet, Herring, Eel, Octopus, Red Snapper, Squid, Sea Cucumber
- River: Bream, Smallmouth Bass, Rainbow Trout, Salmon, Walleye, Catfish, Pike, Sunfish
- Lake: Largemouth Bass, Perch, Carp
- Special: Stonefish, Crimsonfish, Angler, Legend, Lava Eel, Sandfish, Scorpion Carp

**Minerals:**
- Copper Bar, Iron Bar, Gold Bar, Iridium Bar, Refined Quartz
- Quartz, Fire Quartz, Frozen Tear, Earth Crystal

### Missing Items

Items not yet in the database will return:
```python
{
    'name': 'Unknown Item (ID)',
    'category': 'unknown',
    'source': 'unknown',
    'season': 'unknown',
    'location': 'unknown',
    'sell_price': 0,
    'acquisition': 'Check the Stardew Valley Wiki for more information'
}
```

## Adding New Items

### Step 1: Find Item ID

Reference: https://stardewvalleywiki.com/Modding:Object_data

### Step 2: Add to ITEM_DATABASE

```python
'item_id': {
    'name': 'Item Name',
    'category': 'category_name',
    'source': 'how_obtained',
    'season': 'availability',
    'location': 'where_found',
    'sell_price': 000,
    'acquisition': 'Detailed acquisition instructions'
}
```

### Step 3: Test

```python
python item_database.py
```

Verify the item appears in test output.

## Category Reference

### crop
Farmable crops purchased as seeds and grown on the farm.

**Source values:** `farming`

**Example:**
```python
'24': {
    'name': 'Parsnip',
    'category': 'crop',
    'source': 'farming',
    'season': 'spring',
    'location': 'farm',
    'sell_price': 35,
    'acquisition': 'Buy Parsnip Seeds from Pierre\'s (20g), plant in spring, harvest in 4 days'
}
```

### foraging
Items found on the ground or foraged from trees.

**Source values:** `foraging`

**Example:**
```python
'16': {
    'name': 'Wild Horseradish',
    'category': 'foraging',
    'source': 'foraging',
    'season': 'spring',
    'location': 'all areas',
    'sell_price': 50,
    'acquisition': 'Forage on the ground in spring (all areas)'
}
```

### fish
Items caught with fishing rod.

**Source values:** `fishing`

**Example:**
```python
'128': {
    'name': 'Pufferfish',
    'category': 'fish',
    'source': 'fishing',
    'season': 'summer',
    'location': 'ocean',
    'sell_price': 200,
    'acquisition': 'Fish in the ocean on sunny days during summer, 12pm-4pm'
}
```

### fruit
Products from fruit trees planted on farm.

**Source values:** `fruit_tree`

**Example:**
```python
'637': {
    'name': 'Pomegranate',
    'category': 'fruit',
    'source': 'fruit_tree',
    'season': 'fall',
    'location': 'farm',
    'sell_price': 140,
    'acquisition': 'Plant a Pomegranate Sapling (6,000g from Pierre\'s), wait 28 days, harvest in fall'
}
```

### animal_product
Items produced by farm animals.

**Source values:** `chickens`, `cows`, `goats`, `sheep`, `ducks`, `rabbits`, `pigs`

**Example:**
```python
'446': {
    'name': 'Rabbit\'s Foot',
    'category': 'animal_product',
    'source': 'rabbits',
    'season': 'any',
    'location': 'coop',
    'sell_price': 565,
    'acquisition': 'Raise rabbits in a Deluxe Coop, collect randomly (very rare, increases with friendship)'
}
```

### artisan_goods
Processed items created from machines.

**Source values:** `bee_house`, `cheese_press`, `loom`, `oil_maker`, `mayonnaise_machine`, `keg`, `tapper`

**Example:**
```python
'725': {
    'name': 'Oak Resin',
    'category': 'artisan_goods',
    'source': 'tapper',
    'season': 'any',
    'location': 'farm',
    'sell_price': 150,
    'acquisition': 'Place a Tapper on an Oak Tree, collect every 6-7 days'
}
```

### metal_bar
Bars smelted in furnaces from ore.

**Source values:** `smelting`

**Example:**
```python
'334': {
    'name': 'Copper Bar',
    'category': 'metal_bar',
    'source': 'smelting',
    'season': 'any',
    'location': 'furnace',
    'sell_price': 60,
    'acquisition': 'Smelt 5 Copper Ore in a furnace with 1 coal'
}
```

### mineral
Gems, crystals, and minerals found in mines or geodes.

**Source values:** `mining`, `geodes`, `panning`

**Example:**
```python
'82': {
    'name': 'Fire Quartz',
    'category': 'mineral',
    'source': 'mining',
    'season': 'any',
    'location': 'mines',
    'sell_price': 100,
    'acquisition': 'Mine in the Mines levels 80+ or pan in rivers'
}
```

## Integration with Bundle System

The item database integrates seamlessly with the bundle tracking system:

```python
from bundle_definitions import get_bundle_info
from item_database import get_item_name, get_item_acquisition_guide

bundle = get_bundle_info(35)  # Fodder Bundle
for item in bundle['items']:
    name = get_item_name(item['id'])
    guide = get_item_acquisition_guide(item['id'])
    print(f"{name}: {guide}")
```

**Output:**
```
Wheat: Buy Wheat Seeds from Pierre's (10g), plant in summer or fall, harvest in 4 days
Hay: Cut grass with a scythe, or buy from Marnie (50g each)
Apple: Plant an Apple Sapling (4,000g from Pierre's), wait 28 days, harvest in fall
```

## Performance

### Lookup Time
- O(1) constant time for item lookups (dictionary access)
- ~0.0001 seconds per lookup
- No noticeable performance impact even with large queries

### Memory Usage
- ~100KB for entire database in memory
- Negligible impact on system resources

## Best Practices

### When to Use get_item_info()
Use when you need complete item details:
```python
item = get_item_info('725')
print(f"{item['name']}: {item['sell_price']}g")
print(f"Category: {item['category']}")
print(f"How to get: {item['acquisition']}")
```

### When to Use get_item_name()
Use when you only need the name (faster, simpler):
```python
name = get_item_name('725')
print(f"Missing: {name}")
```

### Handling Unknown Items
Always check for unknown items:
```python
item = get_item_info(unknown_id)
if item['name'].startswith('Unknown Item'):
    print(f"Item {unknown_id} not in database")
    # Add to database or check wiki
```

### Batch Lookups
For multiple items, batch the lookups:
```python
item_ids = ['725', '637', '613']
items = [get_item_info(id) for id in item_ids]

for item in items:
    print(f"{item['name']}: {item['acquisition']}")
```

## Future Enhancements

### Planned Additions
1. **Recipe information** (cooking/crafting)
2. **Gift preferences** (loved/liked by which NPCs)
3. **Bundle usage** (which bundles require each item)
4. **Profitability analysis** (sell price vs. processing value)
5. **Growth time** (days to harvest for crops)

### XNB Extraction
Future plan to auto-generate database from game files:
```python
def extract_items_from_xnb():
    """Extract item data from ObjectInformation.xnb"""
    # Parse game files
    # Auto-generate ITEM_DATABASE
    # Keep updated with game patches
```

## Troubleshooting

### Problem: Item shows as "Unknown Item (ID)"

**Solution:** Add the item to ITEM_DATABASE:
1. Look up item ID on wiki
2. Add entry with all required fields
3. Test with `python item_database.py`

### Problem: Acquisition guide is outdated

**Solution:** Update the item entry:
```python
'item_id': {
    # ... other fields
    'acquisition': 'Updated instructions here'
}
```

### Problem: Modded item not supported

**Solution:** Add custom entry:
```python
'mod_item_id': {
    'name': 'Modded Item',
    'category': 'mod',
    'source': 'mod_source',
    'season': 'any',
    'location': 'mod_location',
    'sell_price': 0,
    'acquisition': 'Provided by [Mod Name]'
}
```

## References

- [Object Data Reference](https://stardewvalleywiki.com/Modding:Object_data)
- [Item IDs List](https://stardewids.com/)
- [Stardew Valley Wiki](https://stardewvalleywiki.com/)
