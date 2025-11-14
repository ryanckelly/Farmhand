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
import threading
import time
from functools import wraps
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
# CUSTOM EXCEPTIONS
# =============================================================================

class WikiError(Exception):
    """Base exception for wiki operations."""
    pass

class PageNotFoundError(WikiError):
    """Raised when a wiki page doesn't exist."""
    def __init__(self, page_title: str):
        self.page_title = page_title
        super().__init__(
            f"Page '{page_title}' not found on the wiki. "
            f"Try using the search_wiki tool first to find the correct page name."
        )

class NetworkError(WikiError):
    """Raised when network connection to wiki fails."""
    def __init__(self, url: str, original_error: Exception):
        self.url = url
        self.original_error = original_error
        super().__init__(
            f"Failed to connect to {url}: {original_error}. "
            f"Please check your internet connection and try again."
        )

class ParseError(WikiError):
    """Raised when page parsing fails completely."""
    def __init__(self, page_title: str, reason: str):
        self.page_title = page_title
        self.reason = reason
        super().__init__(
            f"Failed to parse page '{page_title}': {reason}. "
            f"The page may have an unusual format. Please report this issue."
        )

class RedirectError(WikiError):
    """Raised when a page is a redirect."""
    def __init__(self, from_page: str, to_page: str):
        self.from_page = from_page
        self.to_page = to_page
        super().__init__(
            f"Page '{from_page}' redirects to '{to_page}'. "
            f"Use '{to_page}' instead for better results."
        )

# =============================================================================
# RETRY LOGIC
# =============================================================================

