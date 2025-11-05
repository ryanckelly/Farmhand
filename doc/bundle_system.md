# Bundle Tracking System Documentation

## Overview

The Stardew Valley Companion tracks Community Center bundle progress by parsing save file XML data and comparing it against bundle definitions.

## How Bundle Slots Work

### The Slot Mystery - SOLVED

Through empirical analysis of save file data, we've discovered the true bundle slot structure:

**Universal Bundle Slot Structure:**
- **ALL bundles allocate exactly 3 slots per item** (consistent across every bundle)
- **The first N slots map 1:1 to the N items** (slot 0 = item 0, slot 1 = item 1, etc.)
- **The remaining slots are padding/unused** (for potential quality variations)
- **Only the first N slots matter** for determining bundle completion

**Examples:**
- **Fodder Bundle** (3 items, 9 slots): `[True, True, False, F×6]`
  - Slot 0 = Wheat ✓
  - Slot 1 = Hay ✓
  - Slot 2 = Apple ✗
  - Slots 3-8 = padding (ignored)

- **Vault Bundle** (1 item, 3 slots): `[True, False, False]`
  - Slot 0 = Gold ✓
  - Slots 1-2 = padding (ignored)

- **Spring Crops Bundle** (4 items, 12 slots): `[T, T, T, T, F×8]` when complete
  - Slots 0-3 = the 4 items
  - Slots 4-11 = padding (ignored)

### Why 3 Slots Per Item?

The game allocates 3 slots per item universally, likely to accommodate potential quality variations (Normal, Silver, Gold) or multiple submission attempts. However, **only the first slot position for each item actually matters** - the rest are unused padding.

## Bundle Completion Logic

### 1:1 Slot Mapping (Current Implementation)

```python
def count_filled_items_in_bundle(slots_filled, item_count):
    """
    Count how many unique items are filled in a bundle.

    Uses simple 1:1 mapping: first N slots = N items.
    Ignores all slots beyond position N (padding).
    """
    if not slots_filled or item_count == 0:
        return 0

    # Only check the first item_count slots (the rest are padding)
    relevant_slots = slots_filled[:item_count]
    return sum(1 for slot in relevant_slots if slot)
```

This simple approach works universally because:
1. Slot 0 always corresponds to item 0
2. Slot 1 always corresponds to item 1
3. And so on...
4. Everything after slot N-1 is ignored

### Completion Check

A bundle is complete when:
```python
if bundle['all_required']:
    is_complete = filled_items >= item_count
else:
    is_complete = filled_items >= bundle['required']
```

## Bundle Definitions

### Structure

```python
BUNDLE_DEFINITIONS = {
    bundle_id: {
        'name': 'Bundle Name',
        'items': [
            {'id': 'item_id', 'name': 'Item Name', 'quantity': 10, 'quality': 0},
            # ... more items
        ],
        'required': 3,           # Number of items needed for completion
        'all_required': False    # If True, ALL items must be submitted
    }
}
```

### Bundle IDs Reference

**Pantry (Room 0):**
- 0: Spring Crops Bundle
- 1: Summer Crops Bundle
- 2: Fall Crops Bundle
- 3: Quality Crops Bundle
- 4: Animal Bundle
- 5: Artisan Bundle

**Crafts Room (Room 1):**
- 13: Spring Foraging Bundle
- 14: Summer Foraging Bundle
- 19: Exotic Foraging Bundle

**Fish Tank (Room 2):**
- 6: River Fish Bundle
- 7: Lake Fish Bundle
- 8: Ocean Fish Bundle
- 9: Night Fishing Bundle
- 10: Specialty Fish Bundle
- 11: Crab Pot Bundle

**Boiler Room (Room 3):**
- 20: Blacksmith's Bundle
- 21: Geologist's Bundle
- 22: Adventurer's Bundle

**Vault (Room 4):**
- 23: 2,500g Bundle
- 24: 5,000g Bundle
- 25: 10,000g Bundle
- 26: 25,000g Bundle

**Bulletin Board (Room 5):**
- 31: Chef's Bundle
- 32: Field Research Bundle
- 33: Enchanter's Bundle
- 34: Dye Bundle
- 35: Fodder Bundle

**Abandoned Joja Mart (Room 6):**
- 36: The Missing Bundle

## Remixed Bundles

### Detection

Remixed bundles are detected by checking for bundle IDs outside the standard range:

```python
standard_bundle_ids = list(range(0, 11)) + list(range(15, 18)) + list(range(20, 26)) + [31]
remixed_detected = any(bid not in standard_bundle_ids for bid in all_bundle_ids)
```

### Configuration

When remixed bundles are enabled at farm creation:
- Some bundles are permanent (always present)
- Some bundles are randomized (may or may not appear)
- Different rooms have different numbers of random vs. permanent bundles

## Dual-State Validation

The system validates bundle completion using two independent sources:

### 1. Bundle Slot Arrays
Direct inspection of which slots are filled in each bundle.

### 2. Room Completion Flags
```python
# Check Community Center areasComplete
completed_rooms = [0, 1, 3, 4]  # Example: Pantry, Crafts Room, Boiler Room, Vault
```

### 3. Mail Flags
```python
# Check player's mailReceived for bundle rewards
bundle_reward_flags = ['ccPantry', 'ccFishTank', 'ccBoilerRoom', 'ccVault']
```

This redundancy helps validate completion accuracy.

## Common Issues

### Issue 1: Bundle Shows Incomplete When It Should Be Complete

