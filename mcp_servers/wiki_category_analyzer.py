"""
Wiki Category Analyzer
Discovers all Stardew Wiki categories, samples pages, and tests parser coverage.
"""

import requests
import json
from stardew_wiki_mcp import WikiClient, parse_page_data, detect_page_type, WIKI_API_URL

def get_all_categories():
    """Fetch all categories with member counts."""
    params = {
        'action': 'query',
        'list': 'allcategories',
        'acprop': 'size',
        'aclimit': 500,
        'format': 'json'
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    if 'query' in data and 'allcategories' in data['query']:
        return [(cat['*'], cat.get('size', 0)) for cat in data['query']['allcategories']]
    return []

def filter_content_categories(categories):
    """Filter out meta/image categories."""
    skip_keywords = [
        'images', 'image', 'stub', 'template', 'archived',
        'user', 'disambiguation', 'redirect', 'page', 'file',
        'animation', 'teaser'
    ]

    content_cats = []
    for name, size in categories:
        if not any(keyword in name.lower() for keyword in skip_keywords):
            content_cats.append((name, size))

    return content_cats

def categorize_by_type(categories):
    """Group categories by game content type."""
    groups = {
        'Items & Resources': [],
        'NPCs & Characters': [],
        'Locations & Buildings': [],
        'Game Mechanics': [],
        'Quests & Events': [],
        'Other': []
    }

    for name, size in categories:
        name_lower = name.lower()

        # NPCs
        if any(word in name_lower for word in ['villager', 'npc', 'character']):
            groups['NPCs & Characters'].append((name, size))
        # Locations
        elif any(word in name_lower for word in ['location', 'place', 'building', 'room']):
            groups['Locations & Buildings'].append((name, size))
        # Items
        elif any(word in name_lower for word in [
            'crop', 'fish', 'animal', 'item', 'food', 'product', 'goods',
            'ore', 'gem', 'artifact', 'mineral', 'weapon', 'tool', 'equipment',
            'seed', 'recipe', 'furniture', 'clothing'
        ]):
            groups['Items & Resources'].append((name, size))
        # Mechanics
        elif any(word in name_lower for word in [
            'skill', 'profession', 'quest', 'bundle', 'achievement'
        ]):
            groups['Game Mechanics'].append((name, size))
        # Events
        elif any(word in name_lower for word in ['festival', 'event']):
            groups['Quests & Events'].append((name, size))
        else:
            groups['Other'].append((name, size))

    # Sort each group by size
    for group in groups:
        groups[group].sort(key=lambda x: x[1], reverse=True)

    return groups

def get_category_members(category_name, limit=5):
    """Get sample pages from a category."""
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category_name}',
        'cmlimit': limit,
        'format': 'json'
    }
    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    if 'query' in data and 'categorymembers' in data['query']:
        return [member['title'] for member in data['query']['categorymembers']]
    return []

def test_parser_coverage(page_title):
    """Test if current parsers extract useful data from a page."""
    client = WikiClient(WIKI_API_URL)
    result = client.get_page(page_title)

    if not result['success']:
        return 'error', {}

    categories = result.get('categories', [])
    parsed = parse_page_data(result['html'], page_title, categories)

    # Evaluate coverage quality
    field_count = len(parsed.keys())

    if field_count >= 5:
        return 'excellent', parsed
    elif field_count >= 3:
        return 'good', parsed
    else:
        return 'minimal', parsed

def main():
    print('='*80)
    print('STARDEW VALLEY WIKI - COMPREHENSIVE CATEGORY ANALYSIS')
    print('='*80)
    print()

    # Step 1: Get all categories
    print('Step 1: Fetching all categories...')
    all_categories = get_all_categories()
    print(f'  Found {len(all_categories)} total categories')

    # Step 2: Filter content categories
    print('\nStep 2: Filtering content categories...')
    content_categories = filter_content_categories(all_categories)
    print(f'  {len(content_categories)} content categories (after filtering)')

    # Step 3: Categorize by type
    print('\nStep 3: Grouping by content type...')
    groups = categorize_by_type(content_categories)

    for group_name, cats in groups.items():
        if cats:
            print(f'  {group_name}: {len(cats)} categories')

    # Step 4: Analyze each group
    print('\n' + '='*80)
    print('DETAILED ANALYSIS BY GROUP')
    print('='*80)

    for group_name, cats in groups.items():
        if not cats:
            continue

        print(f'\n### {group_name.upper()} ###')
        print(f'Total: {len(cats)} categories\n')

        # Show top categories by size
        print('Top categories by size:')
        for name, size in cats[:10]:
            print(f'  - {name}: {size} pages')

        # Sample 2-3 categories and test parser coverage
        print('\nParser Coverage Test:')
        sample_cats = cats[:min(3, len(cats))]

        for cat_name, cat_size in sample_cats:
            print(f'\n  Category: {cat_name} ({cat_size} pages)')

            # Get sample pages
            sample_pages = get_category_members(cat_name, limit=2)

            if not sample_pages:
                print('    No accessible pages found')
                continue

            for page_title in sample_pages[:1]:  # Test just first page
                print(f'    Testing: {page_title}')
                coverage, parsed_data = test_parser_coverage(page_title)
                print(f'      Coverage: {coverage.upper()}')
                print(f'      Fields: {len(parsed_data)} ({list(parsed_data.keys())[:5]})')

    # Step 5: Generate recommendations
    print('\n' + '='*80)
    print('RECOMMENDATIONS')
    print('='*80)
    print()

    print('USAGE DATA AVAILABILITY:')
    print('  [NO] Page view statistics are not publicly available')
    print('  [YES] Can use category member counts as rough proxy for importance')
    print()

    print('PRIORITIZATION STRATEGY:')
    print('  1. Category size (number of pages)')
    print('  2. Assumed player usage patterns (items > mechanics > locations)')
    print('  3. Current parser coverage quality')
    print()

    print('NEXT STEPS:')
    print('  - Review this analysis to identify high-value categories')
    print('  - Build custom parsers for Phase 2 priorities')
    print('  - Focus on categories with >20 pages and poor current coverage')

if __name__ == '__main__':
    main()
