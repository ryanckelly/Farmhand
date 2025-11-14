#!/usr/bin/env python3
"""
Comprehensive QA testing for all MCP Wiki parsers.
Tests edge cases, malformed data, and boundary conditions.
"""

import json
import time
from typing import Any
from stardew_wiki_mcp import WikiClient, parse_page_data, WIKI_API_URL

# Test configuration
TEST_RESULTS = []
WIKI_CLIENT = WikiClient(WIKI_API_URL)

def test_page(page_title: str, parser_name: str, expected_fields: list[str], test_case_name: str) -> dict[str, Any]:
    """
    Test a single wiki page and validate expected fields.

    Args:
        page_title: Wiki page to fetch
        parser_name: Name of the parser being tested
        expected_fields: List of fields that should be present
        test_case_name: Description of this test case

    Returns:
        Test result dictionary
    """
    result = {
        "parser": parser_name,
        "test_case": test_case_name,
        "page": page_title,
        "status": "PASS",
        "missing_fields": [],
        "errors": [],
        "data_sample": {},
        "duration_ms": 0
    }

    try:
        start_time = time.time()

        # Fetch and parse page
        page_result = WIKI_CLIENT.get_page(page_title)
        if not page_result["success"]:
            result["status"] = "FAIL"
            result["errors"].append(f"Failed to fetch page: {page_result.get('error', 'Unknown error')}")
            return result

        parsed = parse_page_data(page_result['html'], page_title, page_result.get('categories', []))

        end_time = time.time()
        result["duration_ms"] = int((end_time - start_time) * 1000)

        # Check for expected fields
        for field in expected_fields:
            if field not in parsed:
                result["missing_fields"].append(field)
                result["status"] = "FAIL"

        # Store sample of extracted data (first 3 items/fields)
        for key, value in list(parsed.items())[:5]:
            if isinstance(value, list) and len(value) > 3:
                result["data_sample"][key] = f"{len(value)} items (showing first 3)"
                result["data_sample"][f"{key}_sample"] = value[:3]
            else:
                result["data_sample"][key] = value

    except Exception as e:
        result["status"] = "ERROR"
        result["errors"].append(f"Exception: {str(e)}")

    return result


def print_result(result: dict[str, Any]):
    """Print a test result in a readable format."""
    status_symbol = "[PASS]" if result["status"] == "PASS" else "[FAIL]" if result["status"] == "FAIL" else "[ERROR]"
    print(f"\n{status_symbol} {result['parser']}: {result['test_case']}")
    print(f"   Page: {result['page']}")
    print(f"   Duration: {result['duration_ms']}ms")

    if result["missing_fields"]:
        print(f"   Missing fields: {', '.join(result['missing_fields'])}")

    if result["errors"]:
        print(f"   Errors:")
        for error in result["errors"]:
            print(f"     - {error}")

    if result["status"] == "PASS":
        print(f"   Sample data: {list(result['data_sample'].keys())}")


