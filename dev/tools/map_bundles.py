"""
Map bundle definitions to actual bundle IDs

The bundleData array uses indices, but the actual bundles use IDs.
We need to map them to understand which definition goes with which ID.
"""

import xml.etree.ElementTree as ET
import json

SAVE_PATH = r'C:\Users\ryanc\AppData\Roaming\StardewValley\Saves\ryfarm_419564418\ryfarm_419564418'

def parse_bundle_string(bundle_str):
    """Parse a bundle definition string."""
    parts = bundle_str.split('/')
    if len(parts) < 4:
        return None

    name = parts[0]
    items_str = parts[2]
    min_to_complete = parts[4] if len(parts) > 4 and parts[4] else None

    # Parse items
    items = []
    item_parts = items_str.split()
    i = 0
    while i < len(item_parts):
        if item_parts[i].isdigit():
            item_id = item_parts[i]
            count = int(item_parts[i+1]) if i+1 < len(item_parts) else 1
            items.append({'id': item_id, 'count': count})
            i += 3
        else:
            i += 1

    return {
        'name': name,
        'items': items,
        'min_to_complete': int(min_to_complete) if min_to_complete else len(items)
    }


def create_complete_mapping():
    """Create a complete mapping of bundle definitions to actual bundles."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    # Get bundle definitions
    bundle_data = root.find('.//bundleData')
    definitions = []
    if bundle_data:
        items = bundle_data.findall('.//item')
        for i, item in enumerate(items):
            value_elem = item.find('.//value/string')
            if value_elem and value_elem.text:
                parsed = parse_bundle_string(value_elem.text)
                if parsed:
                    parsed['definition_index'] = i
                    definitions.append(parsed)

    # Get actual bundle states
    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
    bundle_items = cc.findall('.//bundles/item')

    actual_bundles = []
    for item in bundle_items:
        bundle_id = int(item.find('.//key/int').text)
        bool_array = item.find('.//value/ArrayOfBoolean')
        if bool_array:
            bools = bool_array.findall('.//boolean')
            slots = [b.text == 'true' for b in bools]

            actual_bundles.append({
                'id': bundle_id,
                'slot_count': len(slots),
                'filled_count': sum(slots),
                'slots': slots
            })

    # Try to match them
    print("="*80)
    print("BUNDLE MAPPING: Definition Index -> Actual ID")
    print("="*80)
    print(f"\n{'DefIdx':<8} {'ActualID':<10} {'Name':<30} {'Items':<7} {'Slots':<7} {'Filled':<8}")
    print("-" * 80)

    # Sort actual bundles by ID
    actual_bundles_sorted = sorted(actual_bundles, key=lambda x: x['id'])

    # Attempt mapping (they might be ordered the same)
    for i, (definition, actual) in enumerate(zip(definitions, actual_bundles_sorted)):
        print(f"{definition['definition_index']:<8} {actual['id']:<10} {definition['name'][:28]:<30} "
              f"{len(definition['items']):<7} {actual['slot_count']:<7} {actual['filled_count']:<8}")

    # Highlight the Fodder bundle specifically
    print("\n" + "="*80)
    print("FODDER BUNDLE ANALYSIS")
    print("="*80)

    fodder_def = next((d for d in definitions if 'Fodder' in d['name']), None)
    if fodder_def:
        print(f"\nDefinition (Index {fodder_def['definition_index']}):")
        print(f"  Name: {fodder_def['name']}")
        print(f"  Items required: {len(fodder_def['items'])}")
        print(f"  Min to complete: {fodder_def['min_to_complete']}")
        print(f"  Items:")
        for item in fodder_def['items']:
            print(f"    - ID {item['id']}: {item['count']}")

        # Find corresponding actual bundle
        # If they're in same order, it would be the 29th actual bundle
        if len(actual_bundles_sorted) > fodder_def['definition_index']:
            corresponding = actual_bundles_sorted[fodder_def['definition_index']]
            print(f"\nCorresponding Actual Bundle (ID {corresponding['id']}):")
            print(f"  Total slots: {corresponding['slot_count']}")
            print(f"  Filled slots: {corresponding['filled_count']}")
            print(f"  Ratio: {corresponding['slot_count']}/{len(fodder_def['items'])} = "
                  f"{corresponding['slot_count'] / len(fodder_def['items']):.1f} slots per item")

            # Check if slot pattern suggests completion
            print(f"\n  Slot pattern analysis:")
            print(f"    All slots filled: {all(corresponding['slots'])}")
            print(f"    Min items needed: {fodder_def['min_to_complete']}")
            print(f"    Items available: {len(fodder_def['items'])}")

            # If bundle allows choice, calculate how many item groups are needed
            if corresponding['slot_count'] % len(fodder_def['items']) == 0:
                slots_per_item = corresponding['slot_count'] // len(fodder_def['items'])
                print(f"    Slots per item: {slots_per_item}")

                # Check each item group
                print(f"\n    Item completion status:")
                for i in range(len(fodder_def['items'])):
                    start = i * slots_per_item
                    end = start + slots_per_item
                    item_slots = corresponding['slots'][start:end]
                    item_complete = any(item_slots)  # At least one slot filled
                    status = "[OK] Complete" if item_complete else "[X] Incomplete"
                    print(f"      Item {i+1} (ID {fodder_def['items'][i]['id']}): "
                          f"{sum(item_slots)}/{len(item_slots)} slots filled - {status}")


if __name__ == '__main__':
    create_complete_mapping()
