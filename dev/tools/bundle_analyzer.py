"""
Bundle Analyzer - Deep analysis of bundle structure in save file

This tool extracts ALL bundle data from the save file and looks for patterns
to understand the slot structure without requiring in-game testing.
"""

import xml.etree.ElementTree as ET
import sys
import json
from pathlib import Path

# Add parent directory to path to import bundle_definitions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from bundle_definitions import get_bundle_info

SAVE_PATH = r'C:\Users\ryanc\AppData\Roaming\StardewValley\Saves\ryfarm_419564418\ryfarm_419564418'

def analyze_all_bundles():
    """Extract and analyze all bundle data from the save file."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    if cc is None:
        return {'error': 'Community Center not found'}

    bundles = cc.findall('.//bundles/item')

    analysis = {
        'total_bundles': len(bundles),
        'bundles': [],
        'patterns': {}
    }

    # Track patterns
    slot_counts = {}

    for bundle in bundles:
        bundle_key = bundle.find('.//key/int')
        if bundle_key is None:
            continue

        bundle_id = int(bundle_key.text)

        # Get slot data
        completed_array = bundle.find('.//value/ArrayOfBoolean')
        if completed_array is not None:
            bool_values = completed_array.findall('.//boolean')
            slots = [b.text == 'true' for b in bool_values]
            slot_count = len(slots)
            filled_count = sum(slots)
        else:
            slots = []
            slot_count = 0
            filled_count = 0

        # Get bundle definition if available
        bundle_def = get_bundle_info(bundle_id)
        bundle_name = bundle_def['name'] if bundle_def else f'Unknown Bundle {bundle_id}'
        expected_items = len(bundle_def['items']) if bundle_def else None
        required = bundle_def.get('required', expected_items) if bundle_def else None

        bundle_data = {
            'id': bundle_id,
            'name': bundle_name,
            'slot_count': slot_count,
            'filled_count': filled_count,
            'slots': slots,
            'expected_items': expected_items,
            'required': required,
            'has_definition': bundle_def is not None
        }

        # Calculate slot ratio if we have definition
        if expected_items and expected_items > 0:
            bundle_data['slots_per_item'] = slot_count / expected_items

        analysis['bundles'].append(bundle_data)

        # Track patterns
        slot_counts[slot_count] = slot_counts.get(slot_count, 0) + 1

    # Analyze patterns
    analysis['patterns']['slot_count_distribution'] = slot_counts

    # Look for common slot ratios
    slot_ratios = {}
    for bundle in analysis['bundles']:
        if 'slots_per_item' in bundle:
            ratio = bundle['slots_per_item']
            ratio_key = f"{ratio:.1f}"
            if ratio_key not in slot_ratios:
                slot_ratios[ratio_key] = []
            slot_ratios[ratio_key].append({
                'id': bundle['id'],
                'name': bundle['name'],
                'slots': bundle['slot_count'],
                'items': bundle['expected_items']
            })

    analysis['patterns']['slots_per_item_ratios'] = slot_ratios

    return analysis


def print_analysis(analysis):
    """Pretty print the analysis results."""
    print("="*80)
    print("BUNDLE STRUCTURE ANALYSIS")
    print("="*80)

    print(f"\nTotal bundles in save file: {analysis['total_bundles']}")

    print("\n" + "="*80)
    print("SLOT COUNT DISTRIBUTION")
    print("="*80)
    for slot_count, count in sorted(analysis['patterns']['slot_count_distribution'].items()):
        print(f"  {slot_count:2d} slots: {count:2d} bundles")

    print("\n" + "="*80)
    print("SLOTS PER ITEM RATIOS")
    print("="*80)
    for ratio, bundles in sorted(analysis['patterns']['slots_per_item_ratios'].items()):
        print(f"\n  Ratio {ratio}:1 (slots per item):")
        for b in bundles:
            print(f"    - {b['name']:30s} (ID {b['id']:2d}): {b['slots']:2d} slots / {b['items']:2d} items")

    print("\n" + "="*80)
    print("INDIVIDUAL BUNDLE DETAILS")
    print("="*80)

    # Group by completion status
    incomplete = [b for b in analysis['bundles'] if b['filled_count'] < b['slot_count']]
    complete_or_unknown = [b for b in analysis['bundles'] if b['filled_count'] >= b['slot_count']]

    print(f"\nINCOMPLETE BUNDLES ({len(incomplete)}):")
    print("-" * 80)
    for b in sorted(incomplete, key=lambda x: x['id']):
        ratio = f"{b.get('slots_per_item', 0):.1f}:1" if 'slots_per_item' in b else "N/A"
        print(f"  ID {b['id']:2d} | {b['name']:30s} | {b['filled_count']:2d}/{b['slot_count']:2d} filled | Ratio: {ratio}")
        if b['expected_items']:
            print(f"         Expected: {b['expected_items']} items, Required: {b['required']}")

    print(f"\nCOMPLETE/FULL BUNDLES ({len(complete_or_unknown)}):")
    print("-" * 80)
    for b in sorted(complete_or_unknown, key=lambda x: x['id']):
        ratio = f"{b.get('slots_per_item', 0):.1f}:1" if 'slots_per_item' in b else "N/A"
        print(f"  ID {b['id']:2d} | {b['name']:30s} | {b['filled_count']:2d}/{b['slot_count']:2d} filled | Ratio: {ratio}")


def find_fodder_and_enchanters():
    """Specifically examine the Fodder and Enchanter's bundles."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    bundles = cc.findall('.//bundles/item')

    print("\n" + "="*80)
    print("DETAILED ANALYSIS: FODDER & ENCHANTER'S BUNDLES")
    print("="*80)

    for bundle in bundles:
        bundle_id = int(bundle.find('.//key/int').text)

        if bundle_id not in [25, 31]:
            continue

        bundle_name = "Enchanter's" if bundle_id == 25 else "Fodder"

        print(f"\n{bundle_name} Bundle (ID {bundle_id}):")
        print("-" * 80)

        # Get the value element
        value = bundle.find('.//value')

        # Get slots
        completed_array = value.find('.//ArrayOfBoolean')
        if completed_array:
            bool_values = completed_array.findall('.//boolean')
            slots = [b.text == 'true' for b in bool_values]

            print(f"  Total slots: {len(slots)}")
            print(f"  Filled slots: {sum(slots)}")
            print(f"  Empty slots: {sum(1 for s in slots if not s)}")
            print(f"\n  Slot pattern:")

            # Print slots in groups of 6 for readability
            for i in range(0, len(slots), 6):
                group = slots[i:i+6]
                slot_str = [f"{'T' if s else 'F'}" for s in group]
                print(f"    Slots {i:2d}-{i+5:2d}: {' '.join(slot_str)}")

        # Look for any other fields
        print(f"\n  Other fields in value element:")
        for child in value:
            if child.tag != 'ArrayOfBoolean':
                print(f"    - {child.tag}: {child.text if child.text else '(empty)'}")


if __name__ == '__main__':
    try:
        analysis = analyze_all_bundles()

        if 'error' in analysis:
            print(f"Error: {analysis['error']}")
            sys.exit(1)

        print_analysis(analysis)
        find_fodder_and_enchanters()

        # Save to JSON for further analysis
        output_file = Path(__file__).parent / 'bundle_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n\nDetailed analysis saved to: {output_file}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
