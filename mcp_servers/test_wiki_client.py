#!/usr/bin/env python3
"""
Test script for the Wiki Client

This script tests the WikiClient independently of the MCP protocol.
Use this to verify that:
1. The wiki API is accessible
2. Search results are returned correctly
3. Error handling works

Usage:
    python test_wiki_client.py
    python test_wiki_client.py "your search term"
"""

import sys
import json

# Import the WikiClient from our MCP server
sys.path.insert(0, '.')
from stardew_wiki_mcp import WikiClient, WIKI_API_URL


def test_search(query: str, limit: int = 5):
    """
    Test the search functionality.

    Args:
        query: What to search for
        limit: How many results to get
    """
    print(f"\n{'='*60}")
    print(f"Testing Wiki Search: '{query}'")
    print(f"{'='*60}\n")

    # Create the client
    client = WikiClient(WIKI_API_URL)

    # Perform the search
    result = client.search(query, limit)

    # Display results
    if result["success"]:
        print(f"[SUCCESS] Found {result['count']} results:\n")

        for i, item in enumerate(result["results"], 1):
            title = item.get("title", "Unknown")
            snippet = item.get("snippet", "No description")
            pageid = item.get("pageid", "N/A")

            # Clean up HTML tags in snippet
            snippet = snippet.replace("<span class=\"searchmatch\">", "")
            snippet = snippet.replace("</span>", "")

            print(f"{i}. {title}")
            print(f"   Page ID: {pageid}")
            print(f"   Snippet: {snippet[:150]}...")
            print(f"   URL: https://stardewvalleywiki.com/{title.replace(' ', '_')}")
            print()
    else:
        print(f"[FAILED] Search failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")

    # Show raw result (for debugging)
    print(f"\n{'='*60}")
    print("Raw Result (JSON):")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))


def main():
    """
    Main test function.
    """
    # Get search term from command line, or use defaults
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]
    else:
        # Run some default tests
        queries = [
            "apple",
            "sebastian",
            "community center",
            "nonexistent_page_12345",  # Test error handling
        ]

    print("\n" + "="*60)
    print("Stardew Valley Wiki Client Test")
    print("="*60)

    for query in queries:
        test_search(query, limit=3)
        print("\n")

    print("\n[DONE] All tests completed!")
    print("\nIf you see search results above, the wiki client is working correctly.")


if __name__ == "__main__":
    main()
