# Stardew Valley Wiki MCP - Troubleshooting Guide

Common issues and solutions for the Stardew Valley Wiki MCP server.

---

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Page Not Found Errors](#page-not-found-errors)
3. [Parsing Issues](#parsing-issues)
4. [Performance Problems](#performance-problems)
5. [Testing Issues](#testing-issues)
6. [MCP Integration Issues](#mcp-integration-issues)
7. [Development Issues](#development-issues)
8. [Getting More Help](#getting-more-help)

---

## Connection Issues

### Issue: "Failed to connect to wiki"

**Symptoms:**
- Error message: "Failed to connect to https://stardewvalleywiki.com/mediawiki/api.php"
- Requests timeout
- Network errors

**Possible Causes:**
1. No internet connection
2. Wiki is temporarily down
3. Firewall blocking requests
4. Rate limiting (too many requests)

**Solutions:**

**1. Check Internet Connection**
```bash
# Test connectivity
ping stardewvalleywiki.com

# Test API endpoint
curl https://stardewvalleywiki.com/mediawiki/api.php
```

**2. Wait and Retry**
- The server automatically retries 3 times with exponential backoff
- Wait 10-30 seconds and try again
- Wiki may be temporarily overloaded

**3. Check Firewall**
```bash
# If using corporate network, check firewall rules
# May need to whitelist stardewvalleywiki.com
```

**4. Reduce Request Rate**
```python
# Increase delay between requests
client = WikiClient(WIKI_API_URL, rate_limit=2.0)  # Slower rate
```

**5. Enable Debug Mode**
```bash
DEBUG=true python stardew_wiki_mcp.py
```

This will show detailed connection logs to identify the issue.

---

## Page Not Found Errors

### Issue: "Page 'X' not found on the wiki"

**Symptoms:**
- Error: "Page 'X' not found"
- Suggestion to use `search_wiki` first

**Common Causes:**
1. Typo in page title
2. Case-sensitivity mismatch
3. Page doesn't exist
4. Page name changed

**Solutions:**

**1. Use search_wiki First**
```json
// Instead of guessing the exact title
{
  "tool": "search_wiki",
  "query": "strawbery"  // Typo
}
// Returns: "Strawberry" (correct spelling)

// Then use exact title
{
  "tool": "get_page_data",
  "page_title": "Strawberry"  // Correct
}
```

**2. Check Case Sensitivity**
```javascript
// Page titles are case-sensitive
get_page_data({page_title: "strawberry"})  // ❌ Wrong
get_page_data({page_title: "Strawberry"})  // ✅ Correct

get_page_data({page_title: "sebastian"})   // ❌ Wrong
get_page_data({page_title: "Sebastian"})   // ✅ Correct
```

**3. Check for Redirects**
Some pages redirect to others:
```javascript
get_page_data({page_title: "Starfruit"})
// May redirect to "Starfruit (crop)"
// Error message will suggest using the target page
```

**4. Search Wiki Directly**
Visit https://stardewvalleywiki.com and search to find the exact page title.

---

## Parsing Issues

### Issue: "parsing_warnings" in Response

**Symptoms:**
- Data is returned but incomplete
- `parsing_warnings` array contains errors
- Some fields are missing

**Example:**
```json
{
  "type": "crop",
  "name": "Strange Crop",
  "seasons": ["Spring"],
  "parsing_warnings": [
    "Failed to extract growth_time: Missing infobox row",
    "Failed to extract sell_price: Price table not found"
  ]
}
```

**Causes:**
1. Wiki page has unusual format
2. Missing sections on page
3. Recently updated wiki structure
4. Page is incomplete/stub

**Solutions:**

**1. Use Available Data**
- Partial data is still usable
- Check which fields are present
- Handle missing fields gracefully

```javascript
if (data.growth_time !== undefined) {
  console.log(`Growth time: ${data.growth_time} days`);
} else {
  console.log("Growth time not available");
}
```

**2. Check Wiki Page Manually**
- Visit the wiki page directly
- Verify if the data exists
- May need to add information to wiki

**3. Report Persistent Issues**
- If warnings occur for many pages of same type
- May indicate parser needs updating
- Open an issue with page examples

**4. Try Different Page**
- Some pages have better structure than others
- Use main pages rather than variant pages
- Example: "Strawberry" better than "Strawberry Seeds"

### Issue: Wrong Parser Used

**Symptoms:**
- `type` field doesn't match expected
- Data structure is unexpected
- Generic parser used instead of specific

**Example:**
```json
// Expected "crop" type, got "item" type
{
  "type": "item",  // Generic parser used
  "name": "Starfruit"
}
```

**Causes:**
1. Page categories don't match expected type
2. Parser detection logic missed the page
3. Page is categorized differently on wiki

**Solutions:**

**1. Check Page Categories**
The parser selection uses wiki categories:
- Crops pages should have "Crops" category
- NPC pages should have "Villagers" or "NPCs" category
- If miscategorized, generic parser is used

**2. Update Parser Detection**
If many pages are affected, the parser detection logic may need updating.
See CONTRIBUTING.md for how to add category checks.

---

## Performance Problems

### Issue: Slow Response Times

**Symptoms:**
- Requests take >5 seconds
- First request is slow, subsequent requests fast
- Intermittent slowness

**Causes:**
1. First request (cache miss)
2. Complex page with large HTML
3. Network latency
4. Wiki server slowness

**Solutions:**

**1. Enable Caching (Already Enabled by Default)**
```python
# Cache is enabled by default with 1-hour TTL
# First request: ~220ms (cache miss)
# Subsequent requests: <1ms (cache hit)
```

**2. Check Cache Statistics**
```python
stats = client.cache.get_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
# High hit rate (>50%) is good
# Low hit rate means you're querying new pages
```

**3. Reduce Rate Limit (If Testing)**
```python
# Only for testing, not production
client = WikiClient(WIKI_API_URL, rate_limit=10.0)  # Faster rate
```

**4. Use Specific Parsers**
- `get_page_data` with specific page faster than `search_wiki`
- Specific parsers faster than generic parser

**5. Batch Related Requests**
```javascript
// Instead of this (sequential)
await get_page_data({page_title: "Strawberry"});
await get_page_data({page_title: "Blueberry"});
await get_page_data({page_title: "Cranberry"});

// Do this (parallel, if supported by your client)
await Promise.all([
  get_page_data({page_title: "Strawberry"}),
  get_page_data({page_title: "Blueberry"}),
  get_page_data({page_title: "Cranberry"})
]);
```

### Issue: Cache Not Working

**Symptoms:**
- Every request takes full time
- Cache hit rate is 0%
- No performance improvement

**Diagnosis:**
```python
# Check if cache is working
client = WikiClient(WIKI_API_URL)

# First request
result1 = client.get_page("Strawberry")
print(f"Request 1 completed")

# Second request (should be cached)
result2 = client.get_page("Strawberry")
print(f"Request 2 completed")

# Check stats
stats = client.cache.get_stats()
print(f"Cache stats: {stats}")
# Should show: hits: 1, misses: 1, hit_rate: 50%
```

**Solutions:**

**1. Check Case Sensitivity**
```python
# Cache keys are case-insensitive, but verify
client.get_page("Strawberry")  # Cache miss
client.get_page("strawberry")  # Should be cache hit (case-insensitive)
```

**2. Check TTL**
```python
# Requests expire after 1 hour by default
# If requests are >1 hour apart, cache won't help

# Increase TTL if needed
client = WikiClient(WIKI_API_URL, cache_ttl=7200)  # 2 hours
```

**3. Check Max Size**
```python
# Cache only stores 100 entries by default
# If you query >100 unique pages, older entries are evicted

# Increase if needed
client = WikiClient(WIKI_API_URL, cache_max_size=500)
```

---

## Testing Issues

### Issue: Tests Failing

**Symptom:**
```
FAILED tests/test_parsers.py::TestCropParser::test_parse_crop_with_growth_time
```

**Common Causes:**

**1. Type Mismatches**
```python
# Test expects string, parser returns int
assert result["growth_time"] == "8 days"  # ❌ Fails

# Fix: Match parser's actual behavior
assert result["growth_time"] == 8  # ✅ Passes
```

**2. Missing Test Dependencies**
```bash
# Install test dependencies
pip install -r tests/requirements-test.txt
```

**3. Import Errors**
```bash
# Run from correct directory
cd mcp_servers
pytest
```

**4. Network Tests**
```python
# Mock network calls in tests
@patch('requests.Session.get')
def test_my_function(mock_get):
    mock_get.return_value = mock_response
    # ...
```

### Issue: Tests Hanging

**Symptom:**
- Tests don't complete
- Timeout errors
- pytest hangs

**Solutions:**

**1. Add Timeouts**
```python
# In pytest.ini
[pytest]
timeout = 300  # 5 minutes max per test
```

**2. Mock Network Calls**
```python
# Don't make real API calls in tests
@patch('requests.Session.get')
def test_something(mock_get):
    # ...
```

**3. Check for Infinite Loops**
```python
# Bad: Can loop forever
while True:
    # ...

# Good: Has exit condition
max_attempts = 10
for attempt in range(max_attempts):
    # ...
```

### Issue: Low Test Coverage

**Symptom:**
```
Coverage: 65% (below 80% target)
```

**Solutions:**

**1. Identify Uncovered Lines**
```bash
pytest --cov=stardew_wiki_mcp --cov-report=html
# Open htmlcov/index.html to see uncovered lines
```

**2. Add Edge Case Tests**
- Empty HTML
- Malformed data
- Missing fields
- Unicode characters

**3. Test Error Paths**
```python
def test_parser_with_missing_infobox():
    html = "<html><body></body></html>"
    result = parse_data(html, "Test")
    assert "parsing_warnings" in result
    assert len(result["parsing_warnings"]) > 0
```

---

## MCP Integration Issues

### Issue: "MCP server not responding"

**Symptoms:**
- Claude can't connect to server
- Server starts but tools don't work
- Connection timeout

**Solutions:**

**1. Check Server is Running**
```bash
# Start server manually
python stardew_wiki_mcp.py

# Should see:
# [INFO] Stardew Valley Wiki MCP server started
```

**2. Check MCP Configuration**
```json
// In Claude's MCP settings
{
  "mcpServers": {
    "stardew-wiki": {
      "command": "python",
      "args": ["path/to/stardew_wiki_mcp.py"]
    }
  }
}
```

**3. Check Python Path**
```bash
# Verify Python is in PATH
python --version

# Or use full path
/usr/bin/python3 stardew_wiki_mcp.py
```

**4. Check Dependencies**
```bash
# Install required packages
pip install requests beautifulsoup4 lxml mcp
```

**5. Check Logs**
```bash
# Enable debug mode
DEBUG=true python stardew_wiki_mcp.py

# Check stderr output for errors
```

### Issue: "Tool not found"

**Symptoms:**
- Error: "Tool 'search_wiki' not found"
- Tools aren't registered

**Solutions:**

**1. Verify Server Started Correctly**
```bash
python stardew_wiki_mcp.py
# Should register tools during startup
```

**2. Check Tool Names**
```javascript
// Correct tool names
search_wiki        // ✅
get_page_data      // ✅

// Wrong names
searchWiki         // ❌
getPageData        // ❌
search-wiki        // ❌
```

**3. Restart MCP Connection**
- Disconnect and reconnect Claude
- Restart Claude Code
- Restart MCP server

---

## Development Issues

### Issue: "Module not found" errors

**Symptom:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
# Install dependencies
pip install requests beautifulsoup4 lxml mcp

# Or from requirements file (if available)
pip install -r requirements.txt
```

### Issue: BeautifulSoup warnings

**Symptom:**
```
UserWarning: No parser was explicitly specified
```

**Solution:**
```python
# Always specify parser
soup = BeautifulSoup(html, 'lxml')  # ✅

# Not this
soup = BeautifulSoup(html)  # ❌
```

### Issue: Linting errors

**Symptom:**
```
pylint: E1101: Instance of 'Tag' has no 'find' member
```

**Solution:**
```python
# Add type hints to help linter
def parse_data(soup: BeautifulSoup, title: str) -> dict[str, Any]:
    # ...

# Or disable specific warnings
# pylint: disable=no-member
```

### Issue: Import errors in tests

**Symptom:**
```
ImportError: cannot import name 'parse_crop_data' from 'stardew_wiki_mcp'
```

**Solution:**
```bash
# Run tests from correct directory
cd mcp_servers
pytest

# Or set PYTHONPATH
export PYTHONPATH=/path/to/mcp_servers
pytest
```

---

## Common Error Messages

### "Page 'X' not found"
**Meaning:** Wiki page doesn't exist or title is incorrect
**Solution:** Use `search_wiki` to find correct title

### "Failed to connect to wiki"
**Meaning:** Network connection failed
**Solution:** Check internet connection, wait and retry

### "Failed to parse page 'X'"
**Meaning:** Parser couldn't extract data
**Solution:** Check `parsing_warnings`, use available data

### "Page 'X' redirects to 'Y'"
**Meaning:** Page is a redirect
**Solution:** Use target page 'Y' instead

### "Rate limit exceeded"
**Meaning:** Too many requests too fast (unlikely with rate limiting)
**Solution:** Wait 10-30 seconds, reduce request rate

### "Cache is full"
**Meaning:** Cache has reached max size (100 entries default)
**Solution:** Increase `cache_max_size` or let eviction happen

### "parsing_warnings: [...]"
**Meaning:** Some data couldn't be extracted
**Solution:** Use available data, check wiki page manually

---

## Debugging Techniques

### Enable Debug Logging

```bash
DEBUG=true python stardew_wiki_mcp.py
```

**Shows:**
- All API calls
- Parsing steps
- Cache hits/misses
- Rate limiting delays
- Error details

### Inspect HTML

```python
from stardew_wiki_mcp import WikiClient, WIKI_API_URL
from bs4 import BeautifulSoup

client = WikiClient(WIKI_API_URL)
result = client.get_page("Strawberry")

# Get raw HTML
html = result.get("raw_html")  # If included
soup = BeautifulSoup(html, 'lxml')

# Inspect structure
print(soup.prettify())

# Find specific elements
infobox = soup.find('table', class_='infobox')
print(infobox)
```

### Test Individual Parsers

```python
from stardew_wiki_mcp import parse_crop_data
from bs4 import BeautifulSoup

# Minimal test HTML
html = """
<table class="infobox">
    <tr><th>Growth Time:</th><td>8 days</td></tr>
</table>
"""

soup = BeautifulSoup(html, 'lxml')
result = parse_crop_data(soup, "Test Crop")
print(result)
```

### Check Cache State

```python
client = WikiClient(WIKI_API_URL)

# Make some requests
client.get_page("Strawberry")
client.get_page("Blueberry")

# Check cache
stats = client.cache.get_stats()
print(f"Size: {stats['size']}")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate_percent']}%")
```

### Measure Performance

```python
import time

client = WikiClient(WIKI_API_URL)

# First request (cache miss)
start = time.time()
result1 = client.get_page("Strawberry")
elapsed1 = time.time() - start
print(f"First request: {elapsed1:.3f}s")

# Second request (cache hit)
start = time.time()
result2 = client.get_page("Strawberry")
elapsed2 = time.time() - start
print(f"Second request: {elapsed2:.3f}s")

# Compare
speedup = elapsed1 / elapsed2
print(f"Speedup: {speedup:.0f}x faster")
```

---

## Performance Benchmarks

### Expected Response Times

| Operation | First Request | Cached Request |
|-----------|--------------|----------------|
| `search_wiki` | 200-300ms | <1ms |
| `get_page_data` (simple) | 220ms | <1ms |
| `get_page_data` (complex) | 350ms | <1ms |

**If slower than this:**
- Check network connection
- Check wiki server status
- Verify rate limiting isn't too restrictive

### Memory Usage

**Typical Memory Usage:**
- Server startup: ~30MB
- Per cached page: ~50KB
- 100 cached pages: ~35MB total

**If higher:**
- Check for memory leaks
- Verify cache eviction working
- Reduce `cache_max_size`

---

## Getting More Help

### Documentation

- **API_REFERENCE.md** - Tool usage and parameters
- **PARSER_COVERAGE.md** - Parser capabilities
- **CONTRIBUTING.md** - Development guidelines
- **tests/README.md** - Test suite documentation

### Wiki Resources

- **Stardew Valley Wiki:** https://stardewvalleywiki.com
- **MediaWiki API:** https://www.mediawiki.org/wiki/API:Main_page
- **Wiki API Sandbox:** https://stardewvalleywiki.com/mediawiki/api.php

### Reporting Issues

**Before opening an issue:**
1. Check this troubleshooting guide
2. Search existing issues
3. Try with DEBUG=true
4. Gather error messages and logs

**Include in issue report:**
- Error message (full text)
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version
- Relevant code snippet
- Debug logs (if applicable)

**Issue Template:**
```markdown
## Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Message
```
Full error text here
```

## Environment
- Python version: 3.x
- OS: Windows/Mac/Linux
- Dependencies: (output of `pip list`)

## Debug Logs (if applicable)
```
DEBUG=true output here
```
```

### Community

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and ideas
- **Wiki Talk Pages:** For wiki-specific questions

---

## FAQ

**Q: Why am I getting "Page not found" for a page that exists?**
A: Page titles are case-sensitive and must match exactly. Use `search_wiki` first.

**Q: Why is the first request slow but subsequent requests fast?**
A: Caching. First request hits the API (~220ms), subsequent requests use cache (<1ms).

**Q: Can I disable caching?**
A: Not recommended, but you can set `cache_ttl=0` to disable.

**Q: Can I increase the rate limit?**
A: Yes, but be respectful of the wiki. Use `rate_limit` parameter (default: 5 req/s).

**Q: Why are some fields missing from the response?**
A: Wiki pages vary in completeness. Check `parsing_warnings` for details.

**Q: How do I add support for a new page type?**
A: See CONTRIBUTING.md for step-by-step guide to adding parsers.

**Q: Can I use this for other wikis?**
A: Yes, change `WIKI_API_URL`. Parsers may need adjustment for different wiki structures.

**Q: Is there a rate limit?**
A: Yes, 5 requests/second by default. MediaWiki wikis typically allow 10-20 req/s.

**Q: How long are pages cached?**
A: 1 hour by default. Configurable with `cache_ttl` parameter.

**Q: What if the wiki structure changes?**
A: Parsers include graceful degradation. Check `parsing_warnings` and report persistent issues.

---

## Still Stuck?

If this guide doesn't solve your problem:

1. **Check existing issues** on GitHub
2. **Open a new issue** with detailed information
3. **Use DEBUG mode** to gather more information
4. **Include reproduction steps** in your report

We're here to help! 🎮

---

## Quick Reference

### Enable Debug Mode
```bash
DEBUG=true python stardew_wiki_mcp.py
```

### Check Cache Stats
```python
stats = client.cache.get_stats()
print(stats)
```

### Test Connection
```bash
curl https://stardewvalleywiki.com/mediawiki/api.php
```

### Run Tests
```bash
cd mcp_servers && pytest
```

### Inspect Parsing
```python
result = client.get_page("PageName")
if result.get("parsing_warnings"):
    print(f"Warnings: {result['parsing_warnings']}")
```

---

## See Also

- **API_REFERENCE.md** - Complete API documentation
- **PARSER_COVERAGE.md** - What each parser extracts
- **CONTRIBUTING.md** - Development and contribution guidelines