def retry_on_network_error(max_retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
    """
    Decorator to retry functions on network errors with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_factor: Multiplier for delay between retries (default: 2.0)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)

    Example:
        With max_retries=3, backoff_factor=2.0, initial_delay=1.0:
        - First retry: wait 1s
        - Second retry: wait 2s
        - Third retry: wait 4s

    Raises:
        NetworkError: If all retries are exhausted
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except requests.exceptions.Timeout as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise NetworkError
                        raise NetworkError(
                            url=str(args[0]) if args else "unknown",
                            original_error=e
                        )

                    # Calculate delay with exponential backoff
                    delay = initial_delay * (backoff_factor ** attempt)
                    logger.warning(
                        f"{func.__name__} timed out (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)

                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise NetworkError
                        raise NetworkError(
                            url=str(args[0]) if args else "unknown",
                            original_error=e
                        )

                    # Calculate delay with exponential backoff
                    delay = initial_delay * (backoff_factor ** attempt)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}, "
                        f"retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)

            # Should not reach here, but just in case
            if last_exception:
                raise NetworkError(
                    url=str(args[0]) if args else "unknown",
                    original_error=last_exception
                )

        return wrapper
    return decorator

# =============================================================================
# CACHING
# =============================================================================

class WikiCache:
    """
    Simple in-memory cache with Time-To-Live (TTL) for wiki pages.

    This cache stores fetched wiki pages to avoid redundant API calls.
    Cached entries expire after a specified TTL period.

    Attributes:
        ttl_seconds: Time in seconds before cached entries expire
        max_size: Maximum number of entries to cache (prevent memory bloat)
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 100):
        """
        Initialize the cache.

        Args:
            ttl_seconds: Time-to-live for cached entries (default: 1 hour)
            max_size: Maximum cache size (default: 100 entries)
        """
        self.cache = {}  # {key: (value, timestamp)}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.hits = 0  # Cache hit counter
        self.misses = 0  # Cache miss counter

    def get(self, key: str) -> Any | None:
        """
        Get a cached value if it exists and hasn't expired.

        Args:
            key: Cache key (usually page title)

        Returns:
            Cached value if found and valid, None otherwise
        """
        key_lower = key.lower()  # Case-insensitive keys

        if key_lower in self.cache:
            value, timestamp = self.cache[key_lower]

            # Check if entry has expired
            age_seconds = time.time() - timestamp
            if age_seconds < self.ttl_seconds:
                self.hits += 1
                return value
            else:
                # Expired, remove it
                del self.cache[key_lower]
                self.misses += 1
                return None
        else:
            self.misses += 1
            return None

    def set(self, key: str, value: Any):
        """
        Cache a value with current timestamp.

        Args:
            key: Cache key (usually page title)
            value: Value to cache
        """
        key_lower = key.lower()  # Case-insensitive keys

        # Enforce max size - remove oldest entry if at capacity
        if len(self.cache) >= self.max_size and key_lower not in self.cache:
            # Remove oldest entry (simple FIFO eviction)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache full, evicted oldest entry: {oldest_key}")

        self.cache[key_lower] = (value, time.time())

    def clear(self):
        """Clear all cached entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hit rate, size, and other metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 1),
            "ttl_seconds": self.ttl_seconds,
        }

# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Prevents making too many requests per second to avoid throttling
    by the wiki server. Thread-safe for concurrent requests.

    Attributes:
        requests_per_second: Maximum requests allowed per second
        min_interval: Minimum time between requests (in seconds)
    """

    def __init__(self, requests_per_second: float = 5.0):
        """
        Initialize the rate limiter.

        Args:
            requests_per_second: Maximum requests per second (default: 5)
                MediaWiki typical limit: 10-20 req/s
                Conservative default: 5 req/s
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        self.lock = threading.Lock()

        logger.info(f"RateLimiter initialized: {requests_per_second} requests/second")

    def wait_if_needed(self):
        """
        Wait if necessary to respect rate limit.

        This method blocks if we're making requests too quickly.
        Thread-safe - only one thread waits at a time.
        """
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.min_interval:
                # Too fast, need to wait
                wait_time = self.min_interval - time_since_last
                logger.debug(f"Rate limit: waiting {wait_time:.3f}s")
                time.sleep(wait_time)

            # Update last request time
            self.last_request_time = time.time()

# =============================================================================
# SEARCH QUERY PREPROCESSING
# =============================================================================

def preprocess_query(query: str) -> list[str]:
    """
    Preprocess natural language search queries into better search terms.

    MediaWiki search is basic keyword matching - no boolean operators,
    no semantic understanding. This function converts natural language
    queries into multiple search strategies.

    Args:
        query: Natural language query (e.g., "what does sebastian like?")

    Returns:
        List of search terms to try, in order of priority

    Examples:
        "spring birthdays" → ["Calendar", "birthday", "spring"]
        "what does sebastian like" → ["Sebastian", "sebastian gifts"]
        "crops in summer" → ["Summer Crops", "summer", "crops"]
    """
    query_lower = query.lower().strip()
    search_strategies = []

    # Pattern 1: "what does X like/love/hate" → NPC gift preferences
    gift_patterns = [
        r"what (?:does|do) (\w+) (?:like|love|hate|want)",
        r"(\w+)'s? (?:favorite|liked|loved|hated) (?:gift|item|thing)",
        r"gift(?:s)? for (\w+)",
        r"best gift for (\w+)"
    ]
    for pattern in gift_patterns:
        match = re.search(pattern, query_lower)
        if match:
            npc_name = match.group(1).title()  # Capitalize first letter
            search_strategies.append(npc_name)  # Direct NPC page
            search_strategies.append(f"{npc_name} gifts")
            return search_strategies

    # Pattern 2: "X birthdays" or "birthdays in X" → Calendar
    if "birthday" in query_lower:
        search_strategies.append("Calendar")  # Calendar page lists all birthdays
        search_strategies.append("birthday")
        # Extract season if present
        for season in ["spring", "summer", "fall", "winter"]:
            if season in query_lower:
                search_strategies.append(season)
                break
        return search_strategies

    # Pattern 3: "crops in/for X season" → Season-specific crop searches
    crop_season_patterns = [
        r"crops? (?:in|for|during) (\w+)",
        r"(\w+) crops?",
        r"what (?:to|can i) plant (?:in|during) (\w+)"
    ]
    for pattern in crop_season_patterns:
        match = re.search(pattern, query_lower)
        if match and "crop" in query_lower:
            season = match.group(1).title()
            if season in ["Spring", "Summer", "Fall", "Winter"]:
                search_strategies.append(f"{season} Crops")
                search_strategies.append(season)
                search_strategies.append("crops")
                return search_strategies

    # Pattern 4: "where to find X" or "how to get X" → Item source
    location_patterns = [
        r"where (?:to find|can i (?:find|get)) (.+)",
        r"how (?:to|do i) (?:get|obtain|find) (.+)",
        r"location of (.+)"
    ]
    for pattern in location_patterns:
        match = re.search(pattern, query_lower)
        if match:
            item = match.group(1).strip()
            search_strategies.append(item.title())  # Try exact item name
            search_strategies.append(item)
            return search_strategies

    # Pattern 5: "X bundle" → Bundle searches
    if "bundle" in query_lower:
        # Remove "what do i need for" type phrases
        bundle_query = re.sub(r"what (?:do i|does .+) need (?:for|to complete) ", "", query_lower)
        bundle_query = re.sub(r"(?:items for|requirements for) ", "", bundle_query)
        search_strategies.append(bundle_query.title())
        search_strategies.append("bundles")
        return search_strategies

    # Pattern 6: "X festival" or "when is X" → Festival/event searches
    if "festival" in query_lower or "event" in query_lower:
        # Extract festival name if present
        festival_query = re.sub(r"when is (?:the )?", "", query_lower)
        festival_query = re.sub(r"what (?:happens at|is) (?:the )?", "", festival_query)
        search_strategies.append(festival_query.title())
        search_strategies.append("festivals")
        return search_strategies

    # Pattern 7: "X quest" → Quest searches
    if "quest" in query_lower:
        quest_query = re.sub(r"(?:how to complete|requirements for) ", "", query_lower)
        search_strategies.append(quest_query.title())
        search_strategies.append("quests")
        return search_strategies

    # Pattern 8: Multi-word phrases → Extract key concepts
    # Remove common filler words
    filler_words = ["the", "a", "an", "in", "on", "at", "to", "for", "of", "with",
                   "is", "are", "was", "were", "can", "i", "you", "what", "where",
                   "when", "how", "do", "does", "did"]

    words = query_lower.split()
    keywords = [w for w in words if w not in filler_words and len(w) > 2]

    # If we extracted keywords, use them
    if keywords:
        # Try multi-word search first (capitalized for better matching)
        if len(keywords) > 1:
            combined = " ".join([w.title() for w in keywords])
            search_strategies.append(combined)

        # Then try individual keywords (most important first)
        for keyword in keywords:
            search_strategies.append(keyword.title())

    # Fallback: Use original query if no patterns matched
    if not search_strategies:
        search_strategies.append(query.title())
        search_strategies.append(query.lower())

    return search_strategies


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

    def __init__(self, api_url: str, cache_ttl: int = 3600, cache_max_size: int = 100, rate_limit: float = 5.0):
        """
        Initialize the Wiki client.

        Args:
            api_url: The base URL for the MediaWiki API
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            cache_max_size: Maximum number of cached pages (default: 100)
            rate_limit: Maximum requests per second (default: 5.0)
        """
        self.api_url = api_url
        self.session = requests.Session()
        # Set a user agent to identify our bot (good practice for API usage)
        self.session.headers.update({
            "User-Agent": "StardewWikiMCP/1.0 (Claude Code Integration)"
        })
        # Initialize cache
        self.cache = WikiCache(ttl_seconds=cache_ttl, max_size=cache_max_size)
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit)
        logger.info(f"WikiClient initialized with API: {api_url} (cache TTL: {cache_ttl}s, max size: {cache_max_size}, rate limit: {rate_limit} req/s)")

    @retry_on_network_error(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
    def _make_api_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Make an API request with retry logic and rate limiting.

        This internal method handles all HTTP requests to the wiki API.
        It automatically:
        - Waits if necessary to respect rate limit
        - Retries on network errors with exponential backoff

        Args:
            params: API parameters dictionary

        Returns:
            JSON response from the API

        Raises:
            NetworkError: If all retries are exhausted
        """
        # Wait if necessary to respect rate limit
        self.rate_limiter.wait_if_needed()

        # Make the request
        response = self.session.get(
            self.api_url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

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
            # Make the HTTP request with automatic retry logic
            data = self._make_api_request(params)

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

        except NetworkError as e:
            # Network error after retries exhausted
            logger.error(f"Network error when searching for '{query}': {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
            }

        except Exception as e:
            logger.error(f"Unexpected error when searching for '{query}': {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "query": query,
            }

    def smart_search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """
        Intelligent search with query preprocessing and fallback strategies.

        This method:
        1. Preprocesses the natural language query into better search terms
        2. Tries multiple search strategies in order
        3. Returns the first successful result with matches
        4. Falls back to original query if all strategies fail

        Args:
            query: Natural language search query
            limit: Maximum results to return

        Returns:
            Search results with added metadata about which strategy worked

        Example:
            "spring birthdays" → Tries: ["Calendar", "birthday", "spring"]
            Returns results from "Calendar" page
        """
        # Preprocess query to get search strategies
        search_terms = preprocess_query(query)

        logger.info(f"Smart search for '{query}' → strategies: {search_terms}")

        # Try each search strategy in order
        for i, term in enumerate(search_terms):
            result = self.search(term, limit)

            if result["success"] and result["count"] > 0:
                # Found results! Add metadata and return
                result["original_query"] = query
                result["strategy_used"] = term
                result["strategy_index"] = i
                logger.info(f"Smart search successful with strategy #{i}: '{term}' ({result['count']} results)")
                return result

        # No strategies worked - try original query as last resort
        logger.warning(f"Smart search: all strategies failed for '{query}', trying original query")
        result = self.search(query, limit)
        result["original_query"] = query
        result["strategy_used"] = query
        result["strategy_index"] = len(search_terms)
        return result

    def get_page(self, page_title: str) -> dict[str, Any]:
        """
        Fetch the HTML content of a wiki page with caching.

        This uses MediaWiki's parse API to get the rendered HTML of a page.
        Results are cached to avoid redundant API calls.

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
        # Check cache first
        cached_result = self.cache.get(page_title)
        if cached_result is not None:
            logger.info(f"Cache hit for '{page_title}'")
            # Log cache stats periodically (every 10 hits)
            if self.cache.hits % 10 == 0:
                stats = self.cache.get_stats()
                logger.info(f"Cache stats: {stats['hit_rate_percent']}% hit rate, {stats['size']}/{stats['max_size']} entries")
            return cached_result

        logger.debug(f"Cache miss for '{page_title}', fetching from API")

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
            # Make the HTTP request with automatic retry logic
            data = self._make_api_request(params)

            if DEBUG:
                logger.debug(f"API response keys: {data.keys()}")

            # Check if the page exists
            if "error" in data:
                error_info = data['error'].get('info', 'Unknown error')
                logger.warning(f"Page not found: '{page_title}'")

                # Raise PageNotFoundError for better error handling
                raise PageNotFoundError(page_title)

            # Extract HTML and categories
            parse_data = data.get("parse", {})
            html = parse_data.get("text", {}).get("*", "")
            categories = [cat["*"] for cat in parse_data.get("categories", [])]

            logger.info(f"Successfully fetched page: '{page_title}'")

            result = {
                "success": True,
                "page_title": page_title,
                "html": html,
                "categories": categories,
            }

            # Cache the successful result
            self.cache.set(page_title, result)

            return result

        except PageNotFoundError as e:
            # Page doesn't exist
            logger.error(f"Page not found: '{page_title}'")
            return {
                "success": False,
                "error": str(e),
                "page_title": page_title,
            }

        except NetworkError as e:
            # Network error after retries exhausted
            logger.error(f"Network error when fetching '{page_title}': {e}")
            return {
                "success": False,
                "error": str(e),
                "page_title": page_title,
            }

        except Exception as e:
            logger.error(f"Unexpected error when fetching '{page_title}': {e}")
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
    elif page_type == "skill":
        return parse_skill_data(soup, page_title)
    elif page_type == "quests":
        return parse_quest_data(soup, page_title)
    elif page_type == "achievements":
        return parse_achievement_data(soup, page_title)
    elif page_type in ["artifact", "mineral"]:
        # Check if this is a collection list page (plural) or single item page
        # List pages: "Artifacts", "Minerals"
        # Single item pages: "Dwarf Gadget", "Quartz"
        if page_title.lower() in ["artifacts", "minerals"]:
            return parse_collection_list(soup, page_title, page_type)
        else:
            return parse_generic_item(soup, page_title, page_type)
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

    # PRIORITY 1: Exact title matches (highest priority to avoid misclassification)
    # These pages often have multiple categories, so exact title match takes precedence
    if title_lower == "quests":
        return "quests"
    if title_lower == "achievements":
        return "achievements"

    # Check for skills - exact title match (e.g., "Fishing" should be skill, not fish)
    skill_names = ["farming", "mining", "foraging", "fishing", "combat", "luck"]
    if title_lower in skill_names:
        return "skill"

    # PRIORITY 2: Category-based detection
    # Check for quests (before achievements, as quest pages may have achievement categories)
    if any("quest" in c for c in cat_lower):
        return "quests"
    # Check for achievements
    if any("achievement" in c for c in cat_lower):
        return "achievements"
    # Check for skills via categories
    if any(skill in cat_lower for skill in skill_names):
        return "skill"
    elif any("crop" in c for c in cat_lower):
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
    elif any("monster" in c for c in cat_lower):
        return "monster"

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
    Extract structured data for crops with graceful degradation.

    Looks for the infobox and extracts:
    - Season(s)
    - Growth time
    - Regrowth time
    - Sell prices
    - Seed source and price

    Returns partial data if some fields fail to parse.
    """
    data = {
        "type": "crop",
        "name": page_title,
        "parsing_warnings": [],  # Track any parsing failures
    }

    # Extract infobox data with error handling
    try:
        # Find the infobox (usually a table with class 'infobox')
        infobox = soup.find("table", class_="infobox")
        if not infobox:
            # Try the first table on the page
            tables = soup.find_all("table")
            if tables:
                infobox = tables[0]

        if infobox:
            # Extract key-value pairs from infobox rows
            for row in infobox.find_all("tr"):
                try:
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
                except Exception as e:
                    # Log but continue processing other rows
                    logger.debug(f"Crop {page_title}: Failed to parse infobox row: {e}")
                    continue

    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract infobox data: {str(e)}")
        logger.warning(f"Crop {page_title}: Infobox extraction failed - {e}")

    # Extract sell prices with error handling
    try:
        price_table = soup.find("table", string=re.compile("Sell Price", re.I))
        if not price_table:
            # Try finding by nearby text
            price_header = soup.find(string=re.compile("Sell Price", re.I))
            if price_header:
                price_table = price_header.find_parent("table")

        if price_table:
            prices = {}
            for row in price_table.find_all("tr")[1:]:  # Skip header row
                try:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        quality = cells[0].get_text(strip=True).lower()
                        price_text = cells[1].get_text(strip=True)
                        # Extract number (e.g., "120g" -> 120)
                        match = re.search(r'(\d+)', price_text)
                        if match:
                            prices[quality] = int(match.group(1))
                except Exception as e:
                    logger.debug(f"Crop {page_title}: Failed to parse price row: {e}")
                    continue

            if prices:
                data["sell_prices"] = prices

    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract sell prices: {str(e)}")
        logger.warning(f"Crop {page_title}: Price extraction failed - {e}")

    return data


def parse_npc_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for NPCs/Villagers with graceful degradation.

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
        "parsing_warnings": [],
    }

    # Find birthday and other info in infobox
    try:
        infobox = soup.find("table", class_="infobox")
        if not infobox:
            # Try first table on page
            tables = soup.find_all("table")
            if tables:
                infobox = tables[0]

        if infobox:
            for row in infobox.find_all("tr"):
                try:
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
                except Exception as e:
                    logger.debug(f"NPC {page_title}: Failed to parse infobox row: {e}")
                    continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract infobox data: {str(e)}")
        logger.warning(f"NPC {page_title}: Infobox extraction failed - {e}")

    # Extract gift preferences
    # Wiki has sections like "Love", "Like", etc. as h3 headers
    # Gift items are in <p> tags between the h3 and the next h3
    for gift_type in ["loved", "liked", "neutral", "disliked", "hated"]:
        try:
            # Find h3 header (e.g., "Love", "Like")
            # Note: header text is just "Love" not "Loved Gifts"
            search_text = gift_type.rstrip("d")  # "loved" -> "love", "liked" -> "like"

            for h3 in soup.find_all("h3"):
                try:
                    h3_text = h3.get_text(strip=True).lower()
                    if search_text in h3_text:
                        # Get all <p> tags between this h3 and the next h3
                        gifts = []
                        current = h3.find_next_sibling()
                        next_h3 = h3.find_next("h3")

                        while current and current != next_h3:
                            try:
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
                            except Exception as e:
                                logger.debug(f"NPC {page_title}: Failed to parse gift item: {e}")
                                pass
                            current = current.find_next_sibling()

                        if gifts:
                            data[f"{gift_type}_gifts"] = gifts
                        break
                except Exception as e:
                    logger.debug(f"NPC {page_title}: Failed to parse {gift_type} gifts section: {e}")
                    continue
        except Exception as e:
            data["parsing_warnings"].append(f"Failed to extract {gift_type} gifts: {str(e)}")
            logger.warning(f"NPC {page_title}: {gift_type.capitalize()} gifts extraction failed - {e}")

    # Extract heart events
    try:
        heart_events = parse_heart_events(soup)
        if heart_events:
            data["heart_events"] = heart_events
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract heart events: {str(e)}")
        logger.warning(f"NPC {page_title}: Heart events extraction failed - {e}")

    return data


