import xml.etree.ElementTree as ET
import json
from datetime import datetime
from pathlib import Path
from bundle_definitions import get_bundle_info, get_missing_items_for_bundle

SAVE_PATH = r'C:\Users\ryanc\AppData\Roaming\StardewValley\Saves\ryfarm_419564418\ryfarm_419564418'

def analyze_save():
    """
    Parse Stardew Valley save file and extract all relevant game state data.
    Returns a comprehensive dictionary of current game state.
    """
    try:
        tree = ET.parse(SAVE_PATH)
        root = tree.getroot()

        state = {
            'timestamp': datetime.now().isoformat(),
            'save_path': SAVE_PATH,
        }

        # Basic game info
        state['game_date'] = {
            'season': get_text(root, './/currentSeason', 'unknown'),
            'day': int(get_text(root, './/dayOfMonth', 0)),
            'year': int(get_text(root, './/year', 0)),
        }
        state['game_date_str'] = f"{state['game_date']['season'].title()} {state['game_date']['day']}, Year {state['game_date']['year']}"

        # Financial data
        state['money'] = int(get_text(root, './/player/money', 0))
        state['total_earned'] = int(get_text(root, './/player/totalMoneyEarned', 0))

        # Play time (in game minutes)
        state['play_time'] = int(get_text(root, './/player/millisecondsPlayed', 0))

        # Skills and levels
        exp_points = root.findall('.//player/experiencePoints/int')
        skill_names = ['Farming', 'Fishing', 'Foraging', 'Mining', 'Combat', 'Luck']
        xp_thresholds = [0, 100, 380, 770, 1300, 2150, 3300, 4800, 6900, 10000, 15000]

        state['skills'] = {}
        for i, exp in enumerate(exp_points[:6]):
            xp = int(exp.text)
            level = calculate_level(xp, xp_thresholds)
            state['skills'][skill_names[i].lower()] = {
                'level': level,
                'xp': xp
            }

        # Professions
        professions = root.findall('.//player/professions/int')
        profession_map = {
            0: 'Rancher', 1: 'Tiller', 2: 'Coopmaster', 3: 'Shepherd', 4: 'Artisan', 5: 'Agriculturist',
            6: 'Fisher', 7: 'Trapper', 8: 'Angler', 9: 'Pirate', 10: 'Mariner', 11: 'Luremaster',
            12: 'Forester', 13: 'Gatherer', 14: 'Lumberjack', 15: 'Tapper', 16: 'Botanist', 17: 'Tracker',
            18: 'Miner', 19: 'Geologist', 20: 'Blacksmith', 21: 'Prospector', 22: 'Excavator', 23: 'Gemologist',
            24: 'Fighter', 25: 'Scout', 26: 'Brute', 27: 'Defender', 28: 'Acrobat', 29: 'Desperado'
        }
        state['professions'] = [profession_map.get(int(p.text), f'Unknown ({p.text})') for p in professions]

        # Tool upgrades
        state['tools'] = get_tool_upgrades(root)

        # House upgrade level
        house_level = int(get_text(root, './/player/houseUpgradeLevel', 0))
        house_names = {0: 'Base', 1: 'First Upgrade', 2: 'Second Upgrade', 3: 'Third Upgrade (Cellar)'}
        state['house_upgrade'] = {
            'level': house_level,
            'name': house_names.get(house_level, f'Level {house_level}'),
            'has_cellar': house_level >= 3
        }

        # Major unlocks and progression flags
        # Get mail flags for more reliable unlock detection
        mail_received = [m.text for m in root.findall('.//player/mailReceived/string') if m.text]

        deepest_level = int(get_text(root, './/player/deepestMineLevel', 0))
        state['unlocks'] = {
            'skull_key': 'HasSkullKey' in mail_received or get_text(root, './/player/hasSkullKey', 'false') == 'true',
            'club_card': 'HasClubCard' in mail_received or get_text(root, './/player/hasClubCard', 'false') == 'true',
            'rusty_key': 'HasRustyKey' in mail_received or get_text(root, './/player/hasRustyKey', 'false') == 'true',
            'sewer_opened': 'OpenedSewer' in mail_received,
            'dark_talisman': 'HasDarkTalisman' in mail_received or get_text(root, './/player/hasDarkTalisman', 'false') == 'true',
            'magic_ink': 'HasMagicInk' in mail_received or get_text(root, './/player/hasMagicInk', 'false') == 'true',
            'town_key': 'HasTownKey' in mail_received or get_text(root, './/player/hasTownKey', 'false') == 'true',
            'special_charm': get_text(root, './/player/hasSpecialCharm', 'false') == 'true',
            'desert_bridge_fixed': get_text(root, './/bridgeFixed', 'false') == 'true',
            'boat_to_island_fixed': get_text(root, './/boatFixed', 'false') == 'true',
            'golden_walnuts': int(get_text(root, './/goldenWalnuts', 0)),
            'golden_walnuts_found': int(get_text(root, './/goldenWalnutsFound', 0)),
            'deepest_mine_level': deepest_level,
            'mines_completed': deepest_level >= 120,
            'skull_cavern_level': max(0, deepest_level - 120) if deepest_level > 120 else 0,
            'can_read_junimo_text': get_text(root, './/player/canReadJunimoText', 'false') == 'true'
        }

        # Animals - only count animals that are in buildings on the farm
        state['animals'] = get_animals_from_buildings(root)

        # Buildings
        buildings = root.findall('.//Building')
        state['buildings'] = {
            'total': len(buildings),
            'by_type': {}
        }
        for building in buildings:
            btype = get_text(building, './/buildingType', 'Unknown')
            state['buildings']['by_type'][btype] = state['buildings']['by_type'].get(btype, 0) + 1

        # Friendships
        friendships = root.findall('.//player/friendshipData/item')
        state['friendships'] = {}
        for friend in friendships:
            name = get_text(friend, './/key/string', None)
            points = int(get_text(friend, './/value/Friendship/Points', 0))
            if name:
                state['friendships'][name] = {
                    'points': points,
                    'hearts': points // 250
                }

        # Marriage status - detect who player is married to
        spouse = get_text(root, './/player/spouse', None)
        state['marriage'] = {
            'married': spouse is not None and spouse != '',
            'spouse': spouse if spouse else None
        }
        # Cross-check with friendships - spouse should have 10+ hearts
        if state['marriage']['married'] and spouse in state['friendships']:
            if state['friendships'][spouse]['hearts'] < 10:
                # If married but hearts < 10, something is wrong with detection
                state['marriage']['note'] = 'Married but hearts < 10 - check data'
        # Also check for high heart counts (11+ means married since dating cap is 10)
        for name, data in state['friendships'].items():
            if data['hearts'] >= 11 and not state['marriage']['married']:
                state['marriage'] = {
                    'married': True,
                    'spouse': name,
                    'note': 'Detected via 11+ hearts (dating cap is 10)'
                }
                break

        # Museum donations
        state['museum'] = get_museum_donations(root)

        # Community Center bundles - detailed tracking
        state['bundles'] = get_detailed_bundle_info(root)

        # Crops on farm
        state['crops_farm'] = get_crops_on_farm(root)

        # Greenhouse crops
        state['crops_greenhouse'] = get_greenhouse_crops(root)

        # Fruit trees (farm and greenhouse)
        state['fruit_trees_farm'] = get_fruit_trees(root, 'farm')
        state['fruit_trees_greenhouse'] = get_fruit_trees(root, 'greenhouse')

        # Summarize crops
        state['crop_summary'] = {
            'farm_total': len(state['crops_farm']),
            'greenhouse_total': len(state['crops_greenhouse']),
            'farm_by_type': {},
            'greenhouse_by_type': {}
        }

        # Count farm crops by type
        for crop in state['crops_farm']:
            crop_name = crop['name']
            state['crop_summary']['farm_by_type'][crop_name] = \
                state['crop_summary']['farm_by_type'].get(crop_name, 0) + 1

        # Count greenhouse crops by type
        for crop in state['crops_greenhouse']:
            crop_name = crop['name']
            state['crop_summary']['greenhouse_by_type'][crop_name] = \
                state['crop_summary']['greenhouse_by_type'].get(crop_name, 0) + 1

        # Machines
        state['machines'] = get_machines_and_contents(root)

        # Player inventory - NEW: for bundle cross-reference
        state['inventory'] = get_player_inventory(root)

        # Chests - ENHANCED: now returns all items with IDs for bundle cross-reference
        state['chest_contents'] = get_chest_contents(root)

        # Weather tomorrow
        state['weather_tomorrow'] = get_text(root, './/weatherForTomorrow', 'unknown')

        # Perfection tracking (100% completion metrics)
        state['perfection'] = get_perfection_data(root)

        return state

    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'status': 'failed'
        }

