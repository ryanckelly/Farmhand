"""
Pytest configuration and fixtures for Stardew Valley Wiki MCP tests.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stardew_wiki_mcp import (
    WikiClient,
    WikiCache,
    RateLimiter,
    parse_crop_data,
    parse_npc_data,
    parse_fish_data,
    parse_bundle_data,
    parse_recipe_data,
    parse_skill_data,
    parse_quest_data,
    parse_achievement_data,
    parse_collection_list,
    parse_generic_item,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def wiki_client():
    """Create a WikiClient instance for testing."""
    return WikiClient("https://stardewvalleywiki.com/mediawiki/api.php")


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    with patch('requests.Session') as mock:
        yield mock


@pytest.fixture
def sample_html_crop():
    """Sample HTML for a crop page (simplified)."""
    return """
    <html>
    <body>
        <table class="infobox">
            <tr><th>Growth Time:</th><td>4 days</td></tr>
            <tr><th>Season:</th><td>Spring</td></tr>
            <tr><th>Sell Price:</th><td>50g</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_npc():
    """Sample HTML for an NPC page."""
    return """
    <html>
    <body>
        <table class="infobox">
            <tr><th>Birthday:</th><td>Spring 10</td></tr>
            <tr><th>Lives in:</th><td>The Mountain</td></tr>
            <tr><th>Address:</th><td>24 Mountain Road</td></tr>
            <tr><th>Marriage:</th><td>Yes</td></tr>
            <tr><th>Family:</th><td>Demetrius (Step-Father), Robin (Mother), Maru (Half-Sister)</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_fish():
    """Sample HTML for a fish page."""
    return """
    <html>
    <body>
        <table class="infobox">
            <tr><th>Location:</th><td>Mountain Lake</td></tr>
            <tr><th>Season:</th><td>Spring, Fall</td></tr>
            <tr><th>Time:</th><td>6am-7pm</td></tr>
            <tr><th>Weather:</th><td>Rainy</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_recipe():
    """Sample HTML for a recipe page."""
    return """
    <html>
    <body>
        <table class="infobox">
            <tr><th>Source:</th><td>Cooking Channel (Year 2)</td></tr>
            <tr><th>Ingredients:</th><td>Green Algae (4)</td></tr>
            <tr><th>Energy / Health:</th><td>3315</td></tr>
            <tr><th>Sell Price:</th><td>30g</td></tr>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_bundle():
    """Sample HTML for a bundle page (stub, should fetch from main Bundles page)."""
    return """
    <html>
    <body>
        <p>This is a stub article for Spring Crops Bundle.</p>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_achievement():
    """Sample HTML for achievements page."""
    return """
    <html>
    <body>
        <table class="wikitable">
            <tr>
                <th>Achievement</th>
                <th>Description</th>
                <th>Unlocks</th>
            </tr>
            <tr>
                <td>Greenhorn</td>
                <td>Earn 15,000g</td>
                <td>Nothing</td>
            </tr>
            <tr>
                <td>Cowpoke</td>
                <td>Earn 50,000g</td>
                <td>Nothing</td>
            </tr>
        </table>
    </body>
    </html>
    """


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_soup(html: str) -> BeautifulSoup:
    """Convert HTML string to BeautifulSoup object."""
    return BeautifulSoup(html, 'lxml')