def parse_heart_events(soup: BeautifulSoup) -> list[dict]:
    """
    Extract heart event information from NPC pages with graceful degradation.

    Returns list of events with:
    - heart_level (2, 4, 6, 8, 10, 14)
    - title (event heading)
    - trigger (if available)
    """
    events = []

    try:
        # Find "Heart Events" or "Events" section
        for h2 in soup.find_all(['h2', 'span'], class_=['mw-headline']):
            try:
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
                        try:
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
                                    try:
                                        if current.parent:
                                            next_p = current.parent.find_next('p')
                                            if next_p:
                                                trigger_text = next_p.get_text(strip=True)
                                                # Only include if it's short (likely a trigger description)
                                                if len(trigger_text) < 200:
                                                    event_data["trigger"] = trigger_text
                                    except Exception as e:
                                        logger.debug(f"Failed to parse trigger for event '{event_title}': {e}")
                                        pass

                                    events.append(event_data)
                        except Exception as e:
                            logger.debug(f"Failed to parse heart event: {e}")
                            pass

                        # Find next h3
                        try:
                            current = current.find_next(['h3', 'span'], class_=['mw-headline'])
                            if not current or current.name != 'span':
                                break
                            # Make sure we're still looking at h3 headers
                            if current.parent.name != 'h3':
                                break
                        except Exception as e:
                            logger.debug(f"Failed to find next heart event: {e}")
                            break

                    break  # Found the events section, stop searching
            except Exception as e:
                logger.debug(f"Failed to parse heart events section: {e}")
                continue
    except Exception as e:
        logger.warning(f"Heart events parsing failed completely: {e}")

    return events