def calculate_level(xp, thresholds):
    """Calculate skill level from XP."""
    level = 0
    for threshold in thresholds:
        if xp >= threshold:
            level += 1
        else:
            break
    return level - 1 if level > 0 else 0

def get_text(element, path, default=''):
    """Safely get text from XML element."""
    try:
        found = element.find(path)
        return found.text if found is not None and found.text else default
    except:
        return default

def is_bundle_complete(bundle_element):
    """Check if a bundle is complete."""
    try:
        completed = bundle_element.find('.//value/ArrayOfBoolean')
        return completed is not None
    except:
        return False

def get_tool_upgrades(root):
    """Extract tool upgrade levels from player inventory."""
    tool_levels = {
        0: 'Basic',
        1: 'Copper',
        2: 'Steel',
        3: 'Gold',
        4: 'Iridium'
    }

    tools = {}
    try:
        items = root.findall('.//player/items/Item')
        for item in items:
            name_el = item.find('.//name')
            upgrade_el = item.find('.//upgradeLevel')

            if name_el is not None and upgrade_el is not None:
                tool_name = name_el.text
                # Only track actual tools
                if any(t in tool_name for t in ['Pickaxe', 'Axe', 'Hoe', 'Watering']):
                    level = int(upgrade_el.text)
                    tools[tool_name] = {
                        'level': level,
                        'tier': tool_levels.get(level, f'Level {level}')
                    }
                elif 'Rod' in tool_name:
                    # Fishing rods are distinct items, not upgrade tiers
                    tools[tool_name] = {
                        'level': None,
                        'tier': tool_name  # Use the item name itself (e.g., "Iridium Rod")
                    }
    except Exception as e:
        print(f"Error parsing tools: {e}")

    return tools

