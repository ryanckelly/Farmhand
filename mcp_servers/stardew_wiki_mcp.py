#!/usr/bin/env python3
"""
Stardew Valley Wiki MCP Server

This MCP (Model Context Protocol) server allows Claude to search and retrieve
information from the Stardew Valley Wiki using the MediaWiki API.

Architecture:
- Uses the `mcp` Python package to create a server that Claude can connect to
- Makes HTTP requests to the Stardew Valley Wiki's MediaWiki API
- Returns structured results to Claude in a format it can understand

Debug Mode:
- Set DEBUG=True to see all API calls and responses
- Helpful for understanding what's happening when things go wrong
"""

import asyncio
import json
import logging
import os
import re
import sys
from typing import Any

import requests
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# =============================================================================
# CONFIGURATION
# =============================================================================

# Enable debug logging - set to True to see detailed API calls
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# MediaWiki API endpoint for Stardew Valley Wiki
WIKI_API_URL = "https://stardewvalleywiki.com/mediawiki/api.php"

# Configure logging based on debug mode
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,  # MCP servers must use stderr for logs (stdout is for protocol)
)
logger = logging.getLogger("stardew-wiki-mcp")

# =============================================================================
# WIKI API CLIENT
# =============================================================================


class WikiClient:
    """
    Handles all communication with the Stardew Valley Wiki's MediaWiki API.

    This class is responsible for:
    1. Making HTTP requests to the wiki
    2. Handling errors and timeouts
    3. Formatting responses for Claude
    """

    def __init__(self, api_url: str):
        """
        Initialize the Wiki client.

        Args:
            api_url: The base URL for the MediaWiki API
        """
        self.api_url = api_url
        self.session = requests.Session()
        # Set a user agent to identify our bot (good practice for API usage)
        self.session.headers.update({
            "User-Agent": "StardewWikiMCP/1.0 (Claude Code Integration)"
        })
        logger.info(f"WikiClient initialized with API: {api_url}")

    def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """
        Search the wiki for pages matching the query.

        This uses MediaWiki's search API endpoint to find pages.

        Args:
            query: Search term (e.g., "apple", "sebastian")
            limit: Maximum number of results to return (1-50)

        Returns:
            A dictionary containing search results with titles and snippets

        Example API call:
            https://stardewvalleywiki.com/api.php?
                action=query
                &list=search
                &srsearch=apple
                &srlimit=10
                &format=json
        """
        # Build the API parameters
        params = {
            "action": "query",      # We're querying the wiki
            "list": "search",       # Specifically using the search list
            "srsearch": query,      # The search term
            "srlimit": limit,       # How many results to return
            "format": "json",       # Return JSON (easier to parse than XML)
        }

        if DEBUG:
            logger.debug(f"Searching wiki: query='{query}', limit={limit}")
            logger.debug(f"API params: {params}")

        try:
            # Make the HTTP request
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=10,  # 10 second timeout
            )
            response.raise_for_status()  # Raise exception for 4xx/5xx errors

            data = response.json()

            if DEBUG:
                logger.debug(f"API response: {data}")

            # Extract the search results from the response
            # MediaWiki returns: {"query": {"search": [...]}}
            search_results = data.get("query", {}).get("search", [])

            logger.info(f"Found {len(search_results)} results for '{query}'")

            return {
                "success": True,
                "query": query,
                "results": search_results,
                "count": len(search_results),
            }

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout when searching for '{query}'")
            return {
                "success": False,
                "error": "Request timed out after 10 seconds",
                "query": query,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "query": query,
            }

    def get_page(self, page_title: str) -> dict[str, Any]:
        """
        Fetch the HTML content of a wiki page.

        This uses MediaWiki's parse API to get the rendered HTML of a page.

        Args:
            page_title: The exact title of the wiki page (e.g., "Strawberry")

        Returns:
            A dictionary containing the page HTML and metadata

        Example API call:
            https://stardewvalleywiki.com/mediawiki/api.php?
                action=parse
                &page=Strawberry
                &format=json
        """
        params = {
            "action": "parse",
            "page": page_title,
            "format": "json",
            "prop": "text|categories",  # Get HTML text and categories
        }

        if DEBUG:
            logger.debug(f"Fetching page: '{page_title}'")
            logger.debug(f"API params: {params}")

        try:
            response = self.session.get(
                self.api_url,
                params=params,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()

            if DEBUG:
                logger.debug(f"API response keys: {data.keys()}")

            # Check if the page exists
            if "error" in data:
                logger.warning(f"Page not found: '{page_title}'")
                return {
                    "success": False,
                    "error": f"Page not found: {data['error'].get('info', 'Unknown error')}",
                    "page_title": page_title,
                }

            # Extract HTML and categories
            parse_data = data.get("parse", {})
            html = parse_data.get("text", {}).get("*", "")
            categories = [cat["*"] for cat in parse_data.get("categories", [])]

            logger.info(f"Successfully fetched page: '{page_title}'")

            return {
                "success": True,
                "page_title": page_title,
                "html": html,
                "categories": categories,
            }

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout when fetching '{page_title}'")
            return {
                "success": False,
                "error": "Request timed out after 10 seconds",
                "page_title": page_title,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "page_title": page_title,
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "page_title": page_title,
            }


# =============================================================================
# DATA PARSING
# =============================================================================


def parse_page_data(html: str, page_title: str, categories: list[str]) -> dict[str, Any]:
    """
    Parse structured data from a wiki page's HTML.

    This function:
    1. Detects the page type (crop, NPC, bundle, etc.) based on categories and title
    2. Extracts relevant data based on the page type
    3. Returns structured JSON

    Args:
        html: The HTML content of the page
        page_title: The title of the page
        categories: List of categories the page belongs to

    Returns:
        Dictionary with structured data based on page type
    """
    soup = BeautifulSoup(html, 'lxml')

    # Detect page type from categories and title
    page_type = detect_page_type(categories, page_title)

    logger.info(f"Detected page type for '{page_title}': {page_type}")

    # Parse based on type
    if page_type == "crop":
        return parse_crop_data(soup, page_title)
    elif page_type == "npc":
        return parse_npc_data(soup, page_title)
    elif page_type == "bundle":
        return parse_bundle_data(soup, page_title)
    elif page_type == "fish":
        return parse_fish_data(soup, page_title)
    elif page_type == "recipe":
        return parse_recipe_data(soup, page_title)
    else:
        # Generic item parsing
        return parse_generic_item(soup, page_title, page_type)


def detect_page_type(categories: list[str], page_title: str = "") -> str:
    """
    Detect the type of page based on its categories and title.

    Args:
        categories: List of category names
        page_title: The page title (used as fallback if categories are empty)

    Returns:
        Page type (crop, npc, bundle, fish, etc.)
    """
    # Convert to lowercase for easier matching
    cat_lower = [c.lower() for c in categories]
    title_lower = page_title.lower()

    # First, try category-based detection
    if any("crop" in c for c in cat_lower):
        return "crop"
    elif any("villager" in c or "npc" in c for c in cat_lower):
        return "npc"
    elif any("bundle" in c for c in cat_lower):
        return "bundle"
    elif any("fish" in c for c in cat_lower):
        return "fish"
    elif any("recipe" in c or "cooking" in c or "craftable" in c for c in cat_lower):
        return "recipe"
    elif any("artifact" in c for c in cat_lower):
        return "artifact"
    elif any("mineral" in c for c in cat_lower):
        return "mineral"

    # Fallback: Use page title if categories didn't match
    # This handles pages that aren't categorized properly
    if "bundle" in title_lower:
        return "bundle"
    elif any(name in title_lower for name in ["abigail", "alex", "caroline", "clint", "demetrius",
                                                "elliott", "emily", "evelyn", "george", "gus",
                                                "haley", "harvey", "jas", "jodi", "kent",
                                                "leah", "lewis", "linus", "marnie", "maru",
                                                "pam", "penny", "pierre", "robin", "sam",
                                                "sebastian", "shane", "vincent", "willy", "wizard"]):
        return "npc"

    return "item"


def parse_crop_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for crops.

    Looks for the infobox and extracts:
    - Season(s)
    - Growth time
    - Regrowth time
    - Sell prices
    - Seed source and price
    """
    data = {
        "type": "crop",
        "name": page_title,
    }

    # Find the infobox (usually a table with class 'infobox')
    # For crops, it's often the first table on the page without a class
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        # Try the first table on the page
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        # Extract key-value pairs from infobox rows
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                # Parse specific fields
                if "season" in key:
                    # Seasons can be multiple (e.g., "Spring, Summer")
                    data["seasons"] = [s.strip() for s in value.split(",")]
                elif "growth time" in key:
                    # Extract number from text like "8 days"
                    match = re.search(r'(\d+)', value)
                    if match:
                        data["growth_time"] = int(match.group(1))
                elif "regrowth" in key:
                    match = re.search(r'(\d+)', value)
                    if match:
                        data["regrowth_time"] = int(match.group(1))

    # Extract sell prices (usually in a dedicated table)
    price_table = soup.find("table", string=re.compile("Sell Price", re.I))
    if not price_table:
        # Try finding by nearby text
        price_header = soup.find(string=re.compile("Sell Price", re.I))
        if price_header:
            price_table = price_header.find_parent("table")

    if price_table:
        prices = {}
        for row in price_table.find_all("tr")[1:]:  # Skip header row
            cells = row.find_all("td")
            if len(cells) >= 2:
                quality = cells[0].get_text(strip=True).lower()
                price_text = cells[1].get_text(strip=True)
                # Extract number (e.g., "120g" -> 120)
                match = re.search(r'(\d+)', price_text)
                if match:
                    prices[quality] = int(match.group(1))

        if prices:
            data["sell_prices"] = prices

    return data


def parse_npc_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for NPCs/Villagers.

    Extracts:
    - Birthday
    - Marriageable status (boolean)
    - Address/residence
    - Family members
    - Gift preferences (loved, liked, neutral, disliked, hated)
    - Heart events (heart level, title, trigger conditions)
    """
    data = {
        "type": "npc",
        "name": page_title,
    }

    # Find birthday and other info in infobox
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        # Try first table on page
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if "birthday" in key:
                    data["birthday"] = value
                elif "marriage" in key:
                    # Check if this NPC is marriageable
                    data["marriageable"] = "yes" in value.lower()
                elif "address" in key or "lives in" in key:
                    data["address"] = value
                elif "family" in key:
                    data["family"] = value

    # Extract gift preferences
    # Wiki has sections like "Love", "Like", etc. as h3 headers
    # Gift items are in <p> tags between the h3 and the next h3
    for gift_type in ["loved", "liked", "neutral", "disliked", "hated"]:
        # Find h3 header (e.g., "Love", "Like")
        # Note: header text is just "Love" not "Loved Gifts"
        search_text = gift_type.rstrip("d")  # "loved" -> "love", "liked" -> "like"

        for h3 in soup.find_all("h3"):
            h3_text = h3.get_text(strip=True).lower()
            if search_text in h3_text:
                # Get all <p> tags between this h3 and the next h3
                gifts = []
                current = h3.find_next_sibling()
                next_h3 = h3.find_next("h3")

                while current and current != next_h3:
                    if current.name == "p":
                        text = current.get_text(strip=True)
                        # Filter out explanatory notes and empty paragraphs
                        # Skip if: starts with note markers, too long for item name, or contains explanatory phrases
                        is_note = (
                            text.startswith("*Note") or
                            text.startswith("Note:") or
                            len(text) > 50 or  # Item names are typically short
                            "the following are" in text.lower() or
                            "not considered" in text.lower()
                        )
                        if text and not is_note:
                            gifts.append(text)
                    current = current.find_next_sibling()

                if gifts:
                    data[f"{gift_type}_gifts"] = gifts
                break

    # Extract heart events
    heart_events = parse_heart_events(soup)
    if heart_events:
        data["heart_events"] = heart_events

    return data


def parse_heart_events(soup: BeautifulSoup) -> list[dict]:
    """
    Extract heart event information from NPC pages.

    Returns list of events with:
    - heart_level (2, 4, 6, 8, 10, 14)
    - title (event heading)
    - trigger (if available)
    """
    events = []

    # Find "Heart Events" or "Events" section
    for h2 in soup.find_all(['h2', 'span'], class_=['mw-headline']):
        h2_text = h2.get_text(strip=True).lower()
        if 'heart event' in h2_text or (h2_text == 'events' and h2.name == 'span'):
            # Find all h3 subheadings (individual events)
            # Get parent of the span (which is the h2)
            if h2.name == 'span':
                header = h2.parent
            else:
                header = h2

            # Find next h2 to know when to stop
            next_h2 = header.find_next(['h2'])

            # Find all h3 headers between this h2 and the next h2
            current = header.find_next(['h3', 'span'], class_=['mw-headline'])

            while current:
                # Stop if we've reached the next h2 section
                if next_h2:
                    # Check if current is after next_h2 in document order
                    if current.parent and next_h2.parent:
                        try:
                            if list(soup.descendants).index(current) >= list(soup.descendants).index(next_h2):
                                break
                        except:
                            break

                event_title = current.get_text(strip=True)

                # Extract heart level from title
                # Formats: "Two Hearts", "Four Hearts", "Six Hearts", etc.
                match = re.search(r'(\w+)\s+Heart', event_title, re.IGNORECASE)
                if match:
                    heart_word = match.group(1).lower()
                    heart_map = {
                        'two': 2, 'four': 4, 'six': 6, 'eight': 8,
                        'ten': 10, 'fourteen': 14
                    }
                    heart_level = heart_map.get(heart_word)

                    if heart_level:
                        event_data = {
                            "heart_level": heart_level,
                            "title": event_title
                        }

                        # Try to get trigger information from first paragraph after heading
                        if current.parent:
                            next_p = current.parent.find_next('p')
                            if next_p:
                                trigger_text = next_p.get_text(strip=True)
                                # Only include if it's short (likely a trigger description)
                                if len(trigger_text) < 200:
                                    event_data["trigger"] = trigger_text

                        events.append(event_data)

                # Find next h3
                current = current.find_next(['h3', 'span'], class_=['mw-headline'])
                if not current or current.name != 'span':
                    break
                # Make sure we're still looking at h3 headers
                if current.parent.name != 'h3':
                    break

            break  # Found the events section, stop searching

    return events


def parse_bundle_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for Community Center bundles.

    Note: Individual bundle pages are often stubs. This function checks if we're
    on a stub page and fetches from the main Bundles page if needed.

    Extracts:
    - Required items
    - Quantities
    - Reward
    """
    data = {
        "type": "bundle",
        "name": page_title,
        "requirements": []
    }

    # Check if this is a stub page (no meaningful tables)
    tables = soup.find_all("table")
    has_content = any(len(table.find_all("tr")) > 1 for table in tables)

    if not has_content and "bundle" in page_title.lower():
        # This is likely a stub - fetch from main Bundles page instead
        logger.info(f"Bundle page '{page_title}' appears to be a stub, fetching main Bundles page")

        try:
            # Fetch the main Bundles page
            client = WikiClient(WIKI_API_URL)
            bundles_result = client.get_page("Bundles")

            if bundles_result["success"]:
                bundles_soup = BeautifulSoup(bundles_result["html"], 'lxml')

                # Find the specific bundle section
                bundle_header = bundles_soup.find(string=re.compile(re.escape(page_title), re.I))
                if bundle_header:
                    # Find the parent table
                    table = bundle_header.find_parent("table")
                    if table:
                        # Extract items from this table
                        for row in table.find_all("tr"):
                            # Skip reward rows
                            row_text = row.get_text(strip=True).lower()
                            if "reward" in row_text:
                                continue

                            cells = row.find_all("td")
                            if cells:
                                # Look through all cells for item links
                                # (different bundles have different table structures)
                                for cell in cells:
                                    item_links = cell.find_all("a")
                                    for link in item_links:
                                        item_name = link.get_text(strip=True)
                                        # Filter out empty strings, the bundle name itself, and category links
                                        if (item_name and
                                            item_name != page_title and
                                            item_name not in ["Spring", "Summer", "Fall", "Winter", "Crops", "Foraging"] and
                                            not any(req["item"] == item_name for req in data["requirements"])):
                                            data["requirements"].append({
                                                "item": item_name,
                                                "quantity": 1  # Bundles usually need 1 of each
                                            })

                        logger.info(f"Extracted {len(data['requirements'])} items for '{page_title}'")
                        return data
        except Exception as e:
            logger.error(f"Error fetching main Bundles page: {e}")
            # Continue with original parsing below

    # Original parsing logic for pages with content
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

        if "item" in headers or "source" in headers:
            # This looks like a bundle requirements table
            for row in table.find_all("tr")[1:]:  # Skip header
                cells = row.find_all("td")
                if cells:
                    item_cell = cells[0]
                    item_name = item_cell.get_text(strip=True)

                    # Try to get quantity if available
                    quantity = 1
                    if len(cells) > 1:
                        qty_text = cells[1].get_text(strip=True)
                        match = re.search(r'(\d+)', qty_text)
                        if match:
                            quantity = int(match.group(1))

                    if item_name:
                        data["requirements"].append({
                            "item": item_name,
                            "quantity": quantity
                        })

    return data


def parse_fish_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for fish.

    Extracts:
    - Location
    - Season
    - Time
    - Weather
    - Sell price
    """
    data = {
        "type": "fish",
        "name": page_title,
    }

    # Find the infobox (usually a table with class 'infobox')
    # For fish, it's often the first table on the page without a class
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        # Try the first table on the page
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if "location" in key:
                    data["location"] = value
                elif "season" in key:
                    data["seasons"] = [s.strip() for s in value.split(",")]
                elif "time" in key:
                    data["time"] = value
                elif "weather" in key:
                    data["weather"] = value

    return data


def parse_recipe_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for cooking and crafting recipes.

    Extracts:
    - Recipe type (cooking or crafting)
    - Ingredients with quantities
    - Buff effects (cooking only)
    - Energy/health restoration
    - Source/unlock method
    - Sell price
    """
    data = {
        "type": "recipe",
        "name": page_title,
    }

    # Get main infobox
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                # Parse specific fields
                if "source" in key and "recipe" not in key:
                    # Determine if cooking or crafting
                    if "cooking" in value.lower():
                        data["recipe_type"] = "cooking"
                    elif "crafting" in value.lower():
                        data["recipe_type"] = "crafting"
                    data["source"] = value

                elif "recipe source" in key:
                    # How to unlock the recipe
                    data["unlock_source"] = value

                elif "ingredient" in key:
                    # Parse ingredients format: "Wood(50)Coal(1)Fiber(20)"
                    ingredients = []

                    # Find all text in the cell
                    ing_text = cells[1].get_text(strip=True)

                    # Pattern: ItemName(Quantity)
                    # Split by looking for patterns like "ItemName(number)"
                    matches = re.findall(r'([A-Za-z\s]+)\((\d+)\)', ing_text)

                    for item_name, quantity in matches:
                        ingredients.append({
                            "item": item_name.strip(),
                            "quantity": int(quantity)
                        })

                    if ingredients:
                        data["ingredients"] = ingredients

                elif "buff" in key and "duration" not in key:
                    # Buff effects (e.g., "Speed(+1)")
                    data["buff"] = value

                elif "buff duration" in key:
                    data["buff_duration"] = value

                elif "energy" in key and "health" in key:
                    # Extract numeric values from format like "7533"
                    # First 2-3 digits are energy, rest are health
                    numbers = re.findall(r'(\d+)', value)
                    if numbers and len(numbers[0]) >= 3:
                        # Try to split: "7533" -> 75 energy, 33 health
                        full_num = numbers[0]
                        if len(full_num) == 4:
                            data["energy"] = int(full_num[:2])
                            data["health"] = int(full_num[2:])
                        elif len(full_num) >= 3:
                            # Split at midpoint
                            mid = len(full_num) // 2
                            data["energy"] = int(full_num[:mid])
                            data["health"] = int(full_num[mid:])

                elif "sell" in key and "price" in key:
                    # Clean price
                    value_clean = value.replace(',', '')
                    match = re.search(r'(\d+)g', value_clean)
                    if match:
                        data["sell_price"] = int(match.group(1))
                    elif "cannot be sold" in value.lower():
                        data["sell_price"] = None

    return data


def parse_generic_item(soup: BeautifulSoup, page_title: str, item_type: str) -> dict[str, Any]:
    """
    Generic parser for items that don't fit other categories.

    Extracts basic information from the infobox.
    """
    data = {
        "type": item_type,
        "name": page_title,
    }

    # Find the infobox (usually a table with class 'infobox')
    # For items, it's often the first table on the page without a class
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        # Try the first table on the page
        tables = soup.find_all("table")
        if tables:
            infobox = tables[0]

    if infobox:
        for row in infobox.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)

                # Store key-value pairs
                # Sanitize key to be a valid dict key
                clean_key = re.sub(r'[^\w\s]', '', key).lower().replace(' ', '_')
                if clean_key:
                    # Special handling for prices - extract just the number
                    if clean_key in ['sell_price', 'purchase_price', 'buy_price']:
                        # Extract number from strings like "2g" or "1,500g" or "data-sort-value="2">2g"
                        # Remove commas first
                        value_clean = value.replace(',', '')
                        match = re.search(r'(\d+)g', value_clean)
                        if match:
                            data[clean_key] = int(match.group(1))
                        else:
                            data[clean_key] = value

                    # Special handling for monster stats - convert to integers
                    elif clean_key in ['base_hp', 'base_damage', 'base_def', 'speed', 'xp']:
                        # Convert numeric strings to integers
                        if value.isdigit():
                            data[clean_key] = int(value)
                        else:
                            # Try to extract number if there's extra text
                            match = re.search(r'(\d+)', value)
                            if match:
                                data[clean_key] = int(match.group(1))
                            else:
                                data[clean_key] = value

                    else:
                        data[clean_key] = value

    return data


# =============================================================================
# MCP SERVER SETUP
# =============================================================================

# Create the MCP server instance
# This is what Claude will connect to
app = Server("stardew-wiki")

# Create our wiki client instance
wiki_client = WikiClient(WIKI_API_URL)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Tell Claude what tools are available.

    This function is called when Claude starts up and wants to know
    what capabilities this MCP server provides.

    Each tool has:
    - name: Unique identifier for the tool
    - description: Tells Claude what the tool does
    - inputSchema: Defines what parameters Claude should send
    """
    return [
        Tool(
            name="search_wiki",
            description="Search the Stardew Valley Wiki for items, NPCs, locations, mechanics, and more. Returns a list of matching pages with titles and snippets. Best for: finding page names, exploratory searches, festival information, achievements, seasonal overviews, and general game mechanics. Use this for informational/overview queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term (e.g., 'apple', 'sebastian', 'community center')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10, max: 50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_page_data",
            description="Extract structured data from a specific Stardew Valley Wiki page. Returns structured JSON data. Best for: crops (seasons, growth time), fish (location, time, weather), NPCs (gift preferences, heart events, marriageable status, address, family), bundles (requirements), recipes (ingredients, buffs, energy), animals (costs, produce), monsters (stats, drops), and items (prices, sources). NOT recommended for: festivals, achievements, skills, or seasonal overview pages (use search_wiki instead for these).",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_title": {
                        "type": "string",
                        "description": "The exact title of the wiki page (e.g., 'Strawberry', 'Sebastian', 'Spring Crops Bundle')",
                    },
                },
                "required": ["page_title"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls from Claude.

    When Claude wants to use a tool, it calls this function with:
    - name: Which tool to use (e.g., "search_wiki")
    - arguments: The parameters (e.g., {"query": "apple", "limit": 10})

    This function:
    1. Validates the tool name
    2. Extracts the arguments
    3. Calls the appropriate wiki client method
    4. Formats the response for Claude
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    if name == "search_wiki":
        # Extract arguments (with defaults)
        query = arguments.get("query")
        limit = arguments.get("limit", 10)

        # Validate required parameters
        if not query:
            return [TextContent(
                type="text",
                text="Error: 'query' parameter is required"
            )]

        # Call the wiki client
        result = wiki_client.search(query, limit)

        # Format the response for Claude
        if result["success"]:
            # Build a readable text response
            response_lines = [
                f"Found {result['count']} results for '{query}':\n"
            ]

            for i, item in enumerate(result["results"], 1):
                title = item.get("title", "Unknown")
                snippet = item.get("snippet", "No description available")
                # Remove HTML tags from snippet for cleaner display
                snippet = snippet.replace("<span class=\"searchmatch\">", "")
                snippet = snippet.replace("</span>", "")

                response_lines.append(f"{i}. **{title}**")
                response_lines.append(f"   {snippet}")
                response_lines.append(f"   URL: https://stardewvalleywiki.com/{title.replace(' ', '_')}")
                response_lines.append("")  # Blank line between results

            response_text = "\n".join(response_lines)
        else:
            # Handle errors
            response_text = f"Search failed: {result.get('error', 'Unknown error')}"

        return [TextContent(type="text", text=response_text)]

    elif name == "get_page_data":
        # Extract arguments
        page_title = arguments.get("page_title")

        # Validate required parameters
        if not page_title:
            return [TextContent(
                type="text",
                text="Error: 'page_title' parameter is required"
            )]

        # Fetch the page
        page_result = wiki_client.get_page(page_title)

        if not page_result["success"]:
            # Page not found or error
            return [TextContent(
                type="text",
                text=f"Error fetching page '{page_title}': {page_result.get('error', 'Unknown error')}"
            )]

        # Parse the page data
        try:
            parsed_data = parse_page_data(
                html=page_result["html"],
                page_title=page_title,
                categories=page_result["categories"]
            )

            # Return structured JSON data
            # Claude will receive this and convert it to natural language
            json_data = json.dumps(parsed_data, indent=2)
            return [TextContent(
                type="text",
                text=json_data
            )]

        except Exception as e:
            logger.error(f"Error parsing page data: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error parsing page data: {str(e)}"
            )]

    # Unknown tool
    return [TextContent(
        type="text",
        text=f"Error: Unknown tool '{name}'"
    )]


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """
    Start the MCP server.

    This uses stdio (standard input/output) to communicate with Claude.
    Claude sends requests via stdin, and we respond via stdout.
    All logging must go to stderr to avoid interfering with the protocol.
    """
    logger.info("Starting Stardew Valley Wiki MCP server...")
    logger.info(f"Debug mode: {DEBUG}")

    # Run the server using stdio communication
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    """
    When this script is run directly, start the server.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
