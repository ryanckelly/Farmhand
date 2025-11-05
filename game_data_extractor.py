"""
Game Data Extractor for Stardew Valley
Auto-generates item_database.py and bundle_definitions.py from game files.

Usage:
    python game_data_extractor.py

This script extracts data from Stardew Valley's Content/Data JSON files
and generates Python modules that can be imported by the companion system.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def find_game_directory():
    """Locate Stardew Valley installation directory."""
    possible_paths = [
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stardew Valley"),
        Path(r"C:\Program Files\Steam\steamapps\common\Stardew Valley"),
        Path(r"D:\SteamLibrary\steamapps\common\Stardew Valley"),
        Path(r"E:\SteamLibrary\steamapps\common\Stardew Valley"),
    ]

    for path in possible_paths:
        if path.exists():
            data_dir = path / "Content" / "Data"
            if data_dir.exists():
                return data_dir

    return None


def extract_objects(objects_file):
    """
    Parse Objects.json and extract item data.

    Format (1.6+): JSON with item IDs as keys
    Each value is a string: "Name/Price/Edibility/Type DisplayName/Description/..."
    """
    print(f"Reading {objects_file.name}...")

    with open(objects_file, 'r', encoding='utf-8') as f:
        objects = json.load(f)

    item_db = {}

    for item_id, data in objects.items():
        # Handle both old (int IDs) and new (string IDs) formats
        if isinstance(data, str):
            # Old format: slash-delimited string
            fields = data.split('/')
            if len(fields) >= 5:
                item_db[str(item_id)] = {
                    'name': fields[0],
                    'price': int(fields[1]) if fields[1].isdigit() else 0,
                    'edibility': int(fields[2]) if fields[2].lstrip('-').isdigit() else -300,
                    'category': fields[3],
                    'display_name': fields[4] if fields[4] else fields[0],
                }
        elif isinstance(data, dict):
            # New format: structured dictionary
            item_db[str(item_id)] = {
                'name': data.get('Name', f'Unknown_{item_id}'),
                'price': data.get('Price', 0),
                'edibility': data.get('Edibility', -300),
                'category': data.get('Category', ''),
                'display_name': data.get('DisplayName', data.get('Name', f'Unknown_{item_id}')),
            }

    print(f"  Extracted {len(item_db)} items")
    return item_db


def extract_bundles(bundles_file):
    """
    Parse Bundles.json and extract bundle definitions.

    Format: "Room/Index": "Name/Reward/Items/Color/RequiredCount"
    Items format: "id qty quality id qty quality ..."
    """
    print(f"Reading {bundles_file.name}...")

    with open(bundles_file, 'r', encoding='utf-8') as f:
        bundles = json.load(f)

    bundle_defs = {}

    for key, value in bundles.items():
        # Key format: "Room/Index"
        parts = key.split('/')
        if len(parts) != 2:
            continue

        room = parts[0]
        try:
            index = int(parts[1])
        except ValueError:
            continue

        # Value format: "Name/Reward/Items/Color/RequiredCount"
        value_parts = value.split('/')
        if len(value_parts) < 3:
            continue

        bundle_name = value_parts[0]
        reward = value_parts[1] if len(value_parts) > 1 and value_parts[1] else None
        items_string = value_parts[2] if len(value_parts) > 2 else ""
        color = int(value_parts[3]) if len(value_parts) > 3 and value_parts[3] else 0
        required_count = int(value_parts[4]) if len(value_parts) > 4 and value_parts[4] else None

        # Parse items
        items = parse_bundle_items(items_string)

        # If no required count specified, all items are required
        if required_count is None:
            required_count = len(items)

        bundle_defs[index] = {
            'room': room,
            'name': bundle_name,
            'reward': reward,
            'items': items,
            'color': color,
            'required': required_count
        }

    print(f"  Extracted {len(bundle_defs)} bundles")
    return bundle_defs


def parse_bundle_items(items_string):
    """
    Parse bundle items format: "id qty quality id qty quality ..."

    Returns list of dicts with id, quantity, quality
    """
    if not items_string.strip():
        return []

    tokens = items_string.split()
    items = []

    # Items come in triplets: id, quantity, quality
    for i in range(0, len(tokens), 3):
        if i + 2 < len(tokens):
            items.append({
                'id': tokens[i],
                'quantity': int(tokens[i + 1]),
                'quality': int(tokens[i + 2])
            })

    return items


def generate_item_database(item_db, output_file):
    """Generate item_database.py from extracted data."""
    print(f"\nGenerating {output_file.name}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write('"""\n')
        f.write('Item Database - AUTO-GENERATED\n')
        f.write(f'Generated: {datetime.now().isoformat()}\n')
        f.write('Source: Stardew Valley Content/Data/Objects.json\n')
        f.write('\n')
        f.write('DO NOT EDIT MANUALLY - Run game_data_extractor.py to regenerate\n')
        f.write('"""\n\n')

        # Main database
        f.write('ITEM_DATABASE = {\n')
        for item_id in sorted(item_db.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            data = item_db[item_id]
            f.write(f"    '{item_id}': {{\n")
            f.write(f"        'name': {repr(data['name'])},\n")
            f.write(f"        'price': {data['price']},\n")
            f.write(f"        'edibility': {data['edibility']},\n")
            f.write(f"        'category': {repr(data['category'])},\n")
            f.write(f"        'display_name': {repr(data['display_name'])},\n")
            f.write(f"    }},\n")
        f.write('}\n\n')

        # Helper functions
        f.write('def get_item_name(item_id):\n')
        f.write('    """Get item name by ID, with fallback for unknown items."""\n')
        f.write('    item_id_str = str(item_id)\n')
        f.write('    item = ITEM_DATABASE.get(item_id_str)\n')
        f.write('    if item:\n')
        f.write('        return item["name"]\n')
        f.write('    return f"Unknown Item ({item_id})"\n\n')

        f.write('def get_item_info(item_id):\n')
        f.write('    """Get complete item info by ID."""\n')
        f.write('    item_id_str = str(item_id)\n')
        f.write('    return ITEM_DATABASE.get(item_id_str, {\n')
        f.write('        "name": f"Unknown Item ({item_id})",\n')
        f.write('        "price": 0,\n')
        f.write('        "edibility": -300,\n')
        f.write('        "category": "unknown",\n')
        f.write('        "display_name": f"Unknown Item ({item_id})"\n')
        f.write('    })\n')

    print(f"  ✓ Generated with {len(item_db)} items")


def generate_bundle_definitions(bundle_defs, output_file):
    """Generate bundle_definitions.py from extracted data."""
    print(f"\nGenerating {output_file.name}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write('"""\n')
        f.write('Bundle Definitions - AUTO-GENERATED\n')
        f.write(f'Generated: {datetime.now().isoformat()}\n')
        f.write('Source: Stardew Valley Content/Data/Bundles.json\n')
        f.write('\n')
        f.write('DO NOT EDIT MANUALLY - Run game_data_extractor.py to regenerate\n')
        f.write('"""\n\n')

        # Main database
        f.write('BUNDLE_DEFINITIONS = {\n')
        for bundle_id in sorted(bundle_defs.keys()):
            data = bundle_defs[bundle_id]
            f.write(f"    {bundle_id}: {{\n")
            f.write(f"        'room': {repr(data['room'])},\n")
            f.write(f"        'name': {repr(data['name'])},\n")
            f.write(f"        'reward': {repr(data['reward'])},\n")
            f.write(f"        'items': [\n")
            for item in data['items']:
                f.write(f"            {repr(item)},\n")
            f.write(f"        ],\n")
            f.write(f"        'color': {data['color']},\n")
            f.write(f"        'required': {data['required']},\n")
            f.write(f"    }},\n")
        f.write('}\n\n')

        # Helper functions
        f.write('def get_bundle_info(bundle_id):\n')
        f.write('    """Get bundle definition by ID."""\n')
        f.write('    return BUNDLE_DEFINITIONS.get(bundle_id)\n\n')

        f.write('def get_bundles_by_room(room_name):\n')
        f.write('    """Get all bundles for a specific room."""\n')
        f.write('    return {\n')
        f.write('        bid: bdata for bid, bdata in BUNDLE_DEFINITIONS.items()\n')
        f.write('        if bdata["room"] == room_name\n')
        f.write('    }\n')

    print(f"  ✓ Generated with {len(bundle_defs)} bundles")


def main():
    """Main extraction workflow."""
    print("=" * 60)
    print("Stardew Valley Game Data Extractor")
    print("=" * 60)
    print()

    # Find game directory
    game_data_dir = find_game_directory()
    if not game_data_dir:
        print("ERROR: Could not find Stardew Valley installation")
        print("\nPlease ensure the game is installed via Steam, or update")
        print("the paths in find_game_directory() function.")
        sys.exit(1)

    print(f"Found game data: {game_data_dir}")
    print()

    # Check for required files
    objects_file = game_data_dir / "Objects.json"
    bundles_file = game_data_dir / "Bundles.json"

    if not objects_file.exists():
        print(f"ERROR: Objects.json not found at {objects_file}")
        sys.exit(1)

    if not bundles_file.exists():
        print(f"ERROR: Bundles.json not found at {bundles_file}")
        sys.exit(1)

    # Extract data
    print("Extracting game data...")
    print()

    item_db = extract_objects(objects_file)
    bundle_defs = extract_bundles(bundles_file)

    # Generate Python files
    output_dir = Path(__file__).parent

    item_db_file = output_dir / "item_database_generated.py"
    bundle_defs_file = output_dir / "bundle_definitions_generated.py"

    generate_item_database(item_db, item_db_file)
    generate_bundle_definitions(bundle_defs, bundle_defs_file)

    # Summary
    print()
    print("=" * 60)
    print("Extraction Complete!")
    print("=" * 60)
    print()
    print(f"Generated files:")
    print(f"  • {item_db_file.name} ({len(item_db)} items)")
    print(f"  • {bundle_defs_file.name} ({len(bundle_defs)} bundles)")
    print()
    print("Next steps:")
    print("  1. Review the generated files")
    print("  2. Backup your current item_database.py and bundle_definitions.py")
    print("  3. Replace them with the generated versions (remove '_generated')")
    print("  4. Test with: python save_analyzer.py")
    print()


if __name__ == '__main__':
    main()