def parse_bundle_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for Community Center bundles with graceful degradation.

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
        "requirements": [],
        "parsing_warnings": []
    }

    # Check if this is a stub page (no meaningful tables)
    try:
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
                                try:
                                    # Skip reward rows
                                    row_text = row.get_text(strip=True).lower()
                                    if "reward" in row_text:
                                        continue

                                    cells = row.find_all("td")
                                    if cells:
                                        # Look through all cells for item links
                                        # (different bundles have different table structures)
                                        for cell in cells:
                                            try:
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
                                            except Exception as e:
                                                logger.debug(f"Bundle {page_title}: Failed to parse cell: {e}")
                                                continue
                                except Exception as e:
                                    logger.debug(f"Bundle {page_title}: Failed to parse row: {e}")
                                    continue

                            logger.info(f"Extracted {len(data['requirements'])} items for '{page_title}'")
                            return data
            except Exception as e:
                data["parsing_warnings"].append(f"Failed to fetch main Bundles page: {str(e)}")
                logger.warning(f"Bundle {page_title}: Error fetching main Bundles page - {e}")
                # Continue with original parsing below
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to check for stub page: {str(e)}")
        logger.warning(f"Bundle {page_title}: Stub check failed - {e}")

    # Original parsing logic for pages with content
    try:
        for table in soup.find_all("table"):
            try:
                headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

                if "item" in headers or "source" in headers:
                    # This looks like a bundle requirements table
                    for row in table.find_all("tr")[1:]:  # Skip header
                        try:
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
                        except Exception as e:
                            logger.debug(f"Bundle {page_title}: Failed to parse requirement row: {e}")
                            continue
            except Exception as e:
                logger.debug(f"Bundle {page_title}: Failed to parse table: {e}")
                continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract requirements: {str(e)}")
        logger.warning(f"Bundle {page_title}: Requirements extraction failed - {e}")

    return data