def get_animals_from_buildings(root):
    """
    Extract animals from building interiors with detailed production data.
    Animals are stored at: Building -> indoors -> animals -> item -> value -> FarmAnimal
    """
    animals_by_type = {}
    animals_by_building_list = []
    all_animals_detailed = []
    total_animals = 0
    animals_with_produce = 0

    try:
        # Find all buildings
        buildings = root.findall('.//locations/GameLocation[@xsi:type="Farm"]/buildings/Building',
                                {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

        for building in buildings:
            building_type = get_text(building, './/buildingType', 'Unknown')

            # Animals are in the indoors section
            animals_in_building = building.findall('.//indoors/animals/item/value/FarmAnimal')

            if animals_in_building:
                # Store as list of individual buildings with their counts
                animals_by_building_list.append({
                    'type': building_type,
                    'count': len(animals_in_building)
                })

            for animal in animals_in_building:
                animal_type = get_text(animal, './/type', 'Unknown')
                animal_name = get_text(animal, './/name', 'Unknown')
                age = int(get_text(animal, './/age', 0))
                happiness = int(get_text(animal, './/happiness', 0))
                friendship = int(get_text(animal, './/friendshipTowardFarmer', 0))
                current_produce = get_text(animal, './/currentProduce', '0')

                # Track if animal has produce ready
                has_produce = current_produce != '0' and current_produce != ''
                if has_produce:
                    animals_with_produce += 1

                animals_by_type[animal_type] = animals_by_type.get(animal_type, 0) + 1
                total_animals += 1

                # Store detailed info for first few animals of each type (sample)
                all_animals_detailed.append({
                    'name': animal_name,
                    'type': animal_type,
                    'age': age,
                    'happiness': happiness,
                    'friendship': friendship,
                    'has_produce_ready': has_produce,
                    'building': building_type
                })

    except Exception as e:
        print(f"Error parsing animals: {e}")

    # Calculate average stats
    avg_happiness = sum(a['happiness'] for a in all_animals_detailed) / max(len(all_animals_detailed), 1)
    avg_friendship = sum(a['friendship'] for a in all_animals_detailed) / max(len(all_animals_detailed), 1)

    return {
        'total': total_animals,
        'by_type': animals_by_type,
        'by_building': animals_by_building_list,
        'production_ready': animals_with_produce,
        'average_happiness': int(avg_happiness),
        'average_friendship': int(avg_friendship),
        'details': all_animals_detailed[:10]  # Limit to first 10 for snapshot size
    }

def get_crops_on_farm(root):
    """Extract detailed information about crops currently planted on the farm."""
    # Crop ID to name mapping (common crops)
    crop_names = {
        '24': 'Parsnip', '188': 'Green Bean', '190': 'Cauliflower', '192': 'Potato',
        '248': 'Garlic', '250': 'Kale', '256': 'Tomato', '262': 'Wheat', '264': 'Radish',
        '266': 'Red Cabbage', '268': 'Starfruit', '270': 'Corn', '272': 'Eggplant',
        '274': 'Artichoke', '276': 'Pumpkin', '278': 'Bok Choy', '280': 'Yam',
        '282': 'Cranberries', '284': 'Beet', '300': 'Amaranth', '304': 'Hops',
        '376': 'Poppy', '398': 'Grape', '400': 'Strawberry', '433': 'Coffee Bean',
        '454': 'Ancient Fruit', '455': 'Ancient Fruit', '487': 'Melon', '488': 'Tomato',
        '490': 'Hot Pepper', '491': 'Wheat', '492': 'Radish', '493': 'Summer Spangle',
        '494': 'Corn', '495': 'Sunflower', '496': 'Fairy Rose', '499': 'Ancient Fruit',
        '595': 'Fairy Rose', '802': 'Cactus Fruit', '889': 'Qi Fruit'
    }

    crops = []
    try:
        farm = root.find('.//locations/GameLocation[@xsi:type="Farm"]',
                        {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        if farm is not None:
            # Use simpler XPath - crops are directly findable
            all_crops = farm.findall('.//crop')
            for crop in all_crops:
                harvest_index = get_text(crop, './/indexOfHarvest', 'unknown')
                crop_name = crop_names.get(harvest_index, f'Unknown ({harvest_index})')
                phase = int(get_text(crop, './/currentPhase', 0))
                days_in_phase = int(get_text(crop, './/dayOfCurrentPhase', 0))
                fully_grown = get_text(crop, './/fullyGrown', 'false') == 'true'

                crops.append({
                    'name': crop_name,
                    'index': harvest_index,
                    'phase': phase,
                    'days_in_phase': days_in_phase,
                    'fully_grown': fully_grown
                })
    except Exception as e:
        print(f"Error parsing farm crops: {e}")
    return crops

def get_greenhouse_crops(root):
    """Extract crops from greenhouse."""
    crop_names = {
        '24': 'Parsnip', '188': 'Green Bean', '190': 'Cauliflower', '192': 'Potato',
        '248': 'Garlic', '250': 'Kale', '256': 'Tomato', '262': 'Wheat', '264': 'Radish',
        '266': 'Red Cabbage', '268': 'Starfruit', '270': 'Corn', '272': 'Eggplant',
        '274': 'Artichoke', '276': 'Pumpkin', '278': 'Bok Choy', '280': 'Yam',
        '282': 'Cranberries', '284': 'Beet', '300': 'Amaranth', '304': 'Hops',
        '376': 'Poppy', '398': 'Grape', '400': 'Strawberry', '433': 'Coffee Bean',
        '454': 'Ancient Fruit', '455': 'Ancient Fruit', '487': 'Melon', '488': 'Tomato',
        '490': 'Hot Pepper', '499': 'Ancient Fruit', '595': 'Fairy Rose', '802': 'Cactus Fruit', '889': 'Qi Fruit'
    }

    crops = []
    try:
        # Greenhouse is stored by name, not xsi:type
        greenhouse = root.find('.//locations/GameLocation[name="Greenhouse"]')
        if greenhouse is not None:
            # Use simpler XPath - crops are directly findable
            all_crops = greenhouse.findall('.//crop')
            for crop in all_crops:
                harvest_index = get_text(crop, './/indexOfHarvest', 'unknown')
                crop_name = crop_names.get(harvest_index, f'Unknown ({harvest_index})')
                phase = int(get_text(crop, './/currentPhase', 0))
                fully_grown = get_text(crop, './/fullyGrown', 'false') == 'true'

                crops.append({
                    'name': crop_name,
                    'index': harvest_index,
                    'phase': phase,
                    'fully_grown': fully_grown
                })
    except Exception as e:
        print(f"Error parsing greenhouse crops: {e}")
    return crops

def get_fruit_trees(root, location='farm'):
    """Extract fruit trees from farm or greenhouse."""
    # Old format (pre-1.6): treeType field with IDs 1-8
    fruit_tree_types_old = {
        '1': 'Cherry', '2': 'Apricot', '3': 'Orange', '4': 'Peach',
        '5': 'Pomegranate', '6': 'Apple', '7': 'Banana', '8': 'Mango'
    }

    # New format (1.6+): treeId field with object IDs
    fruit_tree_types_new = {
        '628': 'Cherry', '629': 'Apricot', '630': 'Orange', '631': 'Peach',
        '632': 'Pomegranate', '633': 'Apple', '69': 'Banana', '835': 'Mango'
    }

    trees = []
    try:
        if location == 'farm':
            loc = root.find('.//locations/GameLocation[@xsi:type="Farm"]',
                           {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        elif location == 'greenhouse':
            loc = root.find('.//locations/GameLocation[name="Greenhouse"]')
        else:
            return trees

        if loc is not None:
            # Fruit trees are in terrainFeatures with xsi:type="FruitTree"
            fruit_trees = loc.findall('.//terrainFeatures/item/value/TerrainFeature[@xsi:type="FruitTree"]',
                                      {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

            for tree in fruit_trees:
                # Try new format first (treeId), then old format (treeType)
                tree_id = get_text(tree, './/treeId', None)
                if tree_id:
                    # New 1.6+ format
                    tree_type = fruit_tree_types_new.get(tree_id, f'Unknown Tree ({tree_id})')
                else:
                    # Old format
                    tree_id = get_text(tree, './/treeType', 'unknown')
                    tree_type = fruit_tree_types_old.get(tree_id, f'Unknown Tree ({tree_id})')

                days_until_mature = int(get_text(tree, './/daysUntilMature', 0))
                fruit_season = get_text(tree, './/fruitSeason', 'all')  # Greenhouse is 'all'
                has_fruit_elem = tree.find('.//fruitsOnTree')
                # Check if element exists and is not None
                has_fruit = has_fruit_elem is not None and has_fruit_elem.text not in ['0', '', None]

                trees.append({
                    'type': tree_type,
                    'type_id': tree_id,
                    'days_until_mature': days_until_mature,
                    'is_mature': days_until_mature <= 0,
                    'fruit_season': fruit_season,
                    'has_fruit': has_fruit
                })
    except Exception as e:
        print(f"Error parsing {location} fruit trees: {e}")

    return trees

def get_machines_and_contents(root):
    """Extract all machines and what they're currently processing."""
    machines = {
        'farm': [],
        'greenhouse': [],
        'shed': []
    }

    machine_names = {
        '12': 'Keg', '13': 'Furnace', '15': 'Preserve Jar', '16': 'Cheese Press',
        '17': 'Loom', '19': 'Oil Maker', '24': 'Recycling Machine', '25': 'Crystalarium',
        '90': 'Bone Mill', '101': 'Incubator', '114': 'Charcoal Kiln', '128': 'Mushroom Box',
        '154': 'Worm Bin', '156': 'Slime Incubator', '158': 'Slime Egg-Press',
        '163': 'Cask', '165': 'Auto-Grabber', '182': 'Geode Crusher', '211': 'Wood Chipper',
        '231': 'Solar Panel', '246': 'Coffee Maker', '254': 'Ostrich Incubator',
        '265': 'Heavy Tapper', '272': 'Fish Smoker', '275': 'Dehydrator', '280': 'Hay Hopper',
        # Additional machine types
        '10': 'Bee House', '105': 'Tapper', '9': 'Lightning Rod', '8': 'Scarecrow',
        '283': 'Mushroom Log'
    }

    locations = {
        'farm': './/locations/GameLocation[@xsi:type="Farm"]',
        'greenhouse': './/locations/GameLocation[@xsi:type="Greenhouse"]',
        'shed': './/locations/GameLocation[@xsi:type="Shed"]'
    }

    for loc_name, loc_path in locations.items():
        try:
            location = root.find(loc_path, {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
            if location is not None:
                objects = location.findall('.//objects/item/value/Object')
                for obj in objects:
                    parent_index = get_text(obj, './/parentSheetIndex', '')
                    machine_name = machine_names.get(parent_index, None)

                    if machine_name:
                        held_object = obj.find('.//heldObject/Object')
                        minutes_remaining = int(get_text(obj, './/minutesUntilReady', 0))

                        machine_info = {
                            'type': machine_name,
                            'processing': held_object is not None,
                            'minutes_remaining': minutes_remaining,
                            'contents': get_text(held_object, './/name', 'Empty') if held_object is not None else 'Empty'
                        }
                        machines[loc_name].append(machine_info)
        except Exception as e:
            print(f"Error parsing machines in {loc_name}: {e}")

    # Count totals by type
    machine_counts = {}
    for location in machines.values():
        for machine in location:
            mtype = machine['type']
            machine_counts[mtype] = machine_counts.get(mtype, 0) + 1

    return {
        'by_location': machines,
        'totals': machine_counts
    }

def get_player_inventory(root):
    """Extract all items in player's inventory."""
    inventory_items = []

    try:
        # Find all items in player inventory
        items = root.findall('.//player/items/Item')

        for idx, item in enumerate(items):
            # Skip empty slots
            if item.get('{http://www.w3.org/2001/XMLSchema-instance}nil') == 'true':
                continue

            # Get item ID (try both old and new formats)
            item_id = get_text(item, './/parentSheetIndex')
            if not item_id:
                item_id = get_text(item, './/itemId')  # 1.6+ format

            name = get_text(item, './/name', 'Unknown')
            stack = int(get_text(item, './/stack', 1))
            quality = int(get_text(item, './/quality', 0))

            inventory_items.append({
                'slot': idx,
                'id': item_id,
                'name': name,
                'quantity': stack,
                'quality': quality,
                'location': 'inventory'
            })

    except Exception as e:
        print(f"Error parsing inventory: {e}")

    return inventory_items


def get_chest_contents(root):
    """Extract ALL items from ALL chests with full details for bundle cross-reference."""
    all_chests_data = []
    chest_num = 1

    try:
        # Find all locations
        locations = root.findall('.//locations/GameLocation')

        for location in locations:
            location_name = get_text(location, './/name', 'Unknown')
            location_type = location.get('{http://www.w3.org/2001/XMLSchema-instance}type', 'Unknown')

            # Find chests in this location
            chests = location.findall('.//objects/item/value/Object[@xsi:type="Chest"]',
                                     {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

            for chest in chests:
                chest_items = []
                items_in_chest = chest.findall('.//items/Item')

                for item in items_in_chest:
                    # Skip empty slots
                    if item.get('{http://www.w3.org/2001/XMLSchema-instance}nil') == 'true':
                        continue

                    # Get item ID (try both old and new formats)
                    item_id = get_text(item, './/parentSheetIndex')
                    if not item_id:
                        item_id = get_text(item, './/itemId')  # 1.6+ format

                    name = get_text(item, './/name', 'Unknown')
                    stack = int(get_text(item, './/stack', 1))
                    quality = int(get_text(item, './/quality', 0))

                    chest_items.append({
                        'id': item_id,
                        'name': name,
                        'quantity': stack,
                        'quality': quality
                    })

                if chest_items:  # Only add chest if it has items
                    all_chests_data.append({
                        'chest_number': chest_num,
                        'location': location_name,
                        'location_type': location_type,
                        'items': chest_items,
                        'item_count': len(chest_items)
                    })
                    chest_num += 1

    except Exception as e:
        print(f"Error parsing chests: {e}")
        import traceback
        traceback.print_exc()

    return all_chests_data

def count_filled_items_in_bundle(slots_filled, item_count):
    """
    Count how many unique items are filled in a bundle.

    Bundle slot structure (discovered through empirical analysis):
    - ALL bundles allocate exactly 3 slots per item (consistent across all bundles)
    - The FIRST N slots map 1:1 to the N items (slot 0 = item 0, slot 1 = item 1, etc.)
    - The REMAINING slots are padding/unused (for quality variations that may not apply)
    - When a bundle is completed in-game, the game marks ALL slots as True

    Examples:
    - Fodder Bundle (3 items, 9 slots): [True, True, False, F×6] = Wheat✓ Hay✓ Apple✗
    - Vault Bundle (1 item, 3 slots): [True, False, False] = Gold✓
    - Completed bundles: [True × all slots] = completion marker

    Args:
        slots_filled: List of booleans indicating which slots are filled
        item_count: Number of items in the bundle definition

    Returns:
        Number of unique items that have at least one slot filled
    """
    if not slots_filled or item_count == 0:
        return 0

    # Use 1:1 mapping: first N slots correspond to N items
    # Only check the first item_count slots, ignore the rest (padding)
    relevant_slots = slots_filled[:item_count]
    return sum(1 for slot in relevant_slots if slot)


def get_room_completion_state(root):
    """
    Extract Community Center room completion flags for validation.

    Returns:
        dict: Completed room numbers and bundle reward mail flags
    """
    state = {
        'completed_rooms': [],
        'bundle_reward_flags': []
    }

    try:
        # Check areasComplete for room completion
        cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                      {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        if cc is not None:
            areas_complete = cc.find('.//areasComplete')
            if areas_complete is not None:
                completed_areas = areas_complete.findall('.//int')
                state['completed_rooms'] = [int(area.text) for area in completed_areas if area.text]

        # Check mail for bundle reward flags (ccPantry, ccFishTank, etc.)
        mail_received = root.findall('.//player/mailReceived/string')
        bundle_flags = [m.text for m in mail_received
                       if m.text and ('cc' in m.text.lower() or 'jojaComplete' in m.text.lower())]
        state['bundle_reward_flags'] = bundle_flags

    except Exception as e:
        print(f"Warning: Could not extract room completion state: {e}")

    return state


def get_museum_donations(root):
    """
    Extract museum donation information including total items and Dwarf Scroll status.

    Returns:
        dict: Museum donation data including total count and dwarf translation unlock status
    """
    museum_data = {
        'total_donated': 0,
        'dwarf_scrolls': {
            'scroll_i': False,
            'scroll_ii': False,
            'scroll_iii': False,
            'scroll_iv': False,
            'all_scrolls_found': False,
            'can_trade_with_dwarf': False
        }
    }

    try:
        # Find the museum location (ArchaeologyHouse)
        archaeology = root.find('.//locations/GameLocation[name="ArchaeologyHouse"]')

        if archaeology is not None:
            # Museum pieces are stored in key-value pairs
            # The key is the tile location, the value is the item ID
            museum_pieces = archaeology.find('.//museumPieces')

            if museum_pieces is not None:
                # Get all donated item IDs
                item_ids = []

                # Try different XML structures (varies by game version)
                # Structure 1: item/value/int
                items = museum_pieces.findall('.//item/value/int')
                if items:
                    item_ids = [item.text for item in items if item.text]
                else:
                    # Structure 2: item/value/string (sometimes items stored as strings)
                    items = museum_pieces.findall('.//item/value/string')
                    if items:
                        item_ids = [item.text for item in items if item.text]

                museum_data['total_donated'] = len(item_ids)

                # Check for Dwarf Scrolls (IDs: 96, 97, 98, 99)
                dwarf_scroll_ids = {
                    '96': 'scroll_i',
                    '97': 'scroll_ii',
                    '98': 'scroll_iii',
                    '99': 'scroll_iv'
                }

                for scroll_id, scroll_key in dwarf_scroll_ids.items():
                    if scroll_id in item_ids:
                        museum_data['dwarf_scrolls'][scroll_key] = True

                # Check if all scrolls are found
                all_found = all(museum_data['dwarf_scrolls'][key] for key in ['scroll_i', 'scroll_ii', 'scroll_iii', 'scroll_iv'])
                museum_data['dwarf_scrolls']['all_scrolls_found'] = all_found
                museum_data['dwarf_scrolls']['can_trade_with_dwarf'] = all_found

        # Also check mail for dwarvish translation guide as backup
        mail_received = root.findall('.//player/mailReceived/string')
        dwarvish_mail = any('dwarvish' in m.text.lower() or 'translation' in m.text.lower()
                           for m in mail_received if m.text)

        if dwarvish_mail:
            museum_data['dwarf_scrolls']['can_trade_with_dwarf'] = True

    except Exception as e:
        print(f"Warning: Could not extract museum data: {e}")

    return museum_data


def get_detailed_bundle_info(root):
    """
    Extract detailed community center bundle information using bundle definitions.
    """
    bundle_data = {
        'complete_count': 0,
        'total_count': 0,
        'incomplete_bundles': [],
        'missing_items': [],
        'remixed_bundles_detected': False,
        'unknown_bundle_ids': []
    }

    try:
        cc = root.find('.//locations/GameLocation[@xsi:type="CommunityCenter"]',
                      {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})

        if cc is None:
            return bundle_data

        bundles = cc.findall('.//bundles/item')
        bundle_data['total_count'] = len(bundles)

        # Track bundle IDs to detect remixed bundles
        all_bundle_ids = []

        for bundle in bundles:
            # Get bundle ID
            bundle_key = bundle.find('.//key/int')
            if bundle_key is None:
                continue

            bundle_id = int(bundle_key.text)
            all_bundle_ids.append(bundle_id)

            # Get bundle definition (may be None if unknown/remixed)
            bundle_def = get_bundle_info(bundle_id)
            bundle_name = bundle_def['name'] if bundle_def else f'Bundle {bundle_id}'

            # Track unknown bundles
            if not bundle_def:
                bundle_data['unknown_bundle_ids'].append(bundle_id)

            # Check completion status
            completed_array = bundle.find('.//value/ArrayOfBoolean')
            if completed_array is not None:
                bool_values = completed_array.findall('.//boolean')
                slots_filled = [b.text == 'true' for b in bool_values]

                # NEW: Use item-based counting instead of slot-based counting
                if bundle_def:
                    item_count = len(bundle_def['items'])
                    required = bundle_def.get('required', item_count)
                    all_required = bundle_def.get('all_required', False)

                    # Count unique items filled (not total slots)
                    filled_items = count_filled_items_in_bundle(slots_filled, item_count)

                    # Bundle is complete if enough items are filled
                    if all_required:
                        is_complete = filled_items >= item_count
                    else:
                        is_complete = filled_items >= required
                else:
                    # Fallback for unknown bundles: use strict all-slots-filled
                    is_complete = all(slots_filled)
            else:
                slots_filled = []
                is_complete = False

            if is_complete:
                bundle_data['complete_count'] += 1
            else:
                # Get missing items using our definitions
                missing_items = get_missing_items_for_bundle(bundle_id, slots_filled)

                if missing_items:
                    bundle_info = {
                        'id': bundle_id,
                        'name': bundle_name,
                        'needed_items': []
                    }

                    for item in missing_items:
                        quality_str = ''
                        if item['quality'] == 1:
                            quality_str = 'Silver '
                        elif item['quality'] == 2:
                            quality_str = 'Gold '
                        elif item['quality'] == 4:
                            quality_str = 'Iridium '

                        full_name = f"{item['quantity']} {quality_str}{item['name']}".strip()
                        bundle_info['needed_items'].append(full_name)

                        # Categorize missing items
                        item_type = 'other'
                        item_id = item['id']

                        # Fish IDs
                        if item_id in ['128', '129', '130', '131', '132', '136', '137', '138', '139', '140',
                                      '141', '142', '143', '144', '145', '146', '147', '148', '149', '150',
                                      '151', '154', '155', '156', '158', '159', '160', '161', '162', '163',
                                      '164', '165', '698', '699', '700', '701', '706']:
                            item_type = 'fish'
                        elif item_id == '613':  # Apple
                            item_type = 'fruit'
                        elif item_id == '446':  # Rabbit's Foot
                            item_type = 'animal_product'
                        elif item_id == 'gold':
                            item_type = 'gold'

                        bundle_data['missing_items'].append({
                            'type': item_type,
                            'name': item['name'],
                            'quantity': item['quantity'],
                            'quality': quality_str.strip(),
                            'bundle': bundle_name
                        })

                    bundle_data['incomplete_bundles'].append(bundle_info)

        # Detect remixed bundles by checking for unknown IDs
        standard_bundle_ids = list(range(0, 11)) + list(range(15, 18)) + list(range(20, 26)) + [31]
        remixed_detected = any(bid not in standard_bundle_ids for bid in all_bundle_ids)
        bundle_data['remixed_bundles_detected'] = remixed_detected

        # Add dual-state validation data (room completion and mail flags)
        room_state = get_room_completion_state(root)
        bundle_data['completed_rooms'] = room_state['completed_rooms']
        bundle_data['bundle_reward_flags'] = room_state['bundle_reward_flags']

    except Exception as e:
        print(f"Error parsing bundle details: {e}")
        import traceback
        traceback.print_exc()

    return bundle_data


def get_perfection_data(root):
    """
    Extract all perfection-related metrics from save file.
    Tracks progress toward 100% game completion (Perfection Tracker).
    """
    perfection = {}

    # 1. Farm buildings (obelisks and golden clock)
    perfection['obelisks'] = get_obelisks_on_farm(root)
    perfection['golden_clock'] = get_golden_clock(root)

    # 2. Shipping achievements
    perfection['produce_shipped'] = get_produce_shipped(root)

    # 3. Fish caught
    perfection['fish_caught'] = get_fish_caught(root)

    # 4. Recipes
    perfection['recipes_cooked'] = get_recipes_cooked(root)
    perfection['recipes_crafted'] = get_recipes_crafted(root)

    # 5. Stardrops found
    perfection['stardrops_found'] = get_stardrops_found(root)

    # 6. Monster Slayer goals
    perfection['monster_goals'] = get_monster_slayer_goals(root)

    # Calculate overall perfection percentage
    perfection['total_percent'] = calculate_perfection_score(perfection)

    return perfection


def get_obelisks_on_farm(root):
    """Count obelisks built on the farm."""
    buildings = root.findall('.//Building')
    obelisk_types = ['Earth Obelisk', 'Water Obelisk', 'Desert Obelisk', 'Island Obelisk']

    obelisks_built = {}
    for obelisk_name in obelisk_types:
        obelisks_built[obelisk_name] = 0

    for building in buildings:
        building_type = get_text(building, './/buildingType', '')
        if building_type in obelisk_types:
            obelisks_built[building_type] += 1

    return {
        'count': sum(obelisks_built.values()),
        'total': 4,
        'details': obelisks_built
    }


def get_golden_clock(root):
    """Check if Golden Clock is built on the farm."""
    buildings = root.findall('.//Building')

    for building in buildings:
        building_type = get_text(building, './/buildingType', '')
        if building_type == 'Gold Clock':
            return True

    return False


def get_produce_shipped(root):
    """Count unique items shipped (for Shipping Collection achievement)."""
    # Check basicShipped dictionary
    shipped_items = root.findall('.//player/basicShipped/item')
    unique_shipped = set()

    for item in shipped_items:
        # Item IDs stored as strings in the XML
        item_id = get_text(item, './/key/string', None)
        if item_id:
            unique_shipped.add(item_id)

    return {
        'count': len(unique_shipped),
        'total': 154  # Total unique items for full shipping collection
    }


def get_fish_caught(root):
    """Count unique fish species caught."""
    # Fish are tracked in stats or a dedicated fishCaught collection
    fish_caught = root.findall('.//player/fishCaught/item')
    unique_fish = set()

    for fish in fish_caught:
        # Fish IDs stored as strings in the XML
        fish_id = get_text(fish, './/key/string', None)
        if fish_id:
            unique_fish.add(fish_id)

    return {
        'count': len(unique_fish),
        'total': 72  # Total unique fish species in game
    }


def get_recipes_cooked(root):
    """Count unique recipes actually cooked (not just known)."""
    recipes_cooked = root.findall('.//player/recipesCooked/item')
    cooked_count = 0

    for recipe in recipes_cooked:
        times_cooked = int(get_text(recipe, './/value/int', 0))
        if times_cooked > 0:
            cooked_count += 1

    return {
        'count': cooked_count,
        'total': 81  # Total cooking recipes (as of 1.6)
    }


def get_recipes_crafted(root):
    """Count unique recipes crafted at least once."""
    recipes_crafted = root.findall('.//player/craftingRecipes/item')
    crafted_count = 0

    for recipe in recipes_crafted:
        recipe_name = get_text(recipe, './/key/string', '')
        times_crafted = int(get_text(recipe, './/value/int', 0))

        # Exclude Wedding Ring (doesn't count toward perfection)
        if times_crafted > 0 and recipe_name != 'Wedding Ring':
            crafted_count += 1

    return {
        'count': crafted_count,
        'total': 149  # Total crafting recipes (excluding Wedding Ring)
    }


def get_stardrops_found(root):
    """Count stardrops found (tracks via multiple sources)."""
    stardrop_count = 0

    # Check mail flags for stardrops
    mail_received = [m.text for m in root.findall('.//player/mailReceived/string') if m.text]

    stardrop_flags = [
        'CF_Fair',        # Stardew Valley Fair (purchase with star tokens)
        'CF_Fish',        # Master Angler (catch all fish)
        'CF_Mines',       # Floor 100 mines
        'CF_Sewer',       # Krobus shop
        'CF_Spouse',      # Spouse gift
        'CF_Statue',      # Secret Woods statue
        'museumComplete'  # Museum completion reward
    ]

    for flag in stardrop_flags:
        if flag in mail_received:
            stardrop_count += 1

    return {
        'count': stardrop_count,
        'total': 7  # Total stardrops in game
    }


def get_monster_slayer_goals(root):
    """Count completed Monster Slayer goals from Adventure Guild."""
    # Monster goals tracked in stats or adventure guild completion flags
    # This is complex - need to check specific monster kill counts vs goals

    # For now, return placeholder (this requires detailed monster kill tracking)
    # TODO: Implement full monster goal tracking when needed
    return {
        'count': 0,
        'total': 12,  # Total monster slayer categories
        'note': 'Not yet implemented - requires monster kill stat parsing'
    }


def calculate_perfection_score(perfection):
    """
    Calculate overall perfection percentage based on all categories.

    Perfection weights (adds up to 100%):
    - Produce Shipped: 15%
    - Obelisks: 4%
    - Golden Clock: 10%
    - Monster Slayer: 10%
    - Great Friends: 11% (tracked elsewhere)
    - Skills Maxed: 5% (tracked elsewhere)
    - Stardrops: 10%
    - Cooking Recipes: 10%
    - Crafting Recipes: 10%
    - Fish Caught: 10%
    - Golden Walnuts: 5% (tracked elsewhere)
    """
    score = 0.0

    # Produce shipped (15%)
    if perfection['produce_shipped']['total'] > 0:
        score += (perfection['produce_shipped']['count'] / perfection['produce_shipped']['total']) * 15

    # Obelisks (4%)
    if perfection['obelisks']['total'] > 0:
        score += (perfection['obelisks']['count'] / perfection['obelisks']['total']) * 4

    # Golden Clock (10%)
    if perfection['golden_clock']:
        score += 10

    # Monster Slayer (10%)
    if perfection['monster_goals']['total'] > 0:
        score += (perfection['monster_goals']['count'] / perfection['monster_goals']['total']) * 10

    # Stardrops (10%)
    if perfection['stardrops_found']['total'] > 0:
        score += (perfection['stardrops_found']['count'] / perfection['stardrops_found']['total']) * 10

    # Cooking (10%)
    if perfection['recipes_cooked']['total'] > 0:
        score += (perfection['recipes_cooked']['count'] / perfection['recipes_cooked']['total']) * 10

    # Crafting (10%)
    if perfection['recipes_crafted']['total'] > 0:
        score += (perfection['recipes_crafted']['count'] / perfection['recipes_crafted']['total']) * 10

    # Fish (10%)
    if perfection['fish_caught']['total'] > 0:
        score += (perfection['fish_caught']['count'] / perfection['fish_caught']['total']) * 10

    # Note: Skills (5%), Friendships (11%), and Golden Walnuts (5%) tracked elsewhere
    # This returns partial score (up to 79%)

    return round(score, 1)


if __name__ == '__main__':
    # Test the analyzer
    state = analyze_save()
    print(json.dumps(state, indent=2))
