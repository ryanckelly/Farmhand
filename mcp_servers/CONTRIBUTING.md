# Contributing to Stardew Valley Wiki MCP

Thank you for your interest in contributing! This guide will help you add new parsers, improve existing ones, and maintain code quality.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Adding a New Parser](#adding-a-new-parser)
4. [Parser Best Practices](#parser-best-practices)
5. [Testing Guidelines](#testing-guidelines)
6. [Code Style](#code-style)
7. [Pull Request Process](#pull-request-process)
8. [Common Pitfalls](#common-pitfalls)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Basic knowledge of HTML/CSS (for parsing)
- Familiarity with BeautifulSoup
- Understanding of the Stardew Valley Wiki structure

### Project Structure

```
mcp_servers/
├── stardew_wiki_mcp.py      # Main server and all parsers
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_parsers.py      # Parser unit tests
│   ├── test_client.py       # Client tests
│   └── test_error_handling.py  # Error tests
├── API_REFERENCE.md         # Tool documentation
├── PARSER_COVERAGE.md       # Parser capabilities
├── CONTRIBUTING.md          # This file
└── TROUBLESHOOTING.md       # Common issues
```

---

## Development Setup

### 1. Install Dependencies

```bash
pip install requests beautifulsoup4 lxml mcp
```

### 2. Install Test Dependencies

```bash
pip install -r tests/requirements-test.txt
```

### 3. Run Tests

```bash
cd mcp_servers
pytest
```

### 4. Enable Debug Mode

```bash
DEBUG=true python stardew_wiki_mcp.py
```

---

## Adding a New Parser

Follow this step-by-step guide to add a new parser for a specific page type.

### Step 1: Identify the Need

**Good candidates for new parsers:**
- Page type with 10+ similar pages
- Consistent infobox/table structure
- Frequently queried information
- Unique data not covered by generic parser

**Examples:**
- Animals (Cow, Chicken, Goat) - Currently uses generic parser
- Machines (Keg, Preserves Jar) - Could benefit from specialized parser
- Festivals (Egg Festival, Luau) - Special event data

### Step 2: Study the Wiki Structure

**Analyze Sample Pages:**

1. Open 3-5 example pages of the target type
2. Identify common elements:
   - Infobox fields
   - Tables (ingredients, stats, etc.)
   - Sections (descriptions, mechanics)
3. Note variations and edge cases
4. Document expected output structure

**Example Analysis - Animals:**

```
Sample Pages: Cow, Chicken, Goat, Sheep, Pig

Common Elements:
- Infobox with:
  - Purchase Price
  - Produces
  - Produce Sell Price
  - Deluxe Produce (if applicable)
  - Adult Days
  - Building Required
- Description paragraph
- Products section with sell prices

Edge Cases:
- Some animals have deluxe products (Cow → Large Milk)
- Dinosaur is special case
- Pigs find truffles (different mechanic)
```

### Step 3: Write the Parser Function

**Template:**

```python
def parse_animal_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Parse animal-specific data from wiki pages.

    Args:
        soup: BeautifulSoup object of page HTML
        page_title: Name of the wiki page

    Returns:
        Dictionary with structured animal data

    Example pages: Cow, Chicken, Goat, Sheep, Pig, Duck
    """
    # Initialize result with base fields
    data = {
        "type": "animal",
        "name": page_title,
        "parsing_warnings": []
    }

    # Extract infobox data
    try:
        infobox = soup.find('table', class_='infobox')
        if infobox:
            for row in infobox.find_all('tr'):
                try:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        header = th.get_text(strip=True).lower()

                        if 'purchase' in header:
                            price_text = td.get_text(strip=True)
                            data['purchase_price'] = _extract_price(price_text)

                        elif 'produces' in header:
                            data['produces'] = td.get_text(strip=True)

                        elif 'days until' in header or 'adult' in header:
                            days_text = td.get_text(strip=True)
                            data['adult_days'] = _extract_number(days_text)

                        elif 'building' in header:
                            data['building_required'] = td.get_text(strip=True)

                except Exception as e:
                    logger.debug(f"Failed to parse infobox row: {e}")
                    continue

    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract infobox: {str(e)}")
        logger.warning(f"Animal infobox extraction failed for '{page_title}': {e}")

    # Extract product information
    try:
        # Find products section
        products_heading = soup.find(['h2', 'h3'], string=re.compile(r'Products?', re.I))
        if products_heading:
            products_section = products_heading.find_next('table')
            if products_section:
                data['products'] = []
                for row in products_section.find_all('tr')[1:]:  # Skip header
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            product = {
                                'name': cells[0].get_text(strip=True),
                                'sell_price': _extract_price(cells[1].get_text(strip=True))
                            }
                            data['products'].append(product)
                    except Exception as e:
                        logger.debug(f"Failed to parse product row: {e}")
                        continue

    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract products: {str(e)}")
        logger.warning(f"Animal products extraction failed for '{page_title}': {e}")

    # Extract description
    try:
        # Find first paragraph (usually description)
        first_para = soup.find('p')
        if first_para:
            data['description'] = first_para.get_text(strip=True)
    except Exception as e:
        data["parsing_warnings"].append(f"Failed to extract description: {str(e)}")

    return data
```

### Step 4: Add Parser to Type Detection

In `parse_page_data()`, add detection logic:

```python
def parse_page_data(html: str, page_title: str, categories: list[str]) -> dict[str, Any]:
    """Auto-detect page type and use appropriate parser."""

    soup = BeautifulSoup(html, 'lxml')
    logger.debug(f"Parsing page: {page_title}, Categories: {categories}")

    # ... existing checks ...

    # Add new parser check
    if "Animals" in categories or any("Animal" in cat for cat in categories):
        logger.debug(f"Detected animal page: {page_title}")
        return parse_animal_data(soup, page_title)

    # ... rest of checks ...
```

### Step 5: Write Tests

Create comprehensive tests in `tests/test_parsers.py`:

```python
class TestAnimalParser:
    """Tests for parse_animal_data function."""

    def test_parse_animal_basic_fields(self):
        """Test parsing basic animal fields from infobox."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Purchase Price:</th><td>2,500g</td></tr>
                <tr><th>Produces:</th><td>Milk</td></tr>
                <tr><th>Days Until Adult:</th><td>5 days</td></tr>
                <tr><th>Building:</th><td>Barn</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_animal_data(soup, "Cow")

        assert result["type"] == "animal"
        assert result["name"] == "Cow"
        assert result["purchase_price"] == 2500
        assert result["produces"] == "Milk"
        assert result["adult_days"] == 5
        assert result["building_required"] == "Barn"
        assert isinstance(result["parsing_warnings"], list)

    def test_parse_animal_with_products(self):
        """Test extracting product information."""
        html = """
        <html>
        <body>
            <h3>Products</h3>
            <table>
                <tr><th>Product</th><th>Sell Price</th></tr>
                <tr><td>Milk</td><td>125g</td></tr>
                <tr><td>Large Milk</td><td>190g</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_animal_data(soup, "Cow")

        assert "products" in result
        assert len(result["products"]) == 2
        assert result["products"][0]["name"] == "Milk"
        assert result["products"][0]["sell_price"] == 125

    def test_parse_animal_empty_html(self):
        """Test graceful handling of empty HTML."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'lxml')
        result = parse_animal_data(soup, "Unknown Animal")

        assert result["type"] == "animal"
        assert result["name"] == "Unknown Animal"
        assert isinstance(result["parsing_warnings"], list)
        # Should not crash, just return minimal data

    def test_parse_animal_malformed_prices(self):
        """Test handling of malformed price data."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Purchase Price:</th><td>invalid</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_animal_data(soup, "Test Animal")

        # Should not crash, should skip invalid price
        assert result["type"] == "animal"
```

### Step 6: Add Fixture (if needed)

In `tests/conftest.py`, add sample HTML fixture:

```python
@pytest.fixture
def sample_html_animal():
    """Sample HTML for an animal page (simplified)."""
    return """
    <html>
    <body>
        <table class="infobox">
            <tr><th>Purchase Price:</th><td>2,500g</td></tr>
            <tr><th>Produces:</th><td>Milk</td></tr>
            <tr><th>Days Until Adult:</th><td>5 days</td></tr>
            <tr><th>Building:</th><td>Barn</td></tr>
        </table>
        <p>Cows are one of the animals you can purchase at Marnie's Ranch.</p>
        <h3>Products</h3>
        <table>
            <tr><th>Product</th><th>Sell Price</th></tr>
            <tr><td>Milk</td><td>125g</td></tr>
            <tr><td>Large Milk</td><td>190g</td></tr>
        </table>
    </body>
    </html>
    """
```

### Step 7: Update Documentation

**PARSER_COVERAGE.md:**

Add section documenting your new parser:

```markdown
## 12. Animal Parser

**Function:** `parse_animal_data(soup, page_title)`
**Location:** `stardew_wiki_mcp.py:XXXX-YYYY`

### Extracts

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `type` | string | Always "animal" | `"animal"` |
| `name` | string | Animal name | `"Cow"` |
| `purchase_price` | int | Cost to buy | `2500` |
| `produces` | string | Main product | `"Milk"` |
| `adult_days` | int | Days to mature | `5` |
| `building_required` | string | Housing | `"Barn"` |
| `products` | list[dict] | Product details | See below |
| `parsing_warnings` | list[string] | Extraction issues | `[]` |

...
```

**API_REFERENCE.md:**

Update the "Supported Page Types" section with your new type.

### Step 8: Test and Validate

```bash
# Run your new tests
pytest tests/test_parsers.py::TestAnimalParser -v

# Run full test suite
pytest

# Test with real wiki page
python -c "
from stardew_wiki_mcp import WikiClient, WIKI_API_URL
client = WikiClient(WIKI_API_URL)
result = client.get_page('Cow')
print(result)
"
```

---

## Parser Best Practices

### 1. Always Use Graceful Degradation

**DO:**
```python
try:
    # Extract section
    for item in items:
        try:
            # Parse individual item
        except Exception as e:
            logger.debug(f"Failed to parse item: {e}")
            continue  # Skip this item
except Exception as e:
    data["parsing_warnings"].append(f"Failed to extract section: {str(e)}")
```

**DON'T:**
```python
# No error handling - will crash on malformed HTML
infobox = soup.find('table', class_='infobox')
for row in infobox.find_all('tr'):
    data[row.find('th').text] = row.find('td').text
```

### 2. Always Return a Dictionary

**DO:**
```python
def parse_my_data(soup, page_title):
    data = {"type": "my_type", "name": page_title, "parsing_warnings": []}
    # ... extraction logic ...
    return data  # Always returns dict, never None
```

**DON'T:**
```python
def parse_my_data(soup, page_title):
    if not soup.find('table'):
        return None  # BAD - breaks downstream code
    # ...
```

### 3. Include parsing_warnings

**DO:**
```python
data["parsing_warnings"] = []
try:
    # extraction
except Exception as e:
    data["parsing_warnings"].append(f"Failed to extract X: {str(e)}")
```

**DON'T:**
```python
# Silently fail without feedback
try:
    # extraction
except:
    pass  # User has no idea what went wrong
```

### 4. Use Helper Functions

**DO:**
```python
def _extract_price(text: str) -> int:
    """Extract numeric price from text like '2,500g' or '125g'."""
    match = re.search(r'([\d,]+)g?', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

# Use in parser
data['price'] = _extract_price(td.get_text())
```

**DON'T:**
```python
# Duplicate price extraction logic everywhere
price_text = td.get_text()
price = int(price_text.replace('g', '').replace(',', ''))
```

### 5. Handle Case-Insensitivity

**DO:**
```python
header = th.get_text(strip=True).lower()
if 'purchase' in header or 'price' in header:
    # ...
```

**DON'T:**
```python
if th.text == "Purchase Price:":  # Won't match "purchase price" or "Purchase price:"
    # ...
```

### 6. Test Edge Cases

**Always test:**
- Empty HTML: `<html><body></body></html>`
- Missing infobox
- Malformed tables
- Unicode characters
- Very long text
- Nested tables
- Empty cells

### 7. Use Descriptive Logging

**DO:**
```python
logger.debug(f"Parsing animal page: {page_title}")
logger.debug(f"Found {len(products)} products")
logger.warning(f"Failed to extract infobox for '{page_title}': {e}")
```

**DON'T:**
```python
logger.debug("Parsing")  # Not helpful
logger.error(str(e))     # Missing context
```

### 8. Keep Functions Focused

**DO:**
```python
def parse_animal_data(soup, page_title):
    """Main parser."""
    data = _init_data(page_title)
    _extract_infobox(soup, data)
    _extract_products(soup, data)
    return data

def _extract_infobox(soup, data):
    """Helper for infobox."""
    # ...
```

**DON'T:**
```python
def parse_animal_data(soup, page_title):
    # 500 lines of nested extraction logic
```

---

## Testing Guidelines

### Test Structure

Each parser should have:
- **Happy path tests** - Normal, well-formed pages
- **Empty HTML tests** - Graceful degradation
- **Malformed HTML tests** - Robustness
- **Edge case tests** - Unicode, long text, etc.

### Test Naming Convention

```python
def test_parse_X_basic_fields():           # Happy path
def test_parse_X_with_Y():                 # Specific feature
def test_parse_X_empty_html():             # Graceful degradation
def test_parse_X_malformed_Z():            # Error handling
def test_parse_X_edge_case_unicode():      # Edge cases
```

### Coverage Goals

- **Target:** 80%+ code coverage
- **Critical paths:** 100% coverage
- **Error handling:** Fully tested

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_parsers.py

# Specific test class
pytest tests/test_parsers.py::TestAnimalParser

# Specific test
pytest tests/test_parsers.py::TestAnimalParser::test_parse_animal_basic_fields

# With coverage
pytest --cov=stardew_wiki_mcp --cov-report=html

# Verbose output
pytest -vv
```

---

## Code Style

### Python Style

- **PEP 8** compliant
- **Type hints** for function signatures
- **Docstrings** for all public functions
- **4 spaces** for indentation
- **Max line length:** 100 characters

### Documentation

```python
def parse_animal_data(soup: BeautifulSoup, page_title: str) -> dict[str, Any]:
    """
    Parse animal-specific data from wiki pages.

    Extracts information about farm animals including purchase price,
    products, maturation time, and housing requirements.

    Args:
        soup: BeautifulSoup object of the parsed HTML
        page_title: Title of the wiki page being parsed

    Returns:
        Dictionary containing structured animal data with fields:
        - type: Always "animal"
        - name: Animal name
        - purchase_price: Cost to buy
        - produces: Main product
        - adult_days: Days to mature
        - building_required: Housing type
        - products: List of products with prices
        - parsing_warnings: List of any extraction issues

    Example:
        >>> html = "<html>...</html>"
        >>> soup = BeautifulSoup(html, 'lxml')
        >>> data = parse_animal_data(soup, "Cow")
        >>> data["produces"]
        "Milk"

    Example pages: Cow, Chicken, Goat, Sheep, Pig, Duck, Rabbit
    """
```

### Import Organization

```python
# Standard library
import asyncio
import json
import logging
import re
import sys

# Third-party
import requests
from bs4 import BeautifulSoup
from mcp.server import Server
```

### Error Messages

**DO:**
```python
raise PageNotFoundError(f"Page '{page_title}' not found. Try using search_wiki first.")
```

**DON'T:**
```python
raise Exception("Page not found")  # Not helpful
```

---

## Pull Request Process

### 1. Before You Start

- Check existing issues/PRs to avoid duplication
- Open an issue to discuss large changes
- Fork the repository

### 2. Making Changes

```bash
# Create feature branch
git checkout -b feature/add-animal-parser

# Make changes
# ...

# Run tests
pytest

# Run linter (if available)
pylint stardew_wiki_mcp.py
```

### 3. Commit Messages

```
Add animal parser for farm animal pages

- Extracts purchase price, products, maturation time
- Handles Cow, Chicken, Goat, Sheep, Pig, Duck, Rabbit
- Includes comprehensive tests (12 tests)
- Updates documentation (PARSER_COVERAGE.md)

Closes #42
```

### 4. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature (parser)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test coverage improvement

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for changes
- [ ] Tested with real wiki pages

## Documentation
- [ ] Updated API_REFERENCE.md (if applicable)
- [ ] Updated PARSER_COVERAGE.md (if adding parser)
- [ ] Updated CONTRIBUTING.md (if changing process)
- [ ] Added/updated docstrings

## Checklist
- [ ] Code follows project style
- [ ] Tests achieve 80%+ coverage
- [ ] No new warnings from linter
- [ ] Documentation is clear and complete
```

### 5. Review Process

- Maintainer will review within 3-5 days
- Address feedback in follow-up commits
- Once approved, squash and merge

---

## Common Pitfalls

### 1. Not Handling None Returns

**Problem:**
```python
infobox = soup.find('table')
for row in infobox.find_all('tr'):  # Crashes if infobox is None
    # ...
```

**Solution:**
```python
infobox = soup.find('table')
if infobox:
    for row in infobox.find_all('tr'):
        # ...
```

### 2. Hardcoding Page Structure

**Problem:**
```python
price = soup.find_all('td')[3].text  # Fragile - breaks if structure changes
```

**Solution:**
```python
price_cell = soup.find('th', string='Price:').find_next('td')
if price_cell:
    price = price_cell.get_text(strip=True)
```

### 3. Not Testing Edge Cases

**Problem:**
```python
# Only tests happy path, breaks on real wiki
```

**Solution:**
```python
# Test empty HTML, malformed tables, missing fields, Unicode, etc.
```

### 4. Raising Exceptions Instead of Warnings

**Problem:**
```python
if not infobox:
    raise ParseError("Missing infobox")  # Fails entire request
```

**Solution:**
```python
if not infobox:
    data["parsing_warnings"].append("Missing infobox")
    return data  # Returns partial data
```

### 5. Not Using Type Hints

**Problem:**
```python
def parse_data(soup, title):  # Unclear types
    # ...
```

**Solution:**
```python
def parse_data(soup: BeautifulSoup, title: str) -> dict[str, Any]:
    # ...
```

### 6. Ignoring Cache/Rate Limits

**Problem:**
```python
# Making rapid API calls in tests
for i in range(100):
    client.get_page(f"Page{i}")
```

**Solution:**
```python
# Mock API calls in tests
@patch('requests.Session.get')
def test_my_parser(mock_get):
    mock_get.return_value = mock_response
    # ...
```

---

## Getting Help

**Questions?**
- Open an issue with the "question" label
- Review existing documentation
- Check TROUBLESHOOTING.md

**Found a Bug?**
- Open an issue with the "bug" label
- Include minimal reproduction case
- Specify Python version and dependencies

**Want to Discuss?**
- Open an issue with the "discussion" label
- Propose your idea before implementing

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🎉

---

## Quick Checklist

Before submitting a PR:

- [ ] Tests pass: `pytest`
- [ ] New tests added for changes
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] Graceful degradation implemented
- [ ] `parsing_warnings` field included
- [ ] Commit messages are clear
- [ ] PR description is complete

---

## See Also

- **API_REFERENCE.md** - Tool usage and parameters
- **PARSER_COVERAGE.md** - Existing parser capabilities
- **TROUBLESHOOTING.md** - Common issues and solutions
- **tests/README.md** - Test suite documentation