def parse_fish_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for fish with graceful degradation.

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
        "parsing_warnings": []
    }

    # Find the infobox (usually a table with class 'infobox')
    # For fish, it's often the first table on the page without a class
    try:
        infobox = soup.find("table", class_="infobox")
        if not infobox:
            # Try the first table on the page
            tables = soup.find_all("table")
            if tables:
                infobox = tables[0]

        if infobox:
            for row in infobox.find_all("tr"):
                try:
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
                except Exception as e:
                    logger.debug(f"Fish {page_title}: Failed to parse infobox row: {e}")
                    continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract infobox data: {str(e)}")
        logger.warning(f"Fish {page_title}: Infobox extraction failed - {e}")

    return data


def parse_recipe_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for cooking and crafting recipes with graceful degradation.

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
        "parsing_warnings": []
    }

    # Get main infobox
    try:
        infobox = soup.find("table", class_="infobox")
        if not infobox:
            tables = soup.find_all("table")
            if tables:
                infobox = tables[0]

        if infobox:
            for row in infobox.find_all("tr"):
                try:
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
                            try:
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
                            except Exception as e:
                                logger.debug(f"Recipe {page_title}: Failed to parse ingredients: {e}")

                        elif "buff" in key and "duration" not in key:
                            # Buff effects (e.g., "Speed(+1)")
                            data["buff"] = value

                        elif "buff duration" in key:
                            data["buff_duration"] = value

                        elif "energy" in key and "health" in key:
                            # Extract numeric values from format like "7533"
                            # First 2-3 digits are energy, rest are health
                            try:
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
                            except Exception as e:
                                logger.debug(f"Recipe {page_title}: Failed to parse energy/health: {e}")

                        elif "sell" in key and "price" in key:
                            # Clean price
                            try:
                                value_clean = value.replace(',', '')
                                match = re.search(r'(\d+)g', value_clean)
                                if match:
                                    data["sell_price"] = int(match.group(1))
                                elif "cannot be sold" in value.lower():
                                    data["sell_price"] = None
                            except Exception as e:
                                logger.debug(f"Recipe {page_title}: Failed to parse price: {e}")
                except Exception as e:
                    logger.debug(f"Recipe {page_title}: Failed to parse infobox row: {e}")
                    continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract infobox data: {str(e)}")
        logger.warning(f"Recipe {page_title}: Infobox extraction failed - {e}")

    # Check for products table (for artisan equipment like Keg, Preserves Jar, etc.)
    # Look for tables with "Product", "Time", or "Processing Time" headers
    try:
        products = []
        for table in soup.find_all("table", class_="wikitable"):
            try:
                headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]

                # Check if this looks like a products table
                # Look for tables with product/name and time/duration columns
                has_product = any("product" in h or (h == "name" and any("time" in hh for hh in headers)) for h in headers)
                has_time = any("time" in h or "duration" in h for h in headers)

                if has_product and has_time:
                    # Find column indices
                    product_idx = next((i for i, h in enumerate(headers) if "product" in h or (h == "name" and has_time)), None)
                    time_idx = next((i for i, h in enumerate(headers) if "time" in h or "duration" in h), None)
                    input_idx = next((i for i, h in enumerate(headers) if "input" in h or "ingredient" in h), None)

                    # Parse product rows
                    for row in table.find_all("tr")[1:]:  # Skip header
                        try:
                            cells = row.find_all("td")
                            if len(cells) > max(product_idx or 0, time_idx or 0):
                                product_name = cells[product_idx].get_text(strip=True) if product_idx is not None else None
                                time_text = cells[time_idx].get_text(strip=True) if time_idx is not None else None
                                input_text = cells[input_idx].get_text(strip=True) if input_idx is not None else None

                                if product_name and time_text:
                                    product_entry = {
                                        "product": product_name,
                                        "processing_time": time_text
                                    }

                                    if input_text:
                                        product_entry["input"] = input_text

                                    # Try to extract numeric minutes from time text
                                    try:
                                        minutes_match = re.search(r'(\d+)\s*m', time_text.lower())
                                        if minutes_match:
                                            product_entry["processing_minutes"] = int(minutes_match.group(1))
                                    except Exception as e:
                                        logger.debug(f"Recipe {page_title}: Failed to parse processing minutes: {e}")

                                    products.append(product_entry)
                        except Exception as e:
                            logger.debug(f"Recipe {page_title}: Failed to parse product row: {e}")
                            continue
            except Exception as e:
                logger.debug(f"Recipe {page_title}: Failed to parse products table: {e}")
                continue

        if products:
            data["products"] = products
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract products data: {str(e)}")
        logger.warning(f"Recipe {page_title}: Products extraction failed - {e}")

    return data


