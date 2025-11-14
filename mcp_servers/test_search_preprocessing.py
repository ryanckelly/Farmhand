#!/usr/bin/env python3
"""
Test script for search query preprocessing and smart search.
Tests natural language queries to verify improved search results.
"""

from stardew_wiki_mcp import WikiClient, WIKI_API_URL

def test_query(client: WikiClient, query: str, expected_strategy: str = None):
    """Test a query and show results."""
    print(f"\n{'='*70}")
    print(f"Query: '{query}'")
    print(f"{'='*70}")

    result = client.smart_search(query, limit=5)

    if result["success"]:
        print(f"[PASS] Success: {result['count']} results found")
        print(f"Strategy used: '{result.get('strategy_used', 'unknown')}'")

        if expected_strategy and result.get('strategy_used') != expected_strategy:
            print(f"[WARN] Expected strategy: '{expected_strategy}'")

        print(f"\nTop results:")
        for i, item in enumerate(result["results"][:3], 1):
            title = item.get("title", "Unknown")
            print(f"  {i}. {title}")
    else:
        print(f"[FAIL] Failed: {result.get('error', 'Unknown error')}")

    return result


def main():
    """Run all search preprocessing tests."""
    print("="*70)
    print("SEARCH QUERY PREPROCESSING TESTS")
    print("="*70)

    client = WikiClient(WIKI_API_URL)

    # Test 1: NPC gift preferences
    print("\n\n[TEST 1] NPC Gift Preferences")
    print("-" * 70)

    test_query(client, "what does sebastian like", "Sebastian")
    test_query(client, "sebastian's favorite gift", "Sebastian")
    test_query(client, "gift for haley", "Haley")
    test_query(client, "best gift for penny", "Penny")

    # Test 2: Birthday queries
    print("\n\n[TEST 2] Birthday Queries")
    print("-" * 70)

    test_query(client, "spring birthdays", "Calendar")
    test_query(client, "birthdays in summer", "Calendar")
    test_query(client, "fall birthday", "Calendar")

    # Test 3: Crop queries
    print("\n\n[TEST 3] Crop Queries")
    print("-" * 70)

    test_query(client, "crops in summer", "Summer Crops")
    test_query(client, "spring crops", "Spring Crops")
    test_query(client, "fall crops", "Fall Crops")
    test_query(client, "crops for winter", "Winter Seeds")

    # Test 4: Location queries
    print("\n\n[TEST 4] Location Queries")
    print("-" * 70)

    test_query(client, "where is the desert", "Calico Desert")
    test_query(client, "how to get to skull cavern", "Skull Cavern")
    test_query(client, "secret woods location", "Secret Woods")

    # Test 5: Bundle queries
    print("\n\n[TEST 5] Bundle Queries")
    print("-" * 70)

    test_query(client, "spring crops bundle", "Spring Crops Bundle")
    test_query(client, "quality crops bundle", "Quality Crops Bundle")
    test_query(client, "community center bundles", "Bundles")

    # Test 6: Festival queries
    print("\n\n[TEST 6] Festival Queries")
    print("-" * 70)

    test_query(client, "spring festival", "Egg Festival")
    test_query(client, "summer festival", "Luau")
    test_query(client, "fall festivals", "Stardew Valley Fair")
    test_query(client, "winter festivals", "Festival of Ice")

    # Test 7: Quest queries
    print("\n\n[TEST 7] Quest Queries")
    print("-" * 70)

    test_query(client, "community center quests", "Quests")
    test_query(client, "special orders", "Quests")
    test_query(client, "help wanted quests", "Quests")

    # Test 8: Complex multi-word queries
    print("\n\n[TEST 8] Complex Multi-Word Queries")
    print("-" * 70)

    test_query(client, "how to catch legendary fish")
    test_query(client, "what can i make with corn")
    test_query(client, "where to find ancient seed")

    print("\n\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
    print("\nVerify that:")
    print("1. Natural language queries return relevant results")
    print("2. Strategy preprocessing converts queries to better search terms")
    print("3. Fallback strategies work when primary strategy fails")
    print("4. Original query is used as last resort")


if __name__ == "__main__":
    main()
