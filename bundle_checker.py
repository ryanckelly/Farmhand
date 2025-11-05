"""
Bundle Readiness Checker

Cross-references player inventory and chest contents with Community Center bundle requirements
to determine which bundles are ready to complete.
"""

from bundle_definitions import BUNDLE_DEFINITIONS, get_bundle_info


def check_bundle_readiness(bundle_progress, inventory, chest_contents):
    """
    Check which bundles the player can complete based on current inventory/chests.

    Args:
        bundle_progress: Bundle completion data from save_analyzer
        inventory: List of items in player inventory
        chest_contents: List of items in all chests

    Returns:
        Dict mapping bundle IDs to readiness information
    """
    results = {}

    # Get list of completed bundle IDs
    completed_bundles = []
    for bundle_info in bundle_progress.get('incomplete_bundles', []):
        # Bundles not in incomplete list are complete
        pass

    # Get all bundle IDs
    all_bundle_ids = set(BUNDLE_DEFINITIONS.keys())

    # Check each incomplete bundle
    for bundle_id in all_bundle_ids:
        # Skip if we don't have definition
        bundle_def = get_bundle_info(bundle_id)
        if not bundle_def:
            continue

        # Check if already complete (not in incomplete list)
        is_incomplete = any(b['id'] == bundle_id for b in bundle_progress.get('incomplete_bundles', []))
        if not is_incomplete:
            continue

        bundle_check = {
            'id': bundle_id,
            'name': bundle_def['name'],
            'required_count': bundle_def['required'],
            'items': [],
            'ready': False,
            'missing_count': 0
        }

        # Check each required item
        for required_item in bundle_def['items']:
            item_check = check_item_availability(
                required_item,
                inventory,
                chest_contents
            )
            bundle_check['items'].append(item_check)

        # Count how many items are available
        available_count = sum(1 for item in bundle_check['items'] if item['available'])

        # Determine if bundle is ready to complete
        bundle_check['ready'] = available_count >= bundle_check['required_count']
        bundle_check['missing_count'] = bundle_check['required_count'] - available_count

        results[bundle_id] = bundle_check

    return results


def check_item_availability(required_item, inventory, chest_contents):
    """
    Check if a required item exists in inventory or chests with sufficient quality/quantity.

    Args:
        required_item: Dict with 'id', 'quantity', 'quality' from bundle definition
        inventory: List of player inventory items
        chest_contents: List of chest items

    Returns:
        Dict with availability info and locations
    """
    item_id = required_item['id']
    needed_qty = required_item['quantity']
    needed_quality = required_item['quality']

    # Combine inventory and chests for searching
    all_items = inventory + chest_contents

    # Find matching items (same ID, quality >= required)
    matches = [
        item for item in all_items
        if item['id'] == item_id and item['quality'] >= needed_quality
    ]

    # Calculate total available
    total_available = sum(item['quantity'] for item in matches)

    # Get locations where item is found
    locations = []
    for item in matches:
        loc_str = f"{item['location']}: {item['quantity']}"
        if item['quality'] > 0:
            quality_names = {1: 'Silver', 2: 'Gold', 4: 'Iridium'}
            loc_str += f" ({quality_names.get(item['quality'], 'Normal')})"
        locations.append(loc_str)

    return {
        'id': item_id,
        'name': required_item.get('name', f'Item {item_id}'),
        'needed': needed_qty,
        'available': total_available >= needed_qty,
        'have': total_available,
        'quality_needed': needed_quality,
        'locations': locations
    }


def get_ready_bundles_summary(bundle_readiness):
    """
    Generate a summary of bundles that are ready to complete.

    Args:
        bundle_readiness: Output from check_bundle_readiness()

    Returns:
        List of ready bundle names and details
    """
    ready_bundles = []

    for bundle_id, data in bundle_readiness.items():
        if data['ready']:
            ready_bundles.append({
                'id': bundle_id,
                'name': data['name'],
                'items_to_collect': [
                    {
                        'name': item['name'],
                        'locations': item['locations']
                    }
                    for item in data['items']
                    if item['available']
                ]
            })

    return ready_bundles


def get_bundles_by_priority(bundle_readiness):
    """
    Prioritize bundles by how close they are to completion.

    Args:
        bundle_readiness: Output from check_bundle_readiness()

    Returns:
        List of bundles sorted by priority (fewest missing items first)
    """
    bundles_with_progress = []

    for bundle_id, data in bundle_readiness.items():
        if not data['ready']:  # Only incomplete bundles
            available_count = sum(1 for item in data['items'] if item['available'])

            bundles_with_progress.append({
                'id': bundle_id,
                'name': data['name'],
                'missing_count': data['missing_count'],
                'available_count': available_count,
                'required_count': data['required_count'],
                'completion_percent': (available_count / data['required_count']) * 100
            })

    # Sort by fewest missing items (closest to completion)
    return sorted(bundles_with_progress, key=lambda x: x['missing_count'])


# Example usage for testing
if __name__ == '__main__':
    # This would normally come from save_analyzer
    test_inventory = [
        {'id': '24', 'name': 'Parsnip', 'quantity': 5, 'quality': 0, 'location': 'inventory'},
        {'id': '188', 'name': 'Green Bean', 'quantity': 3, 'quality': 0, 'location': 'inventory'},
    ]

    test_chests = [
        {'id': '190', 'name': 'Cauliflower', 'quantity': 2, 'quality': 0, 'location': 'Chest #1'},
        {'id': '192', 'name': 'Potato', 'quantity': 10, 'quality': 0, 'location': 'Chest #2'},
    ]

    test_bundle_progress = {
        'incomplete_bundles': [
            {'id': 0, 'name': 'Spring Crops Bundle'}
        ]
    }

    readiness = check_bundle_readiness(test_bundle_progress, test_inventory, test_chests)
    ready = get_ready_bundles_summary(readiness)
    priority = get_bundles_by_priority(readiness)

    print("Ready bundles:", ready)
    print("\nPriority order:", priority)