def parse_skill_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for skills (Farming, Mining, Foraging, Fishing, Combat).

    Extracts:
    - Level progression (1-10) with unlocked recipes
    - Profession choices at levels 5 and 10
    - Profession descriptions and bonuses

    Args:
        soup: BeautifulSoup object of the page HTML
        page_title: Name of the skill (e.g., "Farming")

    Returns:
        Dictionary with skill name, levels, and professions
    """
    data = {
        "type": "skill",
        "name": page_title,
        "levels": {},
        "professions": {},
        "parsing_warnings": []
    }

    # Find the level progression table (wikitable with "Level 1" in header row)
    try:
        table = None
        for candidate_table in soup.find_all("table", class_="wikitable"):
            try:
                rows = candidate_table.find_all("tr")
                if rows:
                    first_row_text = rows[0].get_text()
                    # Check if this table has level headers like "Level 1", "Level 2", etc.
                    if "Level 1" in first_row_text or "Level 2" in first_row_text:
                        table = candidate_table
                        break
            except Exception as e:
                logger.debug(f"Skill {page_title}: Failed to check table: {e}")
                continue

        if not table:
            return data
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to find level progression table: {str(e)}")
        logger.warning(f"Skill {page_title}: Table finding failed - {e}")
        return data

    rows = table.find_all("tr")
    if len(rows) < 3:
        return data

    # Parse table structure:
    # The table has TWO row groups:
    #   Group 1: Levels 1-5 (rows 0-3 typically)
    #   Group 2: Levels 6-10 (rows 4-7 typically)
    # Each group has:
    #   Row 0: Level headers (th cells)
    #   Row 1: "Crafting Recipes:" labels (td cells)
    #   Row 2+: Content rows with recipes or professions

    # Profession keywords for detection
    profession_keywords = ['Rancher', 'Tiller', 'Coopmaster', 'Artisan', 'Shepherd', 'Agriculturist',
                           'Miner', 'Geologist', 'Blacksmith', 'Prospector', 'Excavator', 'Gemologist',
                           'Forester', 'Gatherer', 'Lumberjack', 'Tapper', 'Botanist', 'Tracker',
                           'Fisher', 'Trapper', 'Angler', 'Pirate', 'Mariner', 'Luremaster',
                           'Fighter', 'Scout', 'Brute', 'Defender', 'Acrobat', 'Desperado']

    # Find all header rows (contain "Level X")
    current_levels = []
    row_idx = 0

    while row_idx < len(rows):
        row = rows[row_idx]
        header_cells = row.find_all("th")

        # Check if this is a header row
        is_header = False
        if header_cells:
            text = row.get_text()
            if "Level" in text:
                is_header = True
                # Extract level numbers from this header row
                current_levels = []
                for cell in header_cells:
                    cell_text = cell.get_text(strip=True)
                    match = re.search(r'Level (\d+)', cell_text)
                    if match:
                        current_levels.append(int(match.group(1)))

        if is_header and current_levels:
            # Get the label row (next row after header) to check which columns have professions
            label_row_idx = row_idx + 1
            profession_columns = set()  # Track which column indices have profession choices

            if label_row_idx < len(rows):
                label_row = rows[label_row_idx]
                label_cells = label_row.find_all(["td"])
                for col_idx, cell in enumerate(label_cells):
                    if "Choose a Profession" in cell.get_text():
                        profession_columns.add(col_idx)

            # Skip the label row
            row_idx += 1
            if row_idx >= len(rows):
                break

            # Now parse content rows until we hit another header or end
            row_idx += 1
            while row_idx < len(rows):
                content_row = rows[row_idx]

                # Check if this is another header row (start of next group)
                if content_row.find_all("th") and "Level" in content_row.get_text():
                    break

                # Parse this content row
                cells = content_row.find_all(["td"])

                # Check if this row contains ONLY professions (no recipes)
                # This helps detect special rows where professions span wrong columns
                # A row is profession-only if:
                # 1. It has 2 or fewer non-empty cells (professions are choices, not long lists)
                # 2. ALL non-empty cells contain at least one profession keyword
                non_empty_cells = [cell for cell in cells if cell.get_text(strip=True)]
                row_only_has_professions = False
                if len(non_empty_cells) <= 2 and len(non_empty_cells) > 0:
                    all_cells_have_professions = all(
                        any(prof in cell.get_text(strip=True) for prof in profession_keywords)
                        for cell in non_empty_cells
                    )
                    row_only_has_professions = all_cells_have_professions

                # If this row only has professions and we're in second group (6-10),
                # then professions are actually for the last level (level 10), not the column level
                if row_only_has_professions and current_levels and max(current_levels) == 10:
                    # All professions in this row are level 10 professions
                    # Skip the profession_columns check for these special rows
                    for col_idx, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        if not cell_text:
                            continue

                        # Parse professions from this cell (skip profession_columns check)
                        if any(prof in cell_text for prof in profession_keywords):
                            professions_found = []
                            for prof_name in profession_keywords:
                                if prof_name in cell_text:
                                    start_idx = cell_text.find(prof_name)
                                    if start_idx == -1:
                                        continue

                                    end_idx = len(cell_text)
                                    for other_prof in profession_keywords:
                                        if other_prof != prof_name:
                                            next_idx = cell_text.find(other_prof, start_idx + len(prof_name))
                                            if next_idx != -1 and next_idx < end_idx:
                                                end_idx = next_idx

                                    description = cell_text[start_idx + len(prof_name):end_idx].strip()

                                    if not any(p["name"] == prof_name for p in professions_found):
                                        professions_found.append({
                                            "name": prof_name,
                                            "description": description
                                        })

                            if professions_found:
                                # Add to level 10, not the column index level
                                if 10 not in data["professions"]:
                                    data["professions"][10] = []
                                data["professions"][10].extend(professions_found)
                else:
                    # Normal parsing - use column index to determine level
                    for col_idx, cell in enumerate(cells):
                        # Get the level number, but allow cells beyond header count for professions
                        # (profession choices can be in extra cells)
                        if col_idx < len(current_levels):
                            level_num = current_levels[col_idx]
                        else:
                            # Extra cell beyond headers - use the last level (5 or 10)
                            level_num = current_levels[-1] if current_levels else None
                            if not level_num:
                                continue

                        cell_text = cell.get_text(strip=True)

                        # Skip empty cells or label cells
                        if not cell_text or cell_text in ["Crafting Recipes:", "Crafting / Cooking Recipes:", "Choose a Profession:"]:
                            continue

                        # Check if this column is marked for professions AND contains profession keywords
                        is_profession_column = col_idx in profession_columns or (
                            col_idx >= len(current_levels) and len(profession_columns) > 0
                        )
                        has_profession = is_profession_column and any(prof in cell_text for prof in profession_keywords)

                        if has_profession:
                            # Parse professions
                            professions_found = []
                            for prof_name in profession_keywords:
                                if prof_name in cell_text:
                                    start_idx = cell_text.find(prof_name)
                                    if start_idx == -1:
                                        continue

                                    end_idx = len(cell_text)
                                    for other_prof in profession_keywords:
                                        if other_prof != prof_name:
                                            next_idx = cell_text.find(other_prof, start_idx + len(prof_name))
                                            if next_idx != -1 and next_idx < end_idx:
                                                end_idx = next_idx

                                    description = cell_text[start_idx + len(prof_name):end_idx].strip()

                                    if not any(p["name"] == prof_name for p in professions_found):
                                        professions_found.append({
                                            "name": prof_name,
                                            "description": description
                                        })

                            if professions_found:
                                if level_num not in data["professions"]:
                                    data["professions"][level_num] = []
                                data["professions"][level_num].extend(professions_found)
                        else:
                            # Parse recipes from links (only for cells within header range)
                            if col_idx < len(current_levels):
                                recipes = []
                                links = cell.find_all("a")
                                for link in links:
                                    recipe_name = link.get_text(strip=True)
                                    if recipe_name and len(recipe_name) > 1:
                                        recipes.append(recipe_name)

                                if recipes:
                                    data["levels"][level_num] = {
                                        "recipes": recipes
                                    }

                row_idx += 1
        else:
            row_idx += 1

    return data


def parse_quest_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for quests from the Quests page.

    The Quests page contains multiple tables for different quest types:
    - Story Quests
    - Special Orders
    - Mr. Qi's Special Orders

    Args:
        soup: BeautifulSoup object of the page HTML
        page_title: Name of the page (should be "Quests" or "Quest")

    Returns:
        Dictionary with quest categories and quest data
    """
    data = {
        "type": "quests",
        "name": page_title,
        "story_quests": [],
        "special_orders": [],
        "qi_special_orders": [],
        "parsing_warnings": []
    }

    # Find all wikitables
    try:
        tables = soup.find_all("table", class_="wikitable")

        if not tables:
            return data

        # Parse each table based on its headers
        for table in tables:
            try:
                rows = table.find_all("tr")
                if len(rows) < 2:  # Need header + at least one data row
                    continue

                # Get headers
                header_row = rows[0]
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

                if not headers:
                    continue

                # Determine quest type based on headers
                quest_type = None
                if "Quest Name" in headers:
                    if "Prerequisites" in headers:
                        # Special Orders have Prerequisites instead of Requirements
                        quest_type = "special_orders"
                    elif "Maximum Timeframe" in headers and "Provided By" not in headers:
                        # Qi's Special Orders: Quest Name, Text, Timeframe, Requirements, Rewards (no Provider)
                        quest_type = "qi_special_orders"
                    elif "Provided By" in headers and "Requirements" in headers and "Rewards" in headers:
                        # Story Quests: Quest Name, Text, Provided By, Requirements, Rewards
                        quest_type = "story_quests"

                # Skip if not a quest table or if it's the quest items table
                if not quest_type or "Image" in headers or "Description" in headers:
                    continue

                # Parse quest rows
                for row_idx in range(1, len(rows)):
                    try:
                        row = rows[row_idx]
                        cells = row.find_all(["td"])

                        if len(cells) < len(headers):
                            continue

                        quest = {}

                        # Extract data based on headers
                        for i, header in enumerate(headers):
                            try:
                                if i >= len(cells):
                                    break

                                cell = cells[i]
                                cell_text = cell.get_text(strip=True)

                                # Clean up header name for dict key
                                key = header.lower().replace(" ", "_")

                                # Parse based on header type
                                if header == "Quest Name":
                                    quest["name"] = cell_text
                                elif header == "Quest Text":
                                    quest["description"] = cell_text
                                elif header == "Provided By":
                                    quest["provider"] = cell_text
                                elif header == "Requirements":
                                    quest["requirements"] = cell_text
                                elif header == "Rewards":
                                    # Try to parse rewards (gold, items, etc.)
                                    quest["rewards"] = cell_text
                                elif header == "Prerequisites":
                                    quest["prerequisites"] = cell_text
                                elif header == "Maximum Timeframe":
                                    quest["timeframe"] = cell_text
                                else:
                                    quest[key] = cell_text
                            except Exception as e:
                                logger.debug(f"Quest {page_title}: Failed to parse cell: {e}")
                                continue

                        # Only add quest if it has a name
                        if "name" in quest and quest["name"]:
                            if quest_type == "story_quests":
                                data["story_quests"].append(quest)
                            elif quest_type == "special_orders":
                                data["special_orders"].append(quest)
                            elif quest_type == "qi_special_orders":
                                data["qi_special_orders"].append(quest)
                    except Exception as e:
                        logger.debug(f"Quest {page_title}: Failed to parse row: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Quest {page_title}: Failed to parse table: {e}")
                continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract quest data: {str(e)}")
        logger.warning(f"Quest {page_title}: Quest extraction failed - {e}")

    return data


