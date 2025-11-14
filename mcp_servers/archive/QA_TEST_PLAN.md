# Phase 3.6: Comprehensive Parser QA Testing

## Overview
Adversarial testing of all 12 parsers to identify weaknesses before Phase 4 production deployment.

## Test Strategy

### Test Categories
1. **Edge Cases** - Unusual but valid wiki formatting
2. **Malformed Data** - Missing sections, incomplete tables
3. **Special Characters** - Unicode, apostrophes, special formatting
4. **Boundary Conditions** - Min/max values, empty fields
5. **Version-Specific Content** - Game version differences

### Evaluation Criteria
- ✅ **Data completeness**: All expected fields extracted?
- ✅ **Data accuracy**: Values correct?
- ✅ **Error handling**: Graceful degradation on missing data?
- ✅ **Edge case handling**: Unusual formats parsed correctly?
- ✅ **Performance**: Completes in reasonable time?

## Parser Test Cases

### 1. Crops Parser (parse_crop_data)
**Test Pages:**
- [ ] Coffee - Multi-season crop
- [ ] Corn - Multi-season with regrowth
- [ ] Rice - Paddy crop (special location requirement)
- [ ] Wheat - Simple one-season crop
- [ ] Ancient Fruit - Continuous regrowth
- [ ] Sweet Gem Berry - Rare crop with special properties

**Expected Fields:**
- seasons (list)
- growth_time (int)
- regrowth_time (int or null)
- sell_prices (dict with quality tiers)

**Edge Cases:**
- Crops with no regrowth
- Crops available in multiple seasons
- Giant crop variants (pumpkin, cauliflower, melon)
- Trellis vs. normal crops

### 2. Fish Parser (parse_fish_data)
**Test Pages:**
- [ ] Legend - Legendary fish (unique catch conditions)
- [ ] Catfish - Complex time windows
- [ ] Sandfish - Desert location
- [ ] Lobster - Crab pot catch
- [ ] Glacierfish - Legendary with specific location
- [ ] Midnight Carp - Specific time window

**Expected Fields:**
- location (str)
- time (str)
- seasons (list)
- weather (str)
- difficulty (int)

**Edge Cases:**
- Legendary fish (one-time catch)
- Crab pot catches vs. rod catches
- Fish requiring specific weather + season
- Fish with fishing level requirements

### 3. Bundle Parser (parse_bundle_data)
**Test Pages:**
- [ ] Spring Crops Bundle - Standard bundle
- [ ] Quality Crops Bundle - Remixed bundle (ID 13)
- [ ] Rare Forage Bundle - Remixed bundle (ID 14)
- [ ] Fish Tank Bundle - Choice slots
- [ ] Missing Bundle - Post-CC content (ID 36)

**Expected Fields:**
- name (str)
- requirements (list of items with quantities)

**Edge Cases:**
- Remixed vs. standard bundles
- Bundles with quality requirements
- Bundles with choice slots (pick X of Y)
- Post-Community Center bundles

### 4. NPC Parser (parse_npc_data)
**Test Pages:**
- [ ] Sebastian - Marriage candidate (14-heart events)
- [ ] Pam - Non-marriageable NPC
- [ ] Jas - Child NPC (limited events)
- [ ] Krobus - Secret NPC (unique mechanics)
- [ ] Dwarf - NPC with language barrier
- [ ] Wizard - NPC with complex family

**Expected Fields:**
- loved_gifts (list)
- marriageable (bool)
- address (str)
- family (list)
- heart_events (list with heart_level and title)
- birthday (str)

**Edge Cases:**
- Marriage candidates (12 NPCs)
- NPCs with no fixed address
- Gift preferences with "All Universal X" entries
- NPCs with complex family trees

### 5. Recipe Parser (parse_recipe_data)
**Test Pages:**
- [ ] Algae Soup - Simple cooking recipe
- [ ] Chest - Crafting recipe (furniture)
- [ ] Keg - Artisan equipment with products table
- [ ] Life Elixir - Recipe with many ingredients
- [ ] Triple Shot Espresso - Complex buffs
- [ ] Lucky Lunch - Multi-buff recipe