def run_all_tests():
    """Execute all parser tests."""
    print("="*60)
    print("STARDEW VALLEY WIKI MCP - COMPREHENSIVE QA TESTING")
    print("="*60)

    # 1. CROPS PARSER
    print("\n\n[CROPS] Testing Crops Parser...")
    crops_tests = [
        ("Corn", ["seasons", "growth_time"], "Multi-season with regrowth"),
        ("Wheat", ["seasons", "growth_time"], "Simple one-season"),
        ("Ancient Fruit", ["growth_time", "seasons"], "Continuous regrowth"),
        ("Tomato", ["seasons", "growth_time"], "Summer crop with regrowth"),
        ("Parsnip", ["seasons", "growth_time"], "Spring starter crop"),
    ]
    for page, fields, desc in crops_tests:
        result = test_page(page, "Crops", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 2. FISH PARSER
    print("\n\n[FISH] Testing Fish Parser...")
    fish_tests = [
        ("Legend", ["location", "seasons", "time"], "Legendary fish"),
        ("Catfish", ["location", "time", "weather"], "Complex time windows"),
        ("Sandfish", ["location", "seasons"], "Desert location"),
        ("Lobster", ["location"], "Crab pot catch"),
        ("Midnight Carp", ["time", "seasons"], "Specific time window"),
    ]
    for page, fields, desc in fish_tests:
        result = test_page(page, "Fish", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 3. BUNDLE PARSER
    print("\n\n[BUNDLES] Testing Bundle Parser...")
    bundle_tests = [
        ("Spring Crops Bundle", ["requirements"], "Standard bundle"),
        ("Quality Crops Bundle", ["requirements"], "Remixed bundle"),
        ("Specialty Fish Bundle", ["requirements"], "Choice slots bundle"),
    ]
    for page, fields, desc in bundle_tests:
        result = test_page(page, "Bundles", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 4. NPC PARSER
    print("\n\n[NPCS] Testing NPC Parser...")
    npc_tests = [
        ("Sebastian", ["loved_gifts", "marriageable", "heart_events"], "Marriage candidate"),
        ("Pam", ["loved_gifts", "marriageable"], "Non-marriageable NPC"),
        ("Jas", ["loved_gifts"], "Child NPC"),
        ("Krobus", ["loved_gifts"], "Secret NPC"),
        ("Dwarf", ["loved_gifts"], "Language barrier NPC"),
    ]
    for page, fields, desc in npc_tests:
        result = test_page(page, "NPCs", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 5. RECIPE PARSER
    print("\n\n[RECIPES] Testing Recipe Parser...")
    recipe_tests = [
        ("Algae Soup", ["ingredients", "recipe_type"], "Simple cooking recipe"),
        ("Chest", ["ingredients", "recipe_type"], "Crafting recipe"),
        ("Keg", ["ingredients", "products"], "Artisan equipment"),
        ("Life Elixir", ["ingredients"], "Many ingredients"),
    ]
    for page, fields, desc in recipe_tests:
        result = test_page(page, "Recipes", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 6. SKILLS PARSER
    print("\n\n[SKILLS] Testing Skills Parser...")
    skills_tests = [
        ("Farming", ["levels", "professions"], "Standard skill"),
        ("Mining", ["levels", "professions"], "Profession tree"),
        ("Fishing", ["levels", "professions"], "Quality mechanics"),
    ]
    for page, fields, desc in skills_tests:
        result = test_page(page, "Skills", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 7. QUESTS PARSER
    print("\n\n[QUESTS] Testing Quests Parser...")
    result = test_page("Quests", "Quests", ["story_quests", "special_orders"], "All quest types")
    print_result(result)
    TEST_RESULTS.append(result)

    # 8. ACHIEVEMENTS PARSER
    print("\n\n[ACHIEVEMENTS] Testing Achievements Parser...")
    result = test_page("Achievements", "Achievements", ["achievements"], "All achievements")
    print_result(result)
    TEST_RESULTS.append(result)

    # 9. MONSTER PARSER
    print("\n\n[MONSTERS] Testing Monster Parser...")
    monster_tests = [
        ("Skeleton", ["base_hp", "base_damage", "xp"], "Basic monster"),
        ("Rock Crab", ["base_hp", "base_damage"], "Basic combat monster"),
        ("Dust Sprite", ["drops"], "Valuable drops monster"),
    ]
    for page, fields, desc in monster_tests:
        result = test_page(page, "Monsters", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 10. ANIMAL PARSER
    print("\n\n[ANIMALS] Testing Animal Parser...")
    animal_tests = [
        ("Chicken", ["building", "purchase_price"], "Basic coop animal"),
        ("Cow", ["building", "purchase_price", "produce"], "Basic barn animal"),
        ("Pig", ["produce"], "Truffle producer"),
    ]
    for page, fields, desc in animal_tests:
        result = test_page(page, "Animals", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 11. COLLECTIONS PARSER
    print("\n\n[COLLECTIONS] Testing Collections Parser...")
    collection_tests = [
        ("Artifacts", ["items"], "42 artifacts"),
        ("Minerals", ["items"], "57 minerals"),
    ]
    for page, fields, desc in collection_tests:
        result = test_page(page, "Collections", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # 12. GENERIC ITEM PARSER
    print("\n\n[ITEMS] Testing Generic Item Parser...")
    item_tests = [
        ("Hardwood", ["source"], "Forage item"),
        ("Clay", ["source"], "Digging item"),
        ("Battery Pack", ["source"], "Crafted/found item"),
    ]
    for page, fields, desc in item_tests:
        result = test_page(page, "Items", fields, desc)
        print_result(result)
        TEST_RESULTS.append(result)

    # SUMMARY
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    errors = sum(1 for r in TEST_RESULTS if r["status"] == "ERROR")
    total = len(TEST_RESULTS)

    print(f"\nTotal Tests: {total}")
    print(f"[PASS] Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"[FAIL] Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"[ERROR] Errors: {errors} ({errors/total*100:.1f}%)")

    avg_duration = sum(r["duration_ms"] for r in TEST_RESULTS) / total
    print(f"\n[TIME] Average duration: {avg_duration:.0f}ms")

    # Save detailed results to JSON
    with open("test_results.json", "w") as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print(f"\n[SAVE] Detailed results saved to: test_results.json")

    # Create results matrix
    print("\n" + "="*60)
    print("RESULTS MATRIX BY PARSER")
    print("="*60)

    parsers = {}
    for r in TEST_RESULTS:
        parser = r["parser"]
        if parser not in parsers:
            parsers[parser] = {"passed": 0, "failed": 0, "errors": 0}

        if r["status"] == "PASS":
            parsers[parser]["passed"] += 1
        elif r["status"] == "FAIL":
            parsers[parser]["failed"] += 1
        else:
            parsers[parser]["errors"] += 1

    print(f"\n{'Parser':<20} {'Pass':<8} {'Fail':<8} {'Error':<8} {'Total':<8}")
    print("-" * 60)
    for parser, counts in sorted(parsers.items()):
        total_parser = counts["passed"] + counts["failed"] + counts["errors"]
        print(f"{parser:<20} {counts['passed']:<8} {counts['failed']:<8} {counts['errors']:<8} {total_parser:<8}")

    return passed / total >= 0.9  # Success if 90%+ pass


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