def parse_achievement_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Extract structured data for achievements from the Achievements page.

    The Achievements page contains a table listing all achievements with:
    - Achievement name
    - Description (requirements to unlock)
    - Unlocks (in-game rewards)

    Args:
        soup: BeautifulSoup object of the page HTML
        page_title: Name of the page (should be "Achievements")

    Returns:
        Dictionary with list of achievements
    """
    data = {
        "type": "achievements",
        "name": page_title,
        "achievements": [],
        "parsing_warnings": []
    }

    # Find all wikitables
    try:
        tables = soup.find_all("table", class_="wikitable")

        if not tables:
            return data

        # The first table should be the achievements list
        achievements_table = tables[0]
        rows = achievements_table.find_all("tr")

        if len(rows) < 2:  # Need header + at least one data row
            return data

        # Get headers
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

        if not headers or "Achievement" not in headers:
            return data

        # Find column indices
        achievement_idx = headers.index("Achievement") if "Achievement" in headers else None
        description_idx = headers.index("Description") if "Description" in headers else None
        unlocks_idx = headers.index("Unlocks") if "Unlocks" in headers else None

        # Parse achievement rows
        for row_idx in range(1, len(rows)):
            try:
                row = rows[row_idx]
                cells = row.find_all(["td"])

                if len(cells) < len(headers):
                    continue

                achievement = {}

                # Extract achievement name
                try:
                    if achievement_idx is not None and achievement_idx < len(cells):
                        name = cells[achievement_idx].get_text(strip=True)
                        if name:
                            achievement["name"] = name
                except Exception as e:
                    logger.debug(f"Achievement {page_title}: Failed to parse name: {e}")

                # Extract description/requirements
                try:
                    if description_idx is not None and description_idx < len(cells):
                        description = cells[description_idx].get_text(strip=True)
                        if description:
                            achievement["description"] = description
                except Exception as e:
                    logger.debug(f"Achievement {page_title}: Failed to parse description: {e}")

                # Extract unlocks/rewards
                try:
                    if unlocks_idx is not None and unlocks_idx < len(cells):
                        unlocks = cells[unlocks_idx].get_text(strip=True)
                        if unlocks:
                            achievement["unlocks"] = unlocks
                except Exception as e:
                    logger.debug(f"Achievement {page_title}: Failed to parse unlocks: {e}")

                # Only add achievement if it has a name
                if "name" in achievement:
                    data["achievements"].append(achievement)
            except Exception as e:
                logger.debug(f"Achievement {page_title}: Failed to parse row: {e}")
                continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract achievement data: {str(e)}")
        logger.warning(f"Achievement {page_title}: Achievement extraction failed - {e}")

    return data


def parse_collection_list(soup: BeautifulSoup, page_title: str, collection_type: str) -> dict[str, Any]:
    """
    Extract structured data for collection list pages (Artifacts, Minerals, etc.).

    These pages contain tables listing all items in a collection with details like
    name, description, sell price, and location.

    Args:
        soup: BeautifulSoup object of the page HTML
        page_title: Name of the page (e.g., "Artifacts", "Minerals")
        collection_type: Type of collection (artifact, mineral, etc.)

    Returns:
        Dictionary with list of collection items
    """
    data = {
        "type": collection_type,
        "name": page_title,
        "items": [],
        "parsing_warnings": []
    }

    # Find all wikitables
    try:
        tables = soup.find_all("table", class_="wikitable")

        if not tables:
            return data

        # Process each table (Minerals page has multiple tables for different types)
        for table in tables:
            try:
                rows = table.find_all("tr")

                if len(rows) < 2:  # Need header + at least one data row
                    continue

                # Get headers
                header_row = rows[0]
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

                if not headers or "Name" not in headers:
                    continue

                # Find column indices
                name_idx = headers.index("Name") if "Name" in headers else None
                description_idx = headers.index("Description") if "Description" in headers else None
                sell_price_idx = headers.index("Sell Price") if "Sell Price" in headers else None
                location_idx = headers.index("Location") if "Location" in headers else None

                # Parse item rows
                for row_idx in range(1, len(rows)):
                    try:
                        row = rows[row_idx]
                        cells = row.find_all(["td"])

                        if len(cells) < len(headers):
                            continue

                        item = {}

                        # Extract item name
                        try:
                            if name_idx is not None and name_idx < len(cells):
                                name = cells[name_idx].get_text(strip=True)
                                if name:
                                    item["name"] = name
                        except Exception as e:
                            logger.debug(f"Collection {page_title}: Failed to parse name: {e}")

                        # Extract description
                        try:
                            if description_idx is not None and description_idx < len(cells):
                                description = cells[description_idx].get_text(strip=True)
                                if description:
                                    item["description"] = description
                        except Exception as e:
                            logger.debug(f"Collection {page_title}: Failed to parse description: {e}")

                        # Extract sell price
                        try:
                            if sell_price_idx is not None and sell_price_idx < len(cells):
                                price_text = cells[sell_price_idx].get_text(strip=True)
                                # Try to parse price (format: "100g" or "100")
                                price_match = re.search(r'(\d+)', price_text.replace(',', ''))
                                if price_match:
                                    item["sell_price"] = int(price_match.group(1))
                        except Exception as e:
                            logger.debug(f"Collection {page_title}: Failed to parse price: {e}")

                        # Extract location (for artifacts)
                        try:
                            if location_idx is not None and location_idx < len(cells):
                                location = cells[location_idx].get_text(strip=True)
                                if location:
                                    item["location"] = location
                        except Exception as e:
                            logger.debug(f"Collection {page_title}: Failed to parse location: {e}")

                        # Only add item if it has a name
                        if "name" in item:
                            data["items"].append(item)
                    except Exception as e:
                        logger.debug(f"Collection {page_title}: Failed to parse row: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Collection {page_title}: Failed to parse table: {e}")
                continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract collection data: {str(e)}")
        logger.warning(f"Collection {page_title}: Collection extraction failed - {e}")

    return data


def parse_generic_item(soup: BeautifulSoup, page_title: str, item_type: str) -> dict[str, Any]:
    """
    Generic parser for items that don't fit other categories.

    Extracts basic information from the infobox.
    """
    data = {
        "type": item_type,
        "name": page_title,
        "parsing_warnings": []
    }

    # Find the infobox (usually a table with class 'infobox')
    # For items, it's often the first table on the page without a class
    try:
        infobox = soup.find("table", class_="infobox")
        if not infobox:
            # Try the first table on the page
            tables = soup.find_all("table")
            if tables:
                infobox = tables[0]

        if infobox:
            for row in infobox.find_all("tr"):
                try:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)

                        # Store key-value pairs
                        # Sanitize key to be a valid dict key
                        clean_key = re.sub(r'[^\w\s]', '', key).lower().replace(' ', '_')
                        if clean_key:
                            try:
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
                            except Exception as e:
                                logger.debug(f"Generic item {page_title}: Failed to parse field '{clean_key}': {e}")
                                data[clean_key] = value  # Store raw value as fallback
                except Exception as e:
                    logger.debug(f"Generic item {page_title}: Failed to parse infobox row: {e}")
                    continue
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract infobox data: {str(e)}")
        logger.warning(f"Generic item {page_title}: Infobox extraction failed - {e}")

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

        # Call the wiki client with smart search
        result = wiki_client.smart_search(query, limit)

        # Format the response for Claude
        if result["success"]:
            # Build a readable text response
            response_lines = [
                f"Found {result['count']} results for '{query}':\n"
            ]

            # Show which search strategy worked (if different from original query)
            if "strategy_used" in result and result["strategy_used"] != query:
                response_lines.append(f"(Using search term: '{result['strategy_used']}')\n")

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
