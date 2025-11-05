"""
Stardew Valley Community Center Bundle Definitions
Based on standard game data (no mods)

Reference: https://stardewvalleywiki.com/Bundles
Item IDs: https://stardewvalleywiki.com/Modding:Object_data
"""

# Format: bundle_id: {name, items: [{id, name, quantity, quality}]}
BUNDLE_DEFINITIONS = {
    # PANTRY (Crafts Room)
    0: {
        'name': 'Spring Crops',
        'items': [
            {'id': '24', 'name': 'Parsnip', 'quantity': 1, 'quality': 0},
            {'id': '188', 'name': 'Green Bean', 'quantity': 1, 'quality': 0},
            {'id': '190', 'name': 'Cauliflower', 'quantity': 1, 'quality': 0},
            {'id': '192', 'name': 'Potato', 'quantity': 1, 'quality': 0},
        ],
        'required': 4  # Need all 4
    },
    1: {
        'name': 'Summer Crops',
        'items': [
            {'id': '256', 'name': 'Tomato', 'quantity': 1, 'quality': 0},
            {'id': '260', 'name': 'Hot Pepper', 'quantity': 1, 'quality': 0},
            {'id': '258', 'name': 'Blueberry', 'quantity': 1, 'quality': 0},
            {'id': '254', 'name': 'Melon', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
    2: {
        'name': 'Fall Crops',
        'items': [
            {'id': '270', 'name': 'Corn', 'quantity': 1, 'quality': 0},
            {'id': '272', 'name': 'Eggplant', 'quantity': 1, 'quality': 0},
            {'id': '276', 'name': 'Pumpkin', 'quantity': 1, 'quality': 0},
            {'id': '280', 'name': 'Yam', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
    3: {
        'name': 'Quality Crops',
        'items': [
            {'id': '24', 'name': 'Parsnip', 'quantity': 5, 'quality': 2},  # Gold
            {'id': '254', 'name': 'Melon', 'quantity': 5, 'quality': 2},
            {'id': '276', 'name': 'Pumpkin', 'quantity': 5, 'quality': 2},
            {'id': '270', 'name': 'Corn', 'quantity': 5, 'quality': 2},
        ],
        'required': 3  # Need 3 of 4
    },
    4: {
        'name': 'Animal',
        'items': [
            {'id': '186', 'name': 'Large Egg', 'quantity': 1, 'quality': 0},
            {'id': '182', 'name': 'Large Egg (Brown)', 'quantity': 1, 'quality': 0},
            {'id': '174', 'name': 'Large Milk', 'quantity': 1, 'quality': 0},
            {'id': '438', 'name': 'Large Goat Milk', 'quantity': 1, 'quality': 0},
            {'id': '440', 'name': 'Wool', 'quantity': 1, 'quality': 0},
            {'id': '442', 'name': 'Duck Egg', 'quantity': 1, 'quality': 0},
        ],
        'required': 5  # Need 5 of 6
    },
    5: {
        'name': 'Artisan',
        'items': [
            {'id': '432', 'name': 'Truffle Oil', 'quantity': 1, 'quality': 0},
            {'id': '428', 'name': 'Cloth', 'quantity': 1, 'quality': 0},
            {'id': '426', 'name': 'Goat Cheese', 'quantity': 1, 'quality': 0},
            {'id': '424', 'name': 'Cheese', 'quantity': 1, 'quality': 0},
            {'id': '340', 'name': 'Honey', 'quantity': 1, 'quality': 0},
            {'id': '344', 'name': 'Jelly', 'quantity': 1, 'quality': 0},
            {'id': '613', 'name': 'Apple', 'quantity': 1, 'quality': 0},
            {'id': '634', 'name': 'Apricot', 'quantity': 1, 'quality': 0},
            {'id': '635', 'name': 'Orange', 'quantity': 1, 'quality': 0},
            {'id': '636', 'name': 'Peach', 'quantity': 1, 'quality': 0},
            {'id': '637', 'name': 'Pomegranate', 'quantity': 1, 'quality': 0},
            {'id': '638', 'name': 'Cherry', 'quantity': 1, 'quality': 0},
        ],
        'required': 6  # Need 6 of 12
    },

    # FISH TANK
    6: {
        'name': 'River Fish',
        'items': [
            {'id': '145', 'name': 'Sunfish', 'quantity': 1, 'quality': 0},
            {'id': '143', 'name': 'Catfish', 'quantity': 1, 'quality': 0},
            {'id': '706', 'name': 'Shad', 'quantity': 1, 'quality': 0},
            {'id': '699', 'name': 'Tiger Trout', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
    7: {
        'name': 'Lake Fish',
        'items': [
            {'id': '136', 'name': 'Largemouth Bass', 'quantity': 1, 'quality': 0},
            {'id': '142', 'name': 'Carp', 'quantity': 1, 'quality': 0},
            {'id': '700', 'name': 'Bullhead', 'quantity': 1, 'quality': 0},
            {'id': '698', 'name': 'Sturgeon', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
    8: {
        'name': 'Ocean Fish',
        'items': [
            {'id': '131', 'name': 'Sardine', 'quantity': 1, 'quality': 0},
            {'id': '130', 'name': 'Tuna', 'quantity': 1, 'quality': 0},
            {'id': '150', 'name': 'Red Snapper', 'quantity': 1, 'quality': 0},
            {'id': '701', 'name': 'Tilapia', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
    9: {
        'name': 'Night Fishing',
        'items': [
            {'id': '140', 'name': 'Walleye', 'quantity': 1, 'quality': 0},
            {'id': '132', 'name': 'Bream', 'quantity': 1, 'quality': 0},
            {'id': '148', 'name': 'Eel', 'quantity': 1, 'quality': 0},
        ],
        'required': 3
    },
    10: {
        'name': 'Specialty Fish',
        'items': [
            {'id': '128', 'name': 'Pufferfish', 'quantity': 1, 'quality': 0},
            {'id': '156', 'name': 'Ghostfish', 'quantity': 1, 'quality': 0},
            {'id': '164', 'name': 'Sandfish', 'quantity': 1, 'quality': 0},
            {'id': '165', 'name': 'Woodskip', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },

    # BULLETIN BOARD
    20: {
        'name': "Chef's Bundle",
        'items': [
            {'id': '724', 'name': 'Maple Bar', 'quantity': 1, 'quality': 0},
            {'id': '216', 'name': 'Bread', 'quantity': 1, 'quality': 0},
            {'id': '220', 'name': 'Chocolate Cake', 'quantity': 1, 'quality': 0},
            {'id': '234', 'name': 'Maki Roll', 'quantity': 1, 'quality': 0},
            {'id': '648', 'name': 'Coleslaw', 'quantity': 1, 'quality': 0},
            {'id': '732', 'name': 'Rhubarb Pie', 'quantity': 1, 'quality': 0},
        ],
        'required': 6
    },
    # BULLETIN BOARD
    31: {
        'name': "Chef's Bundle",
        'items': [
            {'id': '724', 'name': 'Maple Syrup', 'quantity': 1, 'quality': 0},
            {'id': '259', 'name': 'Fiddlehead Fern', 'quantity': 1, 'quality': 0},
            {'id': '430', 'name': 'Truffle', 'quantity': 1, 'quality': 0},
            {'id': '376', 'name': 'Poppy', 'quantity': 1, 'quality': 0},
            {'id': '228', 'name': 'Maki Roll', 'quantity': 1, 'quality': 0},
            {'id': '194', 'name': 'Fried Egg', 'quantity': 1, 'quality': 0},
        ],
        'required': 4  # 4 of 6 items required
    },
    32: {
        'name': "Field Research Bundle",
        'items': [
            {'id': '422', 'name': 'Purple Mushroom', 'quantity': 1, 'quality': 0},
            {'id': '392', 'name': 'Nautilus Shell', 'quantity': 1, 'quality': 0},
            {'id': '702', 'name': 'Chub', 'quantity': 1, 'quality': 0},
            {'id': '536', 'name': 'Frozen Geode', 'quantity': 1, 'quality': 0},
        ],
        'required': 4,  # All 4 items required
        'all_required': True
    },
    33: {
        'name': "Enchanter's Bundle",
        'items': [
            {'id': '725', 'name': 'Oak Resin', 'quantity': 1, 'quality': 0},
            {'id': '348', 'name': 'Wine', 'quantity': 1, 'quality': 0},
            {'id': '446', 'name': "Rabbit's Foot", 'quantity': 1, 'quality': 0},
            {'id': '637', 'name': 'Pomegranate', 'quantity': 1, 'quality': 0},
        ],
        'required': 4,  # All 4 items required
        'all_required': True
    },
    34: {
        'name': "Dye Bundle",
        'items': [
            {'id': '420', 'name': 'Red Mushroom', 'quantity': 1, 'quality': 0},
            {'id': '397', 'name': 'Sea Urchin', 'quantity': 1, 'quality': 0},
            {'id': '421', 'name': 'Sunflower', 'quantity': 1, 'quality': 0},
            {'id': '444', 'name': 'Duck Feather', 'quantity': 1, 'quality': 0},
            {'id': '62', 'name': 'Aquamarine', 'quantity': 1, 'quality': 0},
            {'id': '266', 'name': 'Red Cabbage', 'quantity': 1, 'quality': 0},
        ],
        'required': 6,  # All 6 items required
        'all_required': True
    },
    35: {
        'name': 'Fodder Bundle',
        'items': [
            {'id': '262', 'name': 'Wheat', 'quantity': 10, 'quality': 0},
            {'id': '178', 'name': 'Hay', 'quantity': 10, 'quality': 0},
            {'id': '613', 'name': 'Apple', 'quantity': 3, 'quality': 0},
        ],
        'required': 3,  # All 3 items required
        'all_required': True
    },
    36: {
        'name': 'The Missing Bundle',
        'items': [
            {'id': '348', 'name': 'Wine', 'quantity': 1, 'quality': 1},  # Silver quality
            {'id': '807', 'name': 'Dinosaur Egg', 'quantity': 1, 'quality': 0},
            {'id': '74', 'name': 'Prismatic Shard', 'quantity': 1, 'quality': 0},
            {'id': '454', 'name': 'Ancient Fruit', 'quantity': 5, 'quality': 2},  # Gold quality
            {'id': '795', 'name': 'Void Salmon', 'quantity': 1, 'quality': 2},  # Gold quality
            {'id': '445', 'name': 'Caviar', 'quantity': 1, 'quality': 0},
        ],
        'required': 5  # 5 of 6 items required
    },

    # CRAFTS ROOM
    13: {
        'name': 'Spring Foraging Bundle',
        'items': [
            {'id': '16', 'name': 'Wild Horseradish', 'quantity': 1, 'quality': 0},
            {'id': '18', 'name': 'Daffodil', 'quantity': 1, 'quality': 0},
            {'id': '20', 'name': 'Leek', 'quantity': 1, 'quality': 0},
            {'id': '22', 'name': 'Dandelion', 'quantity': 1, 'quality': 0},
        ],
        'required': 4,  # All 4 items required
        'all_required': True
    },
    14: {
        'name': 'Summer Foraging Bundle',
        'items': [
            {'id': '396', 'name': 'Spice Berry', 'quantity': 1, 'quality': 0},
            {'id': '398', 'name': 'Grape', 'quantity': 1, 'quality': 0},
            {'id': '402', 'name': 'Sweet Pea', 'quantity': 1, 'quality': 0},
        ],
        'required': 3,  # All 3 items required
        'all_required': True
    },
    19: {
        'name': 'Exotic Foraging Bundle',
        'items': [
            {'id': '88', 'name': 'Coconut', 'quantity': 1, 'quality': 0},
            {'id': '90', 'name': 'Cactus Fruit', 'quantity': 1, 'quality': 0},
            {'id': '78', 'name': 'Cave Carrot', 'quantity': 1, 'quality': 0},
            {'id': '420', 'name': 'Red Mushroom', 'quantity': 1, 'quality': 0},
            {'id': '422', 'name': 'Purple Mushroom', 'quantity': 1, 'quality': 0},
            {'id': '724', 'name': 'Maple Syrup', 'quantity': 1, 'quality': 0},
            {'id': '725', 'name': 'Oak Resin', 'quantity': 1, 'quality': 0},
            {'id': '726', 'name': 'Pine Tar', 'quantity': 1, 'quality': 0},
            {'id': '257', 'name': 'Morel', 'quantity': 1, 'quality': 0},
        ],
        'required': 5  # 5 of 9 items required
    },

    # VAULT
    23: {'name': '2,500g Bundle', 'items': [{'id': 'gold', 'name': 'Gold', 'quantity': 2500, 'quality': 0}], 'required': 1},
    24: {'name': '5,000g Bundle', 'items': [{'id': 'gold', 'name': 'Gold', 'quantity': 5000, 'quality': 0}], 'required': 1},
    25: {'name': '10,000g Bundle', 'items': [{'id': 'gold', 'name': 'Gold', 'quantity': 10000, 'quality': 0}], 'required': 1},
    26: {'name': '25,000g Bundle', 'items': [{'id': 'gold', 'name': 'Gold', 'quantity': 25000, 'quality': 0}], 'required': 1},

    # BOILER ROOM
    20: {
        'name': 'Blacksmith\'s Bundle',
        'items': [
            {'id': '334', 'name': 'Copper Bar', 'quantity': 1, 'quality': 0},
            {'id': '335', 'name': 'Iron Bar', 'quantity': 1, 'quality': 0},
            {'id': '336', 'name': 'Gold Bar', 'quantity': 1, 'quality': 0},
        ],
        'required': 3
    },
    21: {
        'name': 'Geologist\'s Bundle',
        'items': [
            {'id': '80', 'name': 'Quartz', 'quantity': 1, 'quality': 0},
            {'id': '82', 'name': 'Fire Quartz', 'quantity': 1, 'quality': 0},
            {'id': '84', 'name': 'Frozen Tear', 'quantity': 1, 'quality': 0},
            {'id': '86', 'name': 'Earth Crystal', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
    22: {
        'name': 'Adventurer\'s Bundle',
        'items': [
            {'id': '766', 'name': 'Slime', 'quantity': 99, 'quality': 0},
            {'id': '767', 'name': 'Bat Wing', 'quantity': 10, 'quality': 0},
            {'id': '768', 'name': 'Solar Essence', 'quantity': 1, 'quality': 0},
            {'id': '769', 'name': 'Void Essence', 'quantity': 1, 'quality': 0},
        ],
        'required': 4
    },
}

def get_bundle_info(bundle_id):
    """Get bundle definition by ID"""
    return BUNDLE_DEFINITIONS.get(bundle_id, None)

def get_missing_items_for_bundle(bundle_id, slots_filled):
    """
    Given a bundle ID and which slots are filled, return what's still needed.

    Bundle slot structure (discovered through empirical analysis):
    - ALL bundles allocate exactly 3 slots per item (consistent across all bundles)
    - The FIRST N slots map 1:1 to the N items (slot 0 = item 0, slot 1 = item 1, etc.)
    - The REMAINING slots are padding/unused
    - Only the first N slots matter for determining which items are submitted

    Args:
        bundle_id: The bundle ID
        slots_filled: List of booleans indicating which slots are filled

    Returns:
        List of items still needed to complete the bundle
    """
    bundle_def = get_bundle_info(bundle_id)
    if not bundle_def:
        return None

    items = bundle_def['items']
    item_count = len(items)
    required = bundle_def['required']
    all_required = bundle_def.get('all_required', False)

    if not slots_filled or item_count == 0:
        return items[:required] if not all_required else items

    # Use 1:1 mapping: first N slots correspond to N items
    # Only check the first item_count slots, ignore the rest (padding)
    relevant_slots = slots_filled[:item_count]

    # Determine which items are filled and which are missing
    filled_items = []
    missing_items = []

    for item_idx, item in enumerate(items):
        if item_idx < len(relevant_slots) and relevant_slots[item_idx]:
            filled_items.append(item)
        else:
            missing_items.append(item)

    # Calculate how many more items are needed
    items_filled_count = len(filled_items)
    remaining_needed = max(0, required - items_filled_count)

    if remaining_needed <= 0:
        return []  # Bundle complete

    # If all items are required, return all missing items
    if all_required:
        return missing_items

    # Otherwise, return only the number still needed for completion
    return missing_items[:remaining_needed]
