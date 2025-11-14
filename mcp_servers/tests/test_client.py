"""
Tests for WikiClient class (caching, rate limiting, retry logic).
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stardew_wiki_mcp import (
    WikiClient,
    WikiCache,
    RateLimiter,
    NetworkError,
    PageNotFoundError,
)


# =============================================================================
# WIKICACHE TESTS
# =============================================================================

class TestWikiCache:
    """Tests for WikiCache class."""

    def test_cache_init(self):
        """Test cache initialization with default values."""
        cache = WikiCache()

        assert cache.ttl_seconds == 3600
        assert cache.max_size == 100
        assert cache.hits == 0
        assert cache.misses == 0

    def test_cache_init_custom_values(self):
        """Test cache initialization with custom values."""
        cache = WikiCache(ttl_seconds=1800, max_size=50)

        assert cache.ttl_seconds == 1800
        assert cache.max_size == 50

    def test_cache_set_and_get(self):
        """Test setting and getting values from cache."""
        cache = WikiCache()

        cache.set("test_key", "test_value")
        result = cache.get("test_key")

        assert result == "test_value"
        assert cache.hits == 1
        assert cache.misses == 0

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = WikiCache()

        result = cache.get("nonexistent_key")

        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1

    def test_cache_case_insensitive(self):
        """Test cache keys are case-insensitive."""
        cache = WikiCache()

        cache.set("TestKey", "value1")
        result = cache.get("testkey")

        assert result == "value1"

    def test_cache_ttl_expiration(self):
        """Test cache entries expire after TTL."""
        cache = WikiCache(ttl_seconds=1)

        cache.set("test_key", "test_value")

        # Should get value immediately
        result1 = cache.get("test_key")
        assert result1 == "test_value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        result2 = cache.get("test_key")
        assert result2 is None

    def test_cache_max_size_eviction(self):
        """Test cache evicts oldest entry when max size reached."""
        cache = WikiCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # All three should be in cache
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        # Adding 4th key should evict key1 (oldest)
        cache.set("key4", "value4")

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_cache_get_stats(self):
        """Test cache statistics reporting."""
        cache = WikiCache(ttl_seconds=3600, max_size=100)

        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate_percent"] == 50.0
        assert stats["ttl_seconds"] == 3600
        assert stats["max_size"] == 100


# =============================================================================
# RATELIMITER TESTS
# =============================================================================

class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_rate_limiter_init(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_second=5.0)

        assert limiter.requests_per_second == 5.0
        assert limiter.min_interval == 0.2

    def test_rate_limiter_no_wait_first_request(self):
        """Test first request does not wait."""
        limiter = RateLimiter(requests_per_second=2.0)

        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # First request should be immediate (< 50ms)
        assert elapsed < 0.05

    def test_rate_limiter_enforces_limit(self):
        """Test rate limiter enforces request rate."""
        limiter = RateLimiter(requests_per_second=2.0)  # 500ms between requests

        start = time.time()

        limiter.wait_if_needed()  # First request - immediate
        limiter.wait_if_needed()  # Second request - should wait ~500ms

        elapsed = time.time() - start

        # Should take at least 450ms (allowing some timing variance)
        assert elapsed >= 0.45

    def test_rate_limiter_multiple_requests(self):
        """Test rate limiter with multiple sequential requests."""
        limiter = RateLimiter(requests_per_second=4.0)  # 250ms between requests

        start = time.time()

        for _ in range(3):
            limiter.wait_if_needed()

        elapsed = time.time() - start

        # 3 requests at 4 req/s = ~500ms minimum
        assert elapsed >= 0.45


# =============================================================================
# WIKICLIENT TESTS
# =============================================================================

class TestWikiClient:
    """Tests for WikiClient class."""

    def test_client_init(self):
        """Test WikiClient initialization."""
        client = WikiClient("https://test.wiki/api.php")

        assert client.api_url == "https://test.wiki/api.php"
        assert isinstance(client.cache, WikiCache)
        assert isinstance(client.rate_limiter, RateLimiter)

    def test_client_init_with_custom_params(self):
        """Test WikiClient with custom cache and rate limit settings."""
        client = WikiClient(
            "https://test.wiki/api.php",
            cache_ttl=1800,
            cache_max_size=50,
            rate_limit=10.0
        )

        assert client.cache.ttl_seconds == 1800
        assert client.cache.max_size == 50
        assert client.rate_limiter.requests_per_second == 10.0

    @patch('requests.Session.get')
    def test_client_search_success(self, mock_get):
        """Test successful search request."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "query": {
                "search": [
                    {"title": "Strawberry", "snippet": "A sweet fruit"}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = WikiClient("https://test.wiki/api.php")
        result = client.search("strawberry", limit=1)

        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Strawberry"

    @patch('requests.Session.get')
    def test_client_get_page_success(self, mock_get):
        """Test successful page fetch."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "parse": {
                "title": "Strawberry",
                "text": {"*": "<html><body>Test HTML</body></html>"},
                "categories": [{"*": "Crops"}]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = WikiClient("https://test.wiki/api.php")
        result = client.get_page("Strawberry")

        assert result["success"] is True
        assert result["page_title"] == "Strawberry"
        assert "html" in result
        assert "categories" in result

    @patch('requests.Session.get')
    def test_client_caching_works(self, mock_get):
        """Test that caching prevents redundant API calls."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "parse": {
                "title": "Strawberry",
                "text": {"*": "<html><body>Test HTML</body></html>"},
                "categories": []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = WikiClient("https://test.wiki/api.php")

        # First call - should hit API
        result1 = client.get_page("Strawberry")
        assert mock_get.call_count == 1

        # Second call - should use cache
        result2 = client.get_page("Strawberry")
        assert mock_get.call_count == 1  # No additional call

        # Both results should be identical
        assert result1 == result2

    @patch('requests.Session.get')
    def test_client_retry_on_timeout(self, mock_get):
        """Test retry logic on timeout."""
        # Mock timeout on first two attempts, success on third
        mock_get.side_effect = [
            requests.exceptions.Timeout("Request timed out"),
            requests.exceptions.Timeout("Request timed out"),
            Mock(json=lambda: {"parse": {"title": "Test", "text": {"*": "<html></html>"}, "categories": []}}, raise_for_status=Mock())
        ]

        client = WikiClient("https://test.wiki/api.php")
        result = client.get_page("Test")

        # Should have retried twice and succeeded on third attempt
        assert mock_get.call_count == 3
        assert result["success"] is True

    @patch('requests.Session.get')
    def test_client_raises_network_error_after_retries(self, mock_get):
        """Test NetworkError raised after exhausting retries."""
        # Mock timeout on all attempts
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        client = WikiClient("https://test.wiki/api.php")

        with pytest.raises(NetworkError):
            client.get_page("Test")

        # Should have tried max_retries times (default: 3)
        assert mock_get.call_count == 3

    @patch('requests.Session.get')
    def test_client_page_not_found(self, mock_get):
        """Test PageNotFoundError on missing page."""
        # Mock empty API response (page doesn't exist)
        mock_response = Mock()
        mock_response.json.return_value = {"parse": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = WikiClient("https://test.wiki/api.php")

        with pytest.raises(PageNotFoundError):
            client.get_page("NonExistentPage")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestWikiClientIntegration:
    """Integration tests combining multiple components."""

    @patch('requests.Session.get')
    def test_cache_and_rate_limit_together(self, mock_get):
        """Test caching and rate limiting work together."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "parse": {
                "title": "Test",
                "text": {"*": "<html></html>"},
                "categories": []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = WikiClient("https://test.wiki/api.php", rate_limit=10.0)

        start = time.time()

        # First call - hits API and rate limiter
        client.get_page("Test1")

        # Second call to same page - uses cache (no rate limit wait)
        client.get_page("Test1")

        # Third call to different page - hits API and rate limiter
        client.get_page("Test2")

        elapsed = time.time() - start

        # Should have only 2 API calls (Test1 cached)
        assert mock_get.call_count == 2

        # Should take at least 100ms (2 requests at 10 req/s = 100ms wait)
        assert elapsed >= 0.08
