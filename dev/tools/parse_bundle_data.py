"""
Parse bundleData from save file

The bundleData element contains the actual bundle requirements.
Format: "Name/Reward/Items/Color/MinToComplete/DisplayName"
"""

import xml.etree.ElementTree as ET

SAVE_PATH = r'C:\Users\ryanc\AppData\Roaming\StardewValley\Saves\ryfarm_419564418\ryfarm_419564418'

def parse_bundle_string(bundle_str):
    """
    Parse a bundle definition string.

    Format: "Name/Reward/Items/Color/MinToComplete/DisplayName"
    Items format: "id count quality id count quality ..."
    """
    parts = bundle_str.split('/')

    if len(parts) < 4:
        return None

    name = parts[0]
    reward = parts[1]
    items_str = parts[2]
    color = parts[3]
    min_to_complete = parts[4] if len(parts) > 4 and parts[4] else None
    display_name = parts[5] if len(parts) > 5 else name

    # Parse items
    items = []
    item_parts = items_str.split()

    i = 0
    while i < len(item_parts):
        if item_parts[i].isdigit():
            item_id = item_parts[i]
            count = int(item_parts[i+1]) if i+1 < len(item_parts) else 1
            quality = int(item_parts[i+2]) if i+2 < len(item_parts) else 0

            items.append({
                'id': item_id,
                'count': count,
                'quality': quality
            })
            i += 3
        else:
            i += 1

    return {
        'name': name,
        'reward': reward,
        'items': items,
        'color': color,
        'min_to_complete': min_to_complete,
        'display_name': display_name,
        'total_items': len(items)
    }


def get_all_bundle_definitions():
    """Extract all bundle definitions from the save file."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    bundle_data = root.find('.//bundleData')
    if bundle_data is None:
        return None

    items = bundle_data.findall('.//item')

    bundles = []
    for i, item in enumerate(items):
        key_elem = item.find('.//key/string')
        value_elem = item.find('.//value/string')

        if value_elem is not None and value_elem.text:
            parsed = parse_bundle_string(value_elem.text)
            if parsed:
                # The key is often like "Pantry/0" or just the index
                key = key_elem.text if key_elem is not None else str(i)
                parsed['key'] = key
                parsed['index'] = i
                bundles.append(parsed)

    return bundles


def find_fodder_bundle():
    """Find and analyze the Fodder bundle definition."""
    bundles = get_all_bundle_definitions()

    print("="*80)
    print("SEARCHING FOR FODDER BUNDLE IN bundleData")
    print("="*80)

    for bundle in bundles:
        if 'Fodder' in bundle['name'] or 'fodder' in bundle['name'].lower():
            print(f"\nFound: {bundle['name']}")
            print(f"  Index: {bundle['index']}")
            print(f"  Key: {bundle['key']}")
            print(f"  Display Name: {bundle['display_name']}")
            print(f"  Total items defined: {bundle['total_items']}")
            print(f"  Min to complete: {bundle['min_to_complete']}")
            print(f"  Reward: {bundle['reward']}")
            print(f"\n  Items required:")
            for item in bundle['items']:
                quality_str = ['Any', 'Silver', 'Gold', '', 'Iridium'][item['quality']]
                print(f"    - Item ID {item['id']}: {item['count']} (quality: {quality_str})")

            return bundle

    print("\nFodder bundle not found by name. Listing all bundles:")
    for bundle in bundles:
        print(f"  [{bundle['index']}] {bundle['name']} ({bundle['total_items']} items)")

    return None


def analyze_slot_to_item_mapping():
    """Analyze the relationship between bundle definitions and ArrayOfBoolean slots."""
    bundles = get_all_bundle_definitions()

    # Also get the actual slot counts from save
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()
    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
    bundle_items = cc.findall('.//bundles/item')

    # Create mapping
    bundle_slots = {}
    for item in bundle_items:
        bundle_id = int(item.find('.//key/int').text)
        bool_array = item.find('.//value/ArrayOfBoolean')
        if bool_array:
            slots = len(bool_array.findall('.//boolean'))
            bundle_slots[bundle_id] = slots

    print("\n" + "="*80)
    print("BUNDLE DEFINITION vs ACTUAL SLOTS")
    print("="*80)
    print(f"\n{'Index':<6} {'Name':<30} {'Items':<6} {'Slots':<6} {'Ratio':<10} {'MinComplete':<12}")
    print("-" * 80)

    for i, bundle in enumerate(bundles):
        # Bundle ID might match index
        slots = bundle_slots.get(i, '?')
        ratio = f"{slots}/{bundle['total_items']}" if slots != '?' else '?'

        print(f"{i:<6} {bundle['name'][:28]:<30} {bundle['total_items']:<6} {str(slots):<6} {ratio:<10} {bundle['min_to_complete'] or 'All':<12}")


if __name__ == '__main__':
    fodder = find_fodder_bundle()
    analyze_slot_to_item_mapping()
