"""
XML Inspector - Deep dive into bundle XML structure

This tool examines the complete XML structure of bundles to find
fields beyond ArrayOfBoolean that might track actual completion.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

SAVE_PATH = r'C:\Users\ryanc\AppData\Roaming\StardewValley\Saves\ryfarm_419564418\ryfarm_419564418'

def inspect_bundle_xml_structure(bundle_id):
    """Get the complete XML structure for a specific bundle."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    bundles = cc.findall('.//bundles/item')

    for bundle in bundles:
        bid = int(bundle.find('.//key/int').text)
        if bid == bundle_id:
            return bundle

    return None


def print_xml_tree(element, indent=0):
    """Recursively print XML tree structure."""
    tag = element.tag
    text = element.text.strip() if element.text and element.text.strip() else None
    attrs = element.attrib

    # Print current element
    prefix = "  " * indent
    if attrs:
        print(f"{prefix}<{tag} {attrs}>")
    else:
        print(f"{prefix}<{tag}>")

    if text and len(element) == 0:  # Leaf node with text
        print(f"{prefix}  {text}")

    # Print children
    for child in element:
        print_xml_tree(child, indent + 1)

    print(f"{prefix}</{tag}>")


def analyze_community_center_structure():
    """Analyze the entire Community Center location structure."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    print("="*80)
    print("COMMUNITY CENTER XML STRUCTURE")
    print("="*80)

    # Find all direct children of CC
    print("\nDirect children of CommunityCenter:")
    for child in cc:
        if child.tag == 'bundles':
            bundle_count = len(child.findall('.//item'))
            print(f"  - {child.tag}: {bundle_count} items")
        elif len(child) > 0:
            print(f"  - {child.tag}: {len(child)} children")
        else:
            text = child.text[:50] if child.text else '(empty)'
            print(f"  - {child.tag}: {text}")

    # Check for bundle rewards
    print("\nLooking for bundleRewards:")
    bundle_rewards = cc.find('.//bundleRewards')
    if bundle_rewards is not None:
        reward_items = bundle_rewards.findall('.//item')
        print(f"  Found bundleRewards with {len(reward_items)} items")

        # Show a few examples
        for item in reward_items[:5]:
            key = item.find('.//key/int')
            value = item.find('.//value/boolean')
            if key is not None and value is not None:
                print(f"    Bundle {key.text}: reward claimed = {value.text}")
    else:
        print("  bundleRewards not found")

    # Check for area completion
    print("\nLooking for area completion tracking:")
    for area_name in ['areasComplete', 'bundlesComplete', 'completionRewards']:
        element = cc.find(f'.//{area_name}')
        if element is not None:
            print(f"  Found {area_name}:")
            # Print first few children
            for i, child in enumerate(element[:3]):
                print(f"    {child.tag}: {child.text if child.text else '...'}")
        else:
            print(f"  {area_name}: not found")


def compare_complete_vs_incomplete_bundles():
    """Compare XML structure of complete vs incomplete bundles."""
    tree = ET.parse(SAVE_PATH)
    root = tree.getroot()

    cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                  {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

    bundles = cc.findall('.//bundles/item')

    print("\n" + "="*80)
    print("COMPARISON: Complete vs Incomplete Bundles")
    print("="*80)

    # Get one complete bundle (Spring Crops, ID 0)
    complete_bundle = None
    for bundle in bundles:
        if int(bundle.find('.//key/int').text) == 0:
            complete_bundle = bundle
            break

    # Get Fodder bundle (incomplete according to user, ID 31)
    fodder_bundle = None
    for bundle in bundles:
        if int(bundle.find('.//key/int').text) == 31:
            fodder_bundle = bundle
            break

    # Get Enchanter's bundle (incomplete, ID 25)
    enchanter_bundle = None
    for bundle in bundles:
        if int(bundle.find('.//key/int').text) == 25:
            enchanter_bundle = bundle
            break

    if complete_bundle:
        print("\nSpring Crops Bundle (ID 0 - COMPLETE):")
        print("-" * 80)
        value = complete_bundle.find('.//value')
        print_element_summary(value)

    if fodder_bundle:
        print("\nFodder Bundle (ID 31 - INCOMPLETE per user):")
        print("-" * 80)
        value = fodder_bundle.find('.//value')
        print_element_summary(value)

    if enchanter_bundle:
        print("\nEnchanter's Bundle (ID 25 - INCOMPLETE):")
        print("-" * 80)
        value = enchanter_bundle.find('.//value')
        print_element_summary(value)


def print_element_summary(element, max_depth=2, current_depth=0):
    """Print a summary of an XML element's structure."""
    indent = "  " * current_depth

    for child in element:
        if child.tag == 'ArrayOfBoolean':
            bool_count = len(child.findall('.//boolean'))
            true_count = sum(1 for b in child.findall('.//boolean') if b.text == 'true')
            print(f"{indent}{child.tag}: {true_count}/{bool_count} true")
        elif len(child) > 0 and current_depth < max_depth:
            print(f"{indent}{child.tag}:")
            print_element_summary(child, max_depth, current_depth + 1)
        else:
            text = child.text[:30] if child.text else '(empty)'
            print(f"{indent}{child.tag}: {text}")


if __name__ == '__main__':
    analyze_community_center_structure()
    compare_complete_vs_incomplete_bundles()

    print("\n" + "="*80)
    print("RAW XML FOR FODDER BUNDLE")
    print("="*80)
    fodder = inspect_bundle_xml_structure(31)
    if fodder:
        print_xml_tree(fodder)
