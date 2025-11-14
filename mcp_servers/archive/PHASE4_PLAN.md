# Phase 4: Production Deployment Plan

**Goal**: Make the Stardew Valley Wiki MCP server production-ready with robust error handling, performance optimizations, comprehensive testing, and documentation.

**Estimated Time**: 8-12 hours
**Current Status**: Phase 3 Complete (97.4% parser quality, 95.8% search quality)

---

## Overview

Phase 4 focuses on production readiness:
1. **Error Handling** - Graceful degradation and better error messages
2. **Performance** - Caching and rate limiting
3. **Testing** - Comprehensive test suite
4. **Documentation** - API reference and guides

---

## 4.1 Error Handling (2-3 hours)

### Current Issues
- Parser failures don't provide helpful error messages
- No retry logic for API failures
- Missing data fields fail silently
- Network errors crash the server

### Goals

#### 4.1.1 Graceful Degradation
**What**: Return partial data instead of failing completely
**Why**: Better user experience when wiki pages are incomplete

**Implementation**:
1. Wrap each parser section in try-except blocks
2. Continue parsing even if one section fails
3. Include `parsing_warnings` field in response
4. Log which fields failed to parse

**Example**:
```python
def parse_crop(html, title):
    result = {"type": "crop", "name": title, "parsing_warnings": []}

    try:
        result["seasons"] = extract_seasons(html)
    except Exception as e:
        result["parsing_warnings"].append(f"Failed to extract seasons: {str(e)}")
        logger.warning(f"Crop {title}: seasons extraction failed - {e}")

    try:
        result["growth_time"] = extract_growth_time(html)
    except Exception as e:
        result["parsing_warnings"].append(f"Failed to extract growth_time: {str(e)}")
        logger.warning(f"Crop {title}: growth_time extraction failed - {e}")

    return result
```

#### 4.1.2 Better Error Messages
**What**: Provide actionable error messages to users
**Why**: Help users understand what went wrong and how to fix it

**Error Categories**:
1. **Page Not Found** - "Page 'X' does not exist on the wiki. Try searching first."
2. **Network Error** - "Failed to connect to wiki. Check internet connection."
3. **Parse Error** - "Found page but couldn't extract data. Page may have unusual format."
4. **Redirect** - "Page 'X' redirects to 'Y'. Use 'Y' instead."
5. **Disambiguation** - "Multiple pages found for 'X'. Be more specific."

**Implementation**:
```python
class WikiError(Exception):
    """Base exception for wiki operations"""
    pass

class PageNotFoundError(WikiError):
    """Page doesn't exist"""
    def __init__(self, page_title):
        self.page_title = page_title
        super().__init__(f"Page '{page_title}' not found. Try searching first with search_wiki tool.")

class NetworkError(WikiError):
    """Network connection failed"""
    def __init__(self, url, original_error):
        self.url = url
        self.original_error = original_error
        super().__init__(f"Failed to connect to {url}: {original_error}")
```

#### 4.1.3 Retry Logic
**What**: Automatically retry failed API requests
**Why**: Handle temporary network issues and wiki throttling

