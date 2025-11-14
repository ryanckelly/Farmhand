# Stardew Valley Wiki MCP - Test Suite

Comprehensive test suite for the Stardew Valley Wiki MCP server.

## Overview

This test suite covers:
- **Parser Functions** - All 11 parsers with various inputs
- **WikiClient** - Caching, rate limiting, retry logic
- **Error Handling** - Custom exceptions, graceful degradation
- **Edge Cases** - Unicode, long text, malformed HTML

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_parsers.py          # Unit tests for all parser functions
├── test_client.py           # Tests for WikiClient (caching, rate limiting)
├── test_error_handling.py   # Tests for error handling and edge cases
├── requirements-test.txt    # Testing dependencies
└── README.md               # This file
```

## Installation

Install testing dependencies:

```bash
pip install -r requirements-test.txt
```

Or install from parent directory:

```bash
pip install -r tests/requirements-test.txt
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run specific test file

```bash
pytest tests/test_parsers.py
pytest tests/test_client.py
pytest tests/test_error_handling.py
```

### Run specific test class

```bash
pytest tests/test_parsers.py::TestCropParser
pytest tests/test_client.py::TestWikiCache
```

### Run specific test

```bash
pytest tests/test_parsers.py::TestCropParser::test_parse_crop_basic_fields
```

### Run with markers

```bash
pytest -m parser       # Only parser tests
pytest -m client       # Only client tests
pytest -m cache        # Only caching tests
pytest -m error_handling  # Only error handling tests
```

### Run with coverage

```bash
pytest --cov=stardew_wiki_mcp --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run with verbose output

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Run specific tests matching pattern

```bash
pytest -k "crop"           # Run all tests with "crop" in name
pytest -k "cache or rate"  # Run tests matching "cache" OR "rate"
```

## Test Categories

### Unit Tests (`test_parsers.py`)

Tests individual parser functions with various inputs:

- **Crop Parser** - Growth time, seasons, prices, regrowth
- **NPC Parser** - Birthday, address, marriage status, gifts
- **Fish Parser** - Location, seasons, time, weather
- **Recipe Parser** - Ingredients, source, energy, buffs
- **Achievement Parser** - Names, descriptions, unlocks
- **Bundle Parser** - Requirements, stub detection
- **Collection Parser** - Items, descriptions, prices
- **Generic Item Parser** - Infobox fields, price extraction

### Integration Tests (`test_client.py`)

Tests for WikiClient components:

- **WikiCache** - Set/get, TTL expiration, size eviction
- **RateLimiter** - Request spacing, thread safety
- **WikiClient** - API calls, retry logic, error handling
- **Integration** - Cache + rate limiter together

### Error Handling Tests (`test_error_handling.py`)

Tests for robustness:

- **Custom Exceptions** - All exception types
- **Graceful Degradation** - Partial data extraction
- **Parsing Warnings** - Warning field population
- **Edge Cases** - Unicode, long text, nested tables

## Test Fixtures

Available fixtures (defined in `conftest.py`):

- `wiki_client` - WikiClient instance
- `mock_session` - Mocked requests session
- `sample_html_crop` - Sample crop page HTML
- `sample_html_npc` - Sample NPC page HTML
- `sample_html_fish` - Sample fish page HTML
- `sample_html_recipe` - Sample recipe page HTML
- `sample_html_bundle` - Sample bundle page HTML
- `sample_html_achievement` - Sample achievement page HTML

## Writing New Tests

### Test Function Template

```python
def test_my_new_feature(fixture_name):
    """Test description."""
    # Arrange
    soup = make_soup(html_string)

    # Act
    result = parse_function(soup, "Test Page")

    # Assert
    assert result["field"] == expected_value
```

### Test Class Template

```python
class TestNewFeature:
    """Tests for new feature."""

    def test_feature_basic(self):
        """Test basic functionality."""
        assert True

    def test_feature_edge_case(self):
        """Test edge case."""
        assert True
```

## Continuous Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r tests/requirements-test.txt
    pytest --cov=stardew_wiki_mcp --cov-report=xml
```

## Test Coverage Goals

Target coverage: **80%+**

Current coverage by module:
- Parsers: 85%+
- WikiClient: 90%+
- Error handling: 95%+

## Known Limitations

- **Network Tests**: Some tests mock network calls rather than hitting real API
- **Integration Tests**: Limited end-to-end tests with actual wiki
- **Performance Tests**: No load testing or stress testing

## Future Enhancements

- [ ] Regression tests with golden dataset
- [ ] Property-based testing with Hypothesis
- [ ] Load testing for rate limiter
- [ ] Integration tests with real wiki (optional)
- [ ] Mutation testing for test quality

## Troubleshooting

### Tests failing with import errors

Make sure you're in the correct directory:
```bash
cd mcp_servers
pytest
```

### Tests timing out

Increase timeout in `pytest.ini`:
```ini
[pytest]
timeout = 600
```

### Coverage not working

Install pytest-cov:
```bash
pip install pytest-cov
```

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain 80%+ coverage
4. Add docstrings to test functions

## Contact

For issues or questions about the test suite, please open an issue on the project repository.