**Symptom:** Save file shows all slots filled, but system reports bundle incomplete.

**Cause:** Using slot-based counting instead of item-based counting.

**Solution:** Use `count_filled_items_in_bundle()` to count unique items, not total slots.

### Issue 2: Unknown Bundle IDs

**Symptom:** Bundles with IDs like 13, 14, 19, 26, 33, 35, 36 show as "Bundle {id}".

**Cause:** Player has remixed bundles enabled, but definitions are missing.

**Solution:** Add remixed bundle definitions to `bundle_definitions.py`.

### Issue 3: Incorrect Item Count

**Symptom:** Bundle shows wrong number of missing items (e.g., Fodder shows "10 Hay, 3 Apple" when Hay is already submitted).

**Cause:** Slot alignment issue or incorrect slots_per_item calculation.

**Investigation Needed:**
1. Examine actual slot array from save file
2. Compare before/after item submission
3. Verify slot grouping matches item order

## Save File Behavior

**CRITICAL:** The save file only updates when you sleep (end the day) in Stardew Valley.

This means:
- Submit items to bundles in-game
- **Sleep to save the game**
- Exit Stardew Valley
- Run `session_tracker.py`

If you don't sleep before exiting, bundle changes won't be detected.

## File Structure

### save_analyzer.py
- `analyze_save()`: Main entry point
- `get_detailed_bundle_info(root)`: Parse bundle data from XML
- `count_filled_items_in_bundle(slots, item_count)`: Count unique filled items
- `get_room_completion_state(root)`: Extract validation flags

### bundle_definitions.py
- `BUNDLE_DEFINITIONS`: Dictionary of all bundle requirements
- `get_bundle_info(bundle_id)`: Look up bundle by ID
- `get_missing_items_for_bundle(bundle_id, slots_filled)`: Calculate missing items

### item_database.py
- `ITEM_DATABASE`: Complete item ID to name/info mapping
- `get_item_info(item_id)`: Look up item details
- `get_item_acquisition_guide(item_id)`: How to obtain item
- `get_wiki_url(item_id)`: Generate wiki link

## Usage Examples

### Check Bundle Status
```python
from save_analyzer import analyze_save

state = analyze_save()
bundles = state['bundles']

print(f"Bundles complete: {bundles['complete_count']}/{bundles['total_count']}")

for bundle in bundles['incomplete_bundles']:
    print(f"\n{bundle['name']}:")
    for item in bundle['needed_items']:
        print(f"  - {item}")
```

### Look Up Item Information
```python
from item_database import get_item_info, get_item_acquisition_guide

item = get_item_info('725')  # Oak Resin
print(f"{item['name']}: {item['sell_price']}g")
print(f"How to get: {get_item_acquisition_guide('725')}")
```

### Add New Bundle Definition
```python
# In bundle_definitions.py
BUNDLE_DEFINITIONS[99] = {
    'name': 'Custom Bundle',
    'items': [
        {'id': '24', 'name': 'Parsnip', 'quantity': 5, 'quality': 0},
        {'id': '192', 'name': 'Potato', 'quantity': 5, 'quality': 0},
    ],
    'required': 2,
    'all_required': True
}
```

## Testing

### Test Bundle Detection
```bash
python session_tracker.py
```

Check diary.json for bundle progress updates.

### Test Item Database
```python
python item_database.py
```

Verifies item lookups and category queries.

### Debug Bundle Slots
```python
from save_analyzer import parse_save_xml

root = parse_save_xml()
cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
              {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

for bundle in cc.findall('.//bundles/item'):
    bundle_id = int(bundle.find('.//key/int').text)
    completed_array = bundle.find('.//value/ArrayOfBoolean')
    slots = [b.text == 'true' for b in completed_array.findall('.//boolean')]
    print(f"Bundle {bundle_id}: {len(slots)} slots, {sum(slots)} filled")
```

## Future Enhancements

### Planned Features
1. Inventory cross-reference (check chests for bundle items)
2. Bundle prioritization by reward value
3. Seasonal alerts for time-sensitive items
4. XNB extraction for automatic bundle definitions
5. Visual progress indicators

### Known Limitations
1. Cannot detect in-progress bundle submissions (must sleep first)
2. Modded bundles not supported (only vanilla and remixed)
3. No support for alternative completion routes (Joja vs. Community Center choice detection needs improvement)

## Troubleshooting

### Problem: session_tracker.py shows no changes

**Solution:**
1. Verify you slept in-game before exiting
2. Check that save file timestamp has updated
3. Run `python save_analyzer.py` directly to see current state

### Problem: Bundle shows completed but game shows incomplete

**Solution:**
1. Check `bundle_reward_flags` in output
2. Verify room completion in `completed_rooms`
3. May indicate bundle definition mismatch (check wiki for actual requirements)

### Problem: "Unknown Item (ID)" in bundle output

**Solution:**
Add the item to `item_database.py`:
```python
'item_id': {
    'name': 'Item Name',
    'category': 'category',
    'source': 'source',
    'season': 'season',
    'location': 'location',
    'sell_price': 0,
    'acquisition': 'How to get it'
}
```

## References

- [Stardew Valley Wiki - Bundles](https://stardewvalleywiki.com/Bundles)
- [Stardew Valley Wiki - Remixed Bundles](https://stardewvalleywiki.com/Remixed_Bundles)
- [Modding Wiki - Bundle Data](https://wiki.stardewvalley.net/Modding:Bundles)
- [Item IDs Reference](https://stardewvalleywiki.com/Modding:Object_data)