**Implementation**:
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, backoff_factor=2):
    """Decorator to retry failed requests with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        raise NetworkError(str(args), e)

                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Request failed (attempt {attempt+1}/{max_retries}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)

        return wrapper
    return decorator

# Apply to API methods
@retry_on_failure(max_retries=3, backoff_factor=2)
def _make_api_request(self, params):
    response = requests.get(self.api_url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Deliverables
- [ ] Graceful degradation for all parsers
- [ ] Custom exception classes with helpful messages
- [ ] Retry logic with exponential backoff
- [ ] Parsing warnings in response JSON
- [ ] Comprehensive error logging

---

## 4.2 Performance Optimization (2-3 hours)

### Current Performance
- Average response time: ~220ms per page
- No caching (repeated queries refetch data)
- No rate limiting (could get throttled by wiki)

### Goals

#### 4.2.1 Page Caching
**What**: Cache wiki pages in memory to avoid repeated fetches
**Why**: Reduce API calls and improve response time

**Implementation**:
```python
import time
from functools import lru_cache
from datetime import datetime, timedelta

class WikiCache:
    """Simple in-memory cache with TTL"""
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                # Expired, remove
                del self.cache[key]
        return None

    def set(self, key, value):
        """Cache value with timestamp"""
        self.cache[key] = (value, datetime.now())

    def clear(self):
        """Clear all cached data"""
        self.cache.clear()

# Add to WikiClient
class WikiClient:
    def __init__(self, api_url, cache_ttl=3600):
        self.api_url = api_url
        self.cache = WikiCache(ttl_seconds=cache_ttl)

    def get_page(self, title):
        # Check cache first
        cached = self.cache.get(title)
        if cached:
            logger.info(f"Cache hit for '{title}'")
            return cached

        # Fetch from API
        logger.info(f"Cache miss for '{title}', fetching from API")
        result = self._fetch_page(title)

        # Cache successful results
        if result["success"]:
            self.cache.set(title, result)

        return result
```

**Cache Configuration**:
- Default TTL: 1 hour (wiki pages rarely change)
- Max cache size: 100 pages (prevent memory bloat)
- Cache key: Page title (case-insensitive)

#### 4.2.2 Rate Limiting
**What**: Limit API requests per second to avoid throttling
**Why**: Be a good citizen, avoid getting IP banned

**Implementation**:
```python
import time
import threading

class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    def __init__(self, requests_per_second=5):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0
        self.lock = threading.Lock()

    def wait(self):
        """Wait if necessary to respect rate limit"""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request

            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                time.sleep(wait_time)

            self.last_request = time.time()

# Add to WikiClient
class WikiClient:
    def __init__(self, api_url, rate_limit=5):
        self.api_url = api_url
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit)

    def _make_api_request(self, params):
        self.rate_limiter.wait()  # Wait if necessary
        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
```

**Rate Limit Configuration**:
- Default: 5 requests/second (conservative)
- MediaWiki typical limit: 10-20 requests/second
- User-configurable via environment variable

#### 4.2.3 Request Batching (Optional)
**What**: Combine multiple page requests into one API call
**Why**: Reduce total API calls for bulk operations

**Note**: MediaWiki API supports fetching multiple pages at once. Deferred to Phase 5 (not critical for current use case).

### Deliverables
- [ ] In-memory page cache with TTL
- [ ] Rate limiter for API requests
- [ ] Cache statistics logging
- [ ] Environment variable configuration

---

## 4.3 Testing Suite (3-4 hours)

### Current Testing
- Comprehensive parser tests (38 test cases)
- Search preprocessing tests (24 test cases)
- No unit tests for individual functions
- No integration tests for MCP protocol
- No regression tests

### Goals

#### 4.3.1 Unit Tests
**What**: Test individual parser functions in isolation
**Why**: Catch bugs early, enable confident refactoring

**Test Coverage**:
1. **WikiClient Methods**
   - `search()` - API search
   - `get_page()` - Page fetching
   - `smart_search()` - Query preprocessing

2. **Parser Functions**
   - `detect_page_type()` - Type detection
   - `parse_crop()`, `parse_fish()`, etc. - Individual parsers
   - `preprocess_query()` - Query preprocessing

3. **Utility Functions**
   - `extract_price()` - Price parsing
   - `clean_html()` - HTML cleaning
   - `extract_table_data()` - Table extraction

**Framework**: pytest (standard Python testing)

**Example Unit Test**:
```python
import pytest
from stardew_wiki_mcp import detect_page_type

def test_detect_page_type_crop():
    """Test crop detection by categories"""
    categories = ["Crops", "Spring Crops"]
    assert detect_page_type("Parsnip", categories) == "crop"

def test_detect_page_type_fish():
    """Test fish detection by categories"""
    categories = ["Fish"]
    assert detect_page_type("Catfish", categories) == "fish"

def test_detect_page_type_exact_title():
    """Test exact title match takes priority"""
    categories = ["Achievements"]  # Would normally detect as achievement
    assert detect_page_type("Quests", categories) == "quests"  # Exact title wins
```

#### 4.3.2 Integration Tests
**What**: Test MCP protocol end-to-end
**Why**: Ensure tools work correctly when called by Claude

**Test Coverage**:
1. **MCP Server Initialization**
   - Server starts without errors
   - Tools are registered correctly
   - Logging is configured

2. **Tool Invocation**
   - `search_wiki` returns proper format
   - `get_page_data` returns structured JSON
   - Error handling works end-to-end

3. **Error Scenarios**
   - Invalid page names
   - Network failures
   - Malformed HTML

**Framework**: MCP test harness (if available) or custom test client

**Example Integration Test**:
```python
import json
from stardew_wiki_mcp import call_tool

def test_search_wiki_tool():
    """Test search_wiki tool returns proper format"""
    arguments = {"query": "sebastian", "limit": 5}
    result = call_tool("search_wiki", arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Sebastian" in result[0].text

def test_get_page_data_tool_crop():
    """Test get_page_data returns crop data"""
    arguments = {"page_title": "Parsnip"}
    result = call_tool("get_page_data", arguments)

    data = json.loads(result[0].text)
    assert data["type"] == "crop"
    assert "seasons" in data
    assert "growth_time" in data
```

#### 4.3.3 Regression Tests
**What**: Automated tests to detect wiki structure changes
**Why**: Wiki pages get updated, parsers may break

**Strategy**:
1. **Golden Dataset** - Save known-good parser outputs
2. **Periodic Checks** - Re-run tests weekly
3. **Diff Analysis** - Compare current vs. golden outputs
4. **Alert on Changes** - Flag when parser results change

**Example Regression Test**:
```python
import json
import pytest

# Load golden dataset
with open("test_data/golden_outputs.json") as f:
    GOLDEN_OUTPUTS = json.load(f)

@pytest.mark.parametrize("page_title,expected", GOLDEN_OUTPUTS.items())
def test_parser_regression(page_title, expected):
    """Test that parser output matches golden dataset"""
    result = get_page_data(page_title)

    # Compare key fields (allow some flexibility for changing data)
    assert result["type"] == expected["type"]
    assert set(result.keys()) == set(expected.keys())  # Same fields

    # Check field types match
    for key in result:
        assert type(result[key]) == type(expected[key])
```

#### 4.3.4 Test Organization
```
mcp_servers/
  tests/
    test_wiki_client.py      # Unit tests for WikiClient
    test_parsers.py          # Unit tests for parsers
    test_preprocessing.py    # Unit tests for query preprocessing
    test_integration.py      # Integration tests for MCP tools
    test_regression.py       # Regression tests
    test_data/
      golden_outputs.json    # Known-good parser outputs
      sample_pages/          # Saved HTML for offline testing
```

### Deliverables
- [ ] pytest test suite (50+ unit tests)
- [ ] Integration tests for MCP tools
- [ ] Regression test framework
- [ ] Golden dataset for regression testing
- [ ] Test documentation

---

## 4.4 Documentation (2-3 hours)

### Current Documentation
- README.md - User guide
- roadmap.md - Development plan
- Phase completion reports

### Goals

#### 4.4.1 API Reference
**What**: Complete reference for all tools and parameters
**Why**: Users need to know exact capabilities

**Content**:
```markdown
## Tool: search_wiki

Search the Stardew Valley Wiki for pages matching a query.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Search query (supports natural language) |
| limit | integer | No | 10 | Maximum results to return (1-50) |

### Returns

Text response with:
- Number of results found
- Search strategy used (if different from query)
- List of matching pages with titles, snippets, URLs

### Examples

**Example 1: NPC Gift Query**
```json
{
  "query": "what does sebastian like",
  "limit": 5
}
```
Returns: Sebastian page with gift preferences

**Example 2: Seasonal Query**
```json
{
  "query": "spring birthdays",
  "limit": 10
}
```
Returns: Calendar page with all birthdays

### Error Handling

- Empty query → Error message
- No results found → "No results found for '{query}'"
- Network error → Retry with exponential backoff

---

## Tool: get_page_data

Extract structured data from a specific wiki page.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page_title | string | Yes | - | Exact page title (case-sensitive) |

### Returns

JSON object with structured data. Schema depends on page type:

**Crops**:
```json
{
  "type": "crop",
  "name": "Parsnip",
  "seasons": ["Spring"],
  "growth_time": 4,
  "regrowth_time": null,
  "sell_prices": {
    "base": 35,
    "silver": 43,
    "gold": 52,
    "iridium": 70
  }
}
```

**Fish**:
```json
{
  "type": "fish",
  "name": "Catfish",
  "location": "River (Town and Forest)",
  "seasons": ["Spring", "Fall"],
  "time": "6am-12am",
  "weather": "Rain"
}
```

... (continue for all 12 parsers)

### Error Handling

- Page not found → "Page 'X' does not exist"
- Parse error → Return partial data with `parsing_warnings`
- Network error → Retry with exponential backoff
```

#### 4.4.2 Parser Coverage Matrix
**What**: Table showing what data each parser extracts
**Why**: Users need to know capabilities and limitations

**Content**:
```markdown
## Parser Coverage Matrix

| Category | Supported | Fields Extracted | Pass Rate | Limitations |
|----------|-----------|------------------|-----------|-------------|
| Crops | ✅ Yes | seasons, growth_time, regrowth_time, sell_prices | 100% | - |
| Fish | ✅ Yes | location, time, seasons, weather | 80% | Crab pot catches missing location |
| Bundles | ✅ Yes | requirements (items, quantities) | 100% | - |
| NPCs | ✅ Yes | loved_gifts, heart_events, marriageable, address, family, birthday | 100% | Schedules not supported |
| Recipes | ✅ Yes | ingredients, buffs, energy, source, recipe_type, products | 100% | - |
| Skills | ✅ Yes | levels, professions, recipes_unlocked | 100% | XP requirements not extracted |
| Quests | ✅ Yes | story_quests, special_orders, help_wanted | 100% | - |
| Achievements | ✅ Yes | achievements (name, description) | 100% | - |
| Monsters | ✅ Yes | base_hp, base_damage, defense, speed, xp, drops, locations | 100% | - |
| Animals | ✅ Yes | building, purchase_price, produce | 100% | - |
| Collections | ✅ Yes | items (name, description, location, sell_price) | 100% | - |
| Items (Generic) | ✅ Yes | source, sell_price, purchase_price | 100% | Fallback parser |
```

#### 4.4.3 Contributing Guide
**What**: Instructions for adding new parsers
**Why**: Enable community contributions

**Content**:
```markdown
## Contributing a New Parser

### Step 1: Identify Wiki Structure

1. Find example pages for your category
2. Inspect the HTML using browser DevTools
3. Identify common patterns (infoboxes, tables, lists)

### Step 2: Write Parser Function

```python
def parse_YOUR_CATEGORY(html: str, title: str) -> dict:
    \"\"\"
    Parse YOUR_CATEGORY pages.

    Args:
        html: Page HTML
        title: Page title

    Returns:
        Dictionary with extracted data
    \"\"\"
    soup = BeautifulSoup(html, 'lxml')
    result = {
        "type": "YOUR_CATEGORY",
        "name": title,
        "parsing_warnings": []
    }

    # Extract field 1
    try:
        result["field1"] = extract_field1(soup)
    except Exception as e:
        result["parsing_warnings"].append(f"Failed to extract field1: {e}")

    return result
```

### Step 3: Add to detect_page_type()

```python
def detect_page_type(title: str, categories: list[str]) -> str:
    # Add your category detection
    if any("your_category" in c.lower() for c in categories):
        return "YOUR_CATEGORY"
```

### Step 4: Add to parse_page_data()

```python
def parse_page_data(html, title, categories):
    page_type = detect_page_type(title, categories)

    if page_type == "YOUR_CATEGORY":
        return parse_YOUR_CATEGORY(html, title)
```

### Step 5: Write Tests

```python
def test_YOUR_CATEGORY_parser():
    result = get_page_data("Example Page")
    assert result["type"] == "YOUR_CATEGORY"
    assert "field1" in result
```

### Step 6: Update Documentation

- Add to Parser Coverage Matrix
- Add to README.md examples
- Add to API reference
```

#### 4.4.4 Troubleshooting Guide
**What**: Common issues and solutions
**Why**: Help users debug problems

**Content**:
```markdown
## Troubleshooting Guide

### Issue: "Page not found" error

**Symptoms**: `get_page_data` returns error
**Causes**:
1. Typo in page name
2. Page doesn't exist on wiki
3. Page was renamed

**Solutions**:
1. Use `search_wiki` first to find exact page name
2. Check spelling and capitalization
3. Search wiki directly to verify page exists

---

### Issue: Missing data fields

**Symptoms**: Parser returns data but missing expected fields
**Causes**:
1. Wiki page has different structure
2. Data not available on wiki
3. Parser bug

**Solutions**:
1. Check `parsing_warnings` field for details
2. Compare wiki page to successful examples
3. Report issue with page name and missing field

---

### Issue: Slow response times

**Symptoms**: Queries take >2 seconds
**Causes**:
1. First query (not cached)
2. Network latency
3. Wiki server slow

**Solutions**:
1. Subsequent queries will be faster (cached)
2. Check internet connection
3. Wait and retry

---

### Issue: "Rate limited" error

**Symptoms**: Multiple requests fail with 429 error
**Causes**:
1. Too many requests too quickly

**Solutions**:
1. Wait 60 seconds and retry
2. Reduce request frequency
3. Built-in rate limiter prevents this (check configuration)
```

### Deliverables
- [ ] Complete API reference
- [ ] Parser coverage matrix
- [ ] Contributing guide
- [ ] Troubleshooting guide
- [ ] Updated README with examples

---

## Implementation Order

Recommended sequence:

1. **Error Handling** (Day 1)
   - Implement graceful degradation
   - Add custom exceptions
   - Add retry logic

2. **Performance** (Day 1-2)
   - Implement caching
   - Add rate limiter
   - Test performance improvements

3. **Testing** (Day 2-3)
   - Write unit tests
   - Create integration tests
   - Build regression framework

4. **Documentation** (Day 3-4)
   - API reference
   - Coverage matrix
   - Contributing guide
   - Troubleshooting guide

---

## Success Criteria

Phase 4 is complete when:

- [x] Error handling: All parsers have graceful degradation
- [x] Error handling: Custom exceptions with helpful messages
- [x] Error handling: Retry logic implemented
- [x] Performance: Page caching working
- [x] Performance: Rate limiter preventing throttling
- [x] Testing: 80%+ code coverage with unit tests
- [x] Testing: Integration tests for both MCP tools
- [x] Testing: Regression test framework in place
- [x] Documentation: Complete API reference
- [x] Documentation: Parser coverage matrix
- [x] Documentation: Contributing guide
- [x] Documentation: Troubleshooting guide

---

## Estimated Timeline

| Task | Time | Cumulative |
|------|------|------------|
| 4.1 Error Handling | 2-3 hours | 2-3 hours |
| 4.2 Performance | 2-3 hours | 4-6 hours |
| 4.3 Testing | 3-4 hours | 7-10 hours |
| 4.4 Documentation | 2-3 hours | 9-13 hours |

**Total**: 9-13 hours (2-3 development sessions)

---

## Phase 4 Deliverables Checklist

### Code Changes
- [ ] Custom exception classes
- [ ] Graceful degradation in all parsers
- [ ] Retry logic with exponential backoff
- [ ] WikiCache class
- [ ] RateLimiter class
- [ ] Unit test suite (50+ tests)
- [ ] Integration tests
- [ ] Regression test framework

### Documentation
- [ ] API_REFERENCE.md
- [ ] PARSER_COVERAGE.md
- [ ] CONTRIBUTING.md
- [ ] TROUBLESHOOTING.md
- [ ] Updated README.md

### Quality Gates
- [ ] 80%+ code coverage
- [ ] All integration tests passing
- [ ] Performance improvement (cache hit rate >50%)
- [ ] Zero production errors in smoke testing

---

## Next Steps After Phase 4

Once Phase 4 is complete, the MCP server is **production-ready** and can be:
- Released to the community
- Deployed in production environments
- Used as reference for other MCP servers

**Optional Phase 5** (Advanced Features):
- Fuzzy search matching
- Data enrichment (profit calculations)
- Real-time wiki change notifications