**Expected Fields:**
- recipe_type (cooking or crafting)
- ingredients (list with item and quantity)
- products (list for machines)
- buff (str)
- energy/health (int)
- unlock_source (str)

**Edge Cases:**
- Recipes with 10+ ingredients
- Recipes with no sell price
- Recipes unlocked via events
- Artisan equipment with processing times
- Recipes with buffs but no energy

### 6. Skills Parser (parse_skill_data)
**Test Pages:**
- [ ] Farming - Standard skill
- [ ] Mining - Profession tree with geologist
- [ ] Fishing - Quality fish mechanics
- [ ] Foraging - Botanist profession
- [ ] Combat - Fighter/Scout paths

**Expected Fields:**
- levels (dict with 1-10 and unlocks)
- professions (dict with level 5 and 10 choices)

**Edge Cases:**
- Level 5 profession branches
- Level 10 profession requirements
- Recipes unlocked at each level

### 7. Quests Parser (parse_quest_data)
**Test Pages:**
- [ ] Quests - Main quest page (all quest types)

**Expected Fields:**
- story_quests (list)
- special_orders (list)
- qi_special_orders (list)

**Edge Cases:**
- Story quests vs. special orders
- Qi's orders vs. special orders
- Quest time limits

### 8. Achievements Parser (parse_achievement_data)
**Test Pages:**
- [ ] Achievements - Main achievements page

**Expected Fields:**
- achievements (list with name, description, unlocks)

**Edge Cases:**
- Steam vs. console achievements
- Secret achievements

### 9. Monster Parser (parse_generic_item for monsters)
**Test Pages:**
- [ ] Skeleton - Basic monster
- [ ] Green Slime - Monster with variants
- [ ] Dust Sprite - Monster with valuable drops
- [ ] Iridium Bat - Dangerous mine variant
- [ ] Mummy - Monster with revival mechanic
- [ ] Serpent - Skull Cavern exclusive

**Expected Fields:**
- base_hp (int)
- base_damage (int)
- base_def (int)
- speed (int)
- xp (int)
- drops (str)
- spawns_in (str)

**Edge Cases:**
- Monsters with variants (slimes by color)
- Monsters with conditional stats (Dangerous mode)
- Monsters with special abilities
- Boss monsters vs. regular monsters

### 10. Animal Parser (parse_animal_data)
**Test Pages:**
- [ ] Chicken - Basic coop animal
- [ ] Cow - Basic barn animal
- [ ] Pig - Truffle-producing animal
- [ ] Sheep - Wool-producing with shearing
- [ ] Dinosaur - Special animal
- [ ] Ostrich - Deluxe barn animal

**Expected Fields:**
- building (str)
- purchase_price (int)
- produce (str)

**Edge Cases:**
- Animals requiring building upgrades
- Animals with multiple product types
- Animals with quality modifiers

### 11. Collections Parser (parse_collection_list)
**Test Pages:**
- [ ] Artifacts - 42 artifacts
- [ ] Minerals - 57 minerals

**Expected Fields:**
- items (list with name, description, sell_price, location)

**Edge Cases:**
- Multiple tables per page
- Items with no location
- Items with seasonal availability

### 12. Generic Item Parser (parse_generic_item)
**Test Pages:**
- [ ] Hardwood - Forage item
- [ ] Clay - Digging item
- [ ] Battery Pack - Crafted/found item

**Expected Fields:**
- source (str)
- sell_price (int)
- purchase_price (int)

**Edge Cases:**
- Items with no purchase price
- Items with no sell price
- Items with multiple sources

## Test Execution Plan

1. **Create test script** for each parser
2. **Run tests** and record results
3. **Document failures** with specific error messages
4. **Fix critical bugs** identified during testing
5. **Document known limitations** for non-critical issues
6. **Create test results matrix** (pass/fail grid)

## Deliverables
- [ ] Comprehensive test script (test_all_parsers.py)
- [ ] Test results matrix (CSV or markdown table)
- [ ] Bug list with fixes implemented
- [ ] Known limitations documentation
- [ ] Performance benchmarks

## Success Criteria
- ✅ 90%+ test cases pass
- ✅ All critical bugs fixed
- ✅ Known limitations documented
- ✅ Performance acceptable (<2s per page)
- ✅ Graceful degradation on missing data
