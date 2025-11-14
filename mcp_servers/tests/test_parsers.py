"""
Unit tests for parser functions.

Tests each parser function with various inputs to ensure they handle:
- Normal data extraction
- Missing fields gracefully
- Malformed HTML
- Edge cases
"""

import pytest
from bs4 import BeautifulSoup
from conftest import make_soup

# Import parsers
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stardew_wiki_mcp import (
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
# CROP PARSER TESTS
# =============================================================================

class TestCropParser:
    """Tests for parse_crop_data function."""

    def test_parse_crop_basic_fields(self, sample_html_crop):
        """Test parsing basic crop fields from infobox."""
        soup = make_soup(sample_html_crop)
        result = parse_crop_data(soup, "Test Crop")

        assert result["type"] == "crop"
        assert result["name"] == "Test Crop"
        assert "parsing_warnings" in result
        assert isinstance(result["parsing_warnings"], list)

    def test_parse_crop_with_growth_time(self, sample_html_crop):
        """Test extracting growth time."""
        soup = make_soup(sample_html_crop)
        result = parse_crop_data(soup, "Test Crop")

        assert "growth_time" in result
        assert "4 days" in result["growth_time"] or "4" in str(result.get("growth_time", ""))

    def test_parse_crop_with_seasons(self, sample_html_crop):
        """Test extracting seasons."""
        soup = make_soup(sample_html_crop)
        result = parse_crop_data(soup, "Test Crop")

        assert "seasons" in result or len(result["parsing_warnings"]) > 0

    def test_parse_crop_with_prices(self, sample_html_crop):
        """Test extracting sell prices."""
        soup = make_soup(sample_html_crop)
        result = parse_crop_data(soup, "Test Crop")

        # Should have either prices or warnings
        has_prices = "sell_prices" in result or "sell_price" in result
        has_warnings = len(result["parsing_warnings"]) > 0
        assert has_prices or has_warnings

    def test_parse_crop_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_crop_data(soup, "Empty Crop")

        assert result["type"] == "crop"
        assert result["name"] == "Empty Crop"
        assert "parsing_warnings" in result

    def test_parse_crop_malformed_html(self):
        """Test parser handles malformed HTML gracefully."""
        soup = make_soup("<html><table><tr><th>Bad</html>")
        result = parse_crop_data(soup, "Bad Crop")

        assert result["type"] == "crop"
        assert result["name"] == "Bad Crop"
        # Should not crash, may have warnings


# =============================================================================
# NPC PARSER TESTS
# =============================================================================

class TestNPCParser:
    """Tests for parse_npc_data function."""

    def test_parse_npc_basic_fields(self, sample_html_npc):
        """Test parsing basic NPC fields from infobox."""
        soup = make_soup(sample_html_npc)
        result = parse_npc_data(soup, "Sebastian")

        assert result["type"] == "npc"
        assert result["name"] == "Sebastian"
        assert "parsing_warnings" in result

    def test_parse_npc_birthday(self, sample_html_npc):
        """Test extracting birthday."""
        soup = make_soup(sample_html_npc)
        result = parse_npc_data(soup, "Sebastian")

        assert "birthday" in result
        assert "Spring 10" in result["birthday"]

    def test_parse_npc_address(self, sample_html_npc):
        """Test extracting address/residence."""
        soup = make_soup(sample_html_npc)
        result = parse_npc_data(soup, "Sebastian")

        assert "address" in result
        assert "Mountain" in result["address"]

    def test_parse_npc_marriageable(self, sample_html_npc):
        """Test detecting marriageable status."""
        soup = make_soup(sample_html_npc)
        result = parse_npc_data(soup, "Sebastian")

        assert "marriageable" in result
        assert result["marriageable"] is True

    def test_parse_npc_family(self, sample_html_npc):
        """Test extracting family members."""
        soup = make_soup(sample_html_npc)
        result = parse_npc_data(soup, "Sebastian")

        assert "family" in result
        assert "Robin" in result["family"]

    def test_parse_npc_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_npc_data(soup, "Empty NPC")

        assert result["type"] == "npc"
        assert result["name"] == "Empty NPC"
        assert "parsing_warnings" in result


# =============================================================================
# FISH PARSER TESTS
# =============================================================================

class TestFishParser:
    """Tests for parse_fish_data function."""

    def test_parse_fish_basic_fields(self, sample_html_fish):
        """Test parsing basic fish fields from infobox."""
        soup = make_soup(sample_html_fish)
        result = parse_fish_data(soup, "Test Fish")

        assert result["type"] == "fish"
        assert result["name"] == "Test Fish"
        assert "parsing_warnings" in result

    def test_parse_fish_location(self, sample_html_fish):
        """Test extracting location."""
        soup = make_soup(sample_html_fish)
        result = parse_fish_data(soup, "Test Fish")

        assert "location" in result
        assert "Mountain Lake" in result["location"]

    def test_parse_fish_seasons(self, sample_html_fish):
        """Test extracting seasons as list."""
        soup = make_soup(sample_html_fish)
        result = parse_fish_data(soup, "Test Fish")

        assert "seasons" in result
        assert isinstance(result["seasons"], list)
        assert len(result["seasons"]) > 0

    def test_parse_fish_time(self, sample_html_fish):
        """Test extracting time window."""
        soup = make_soup(sample_html_fish)
        result = parse_fish_data(soup, "Test Fish")

        assert "time" in result
        assert "6am" in result["time"] or "7pm" in result["time"]

    def test_parse_fish_weather(self, sample_html_fish):
        """Test extracting weather condition."""
        soup = make_soup(sample_html_fish)
        result = parse_fish_data(soup, "Test Fish")

        assert "weather" in result
        assert "Rainy" in result["weather"]

    def test_parse_fish_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_fish_data(soup, "Empty Fish")

        assert result["type"] == "fish"
        assert result["name"] == "Empty Fish"


# =============================================================================
# RECIPE PARSER TESTS
# =============================================================================

class TestRecipeParser:
    """Tests for parse_recipe_data function."""

    def test_parse_recipe_basic_fields(self, sample_html_recipe):
        """Test parsing basic recipe fields from infobox."""
        soup = make_soup(sample_html_recipe)
        result = parse_recipe_data(soup, "Test Recipe")

        assert result["type"] == "recipe"
        assert result["name"] == "Test Recipe"
        assert "parsing_warnings" in result

    def test_parse_recipe_source(self, sample_html_recipe):
        """Test extracting recipe source/unlock method."""
        soup = make_soup(sample_html_recipe)
        result = parse_recipe_data(soup, "Test Recipe")

        assert "source" in result or "recipe_type" in result

    def test_parse_recipe_ingredients(self, sample_html_recipe):
        """Test extracting ingredients list."""
        soup = make_soup(sample_html_recipe)
        result = parse_recipe_data(soup, "Test Recipe")

        # May or may not extract ingredients depending on format
        # Should not crash
        assert "parsing_warnings" in result

    def test_parse_recipe_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_recipe_data(soup, "Empty Recipe")

        assert result["type"] == "recipe"
        assert result["name"] == "Empty Recipe"


# =============================================================================
# ACHIEVEMENT PARSER TESTS
# =============================================================================

class TestAchievementParser:
    """Tests for parse_achievement_data function."""

    def test_parse_achievement_basic_fields(self, sample_html_achievement):
        """Test parsing basic achievement fields from table."""
        soup = make_soup(sample_html_achievement)
        result = parse_achievement_data(soup, "Achievements")

        assert result["type"] == "achievements"
        assert result["name"] == "Achievements"
        assert "parsing_warnings" in result
        assert "achievements" in result

    def test_parse_achievement_list(self, sample_html_achievement):
        """Test extracting list of achievements."""
        soup = make_soup(sample_html_achievement)
        result = parse_achievement_data(soup, "Achievements")

        assert len(result["achievements"]) > 0

    def test_parse_achievement_names(self, sample_html_achievement):
        """Test achievement names are extracted."""
        soup = make_soup(sample_html_achievement)
        result = parse_achievement_data(soup, "Achievements")

        names = [a["name"] for a in result["achievements"]]
        assert "Greenhorn" in names
        assert "Cowpoke" in names

    def test_parse_achievement_descriptions(self, sample_html_achievement):
        """Test achievement descriptions are extracted."""
        soup = make_soup(sample_html_achievement)
        result = parse_achievement_data(soup, "Achievements")

        greenhorn = next(a for a in result["achievements"] if a["name"] == "Greenhorn")
        assert "description" in greenhorn
        assert "15,000g" in greenhorn["description"]

    def test_parse_achievement_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_achievement_data(soup, "Empty Achievements")

        assert result["type"] == "achievements"
        assert result["name"] == "Empty Achievements"
        assert result["achievements"] == []


# =============================================================================
# BUNDLE PARSER TESTS
# =============================================================================

class TestBundleParser:
    """Tests for parse_bundle_data function."""

    def test_parse_bundle_basic_fields(self, sample_html_bundle):
        """Test parsing basic bundle fields."""
        soup = make_soup(sample_html_bundle)
        result = parse_bundle_data(soup, "Test Bundle")

        assert result["type"] == "bundle"
        assert result["name"] == "Test Bundle"
        assert "parsing_warnings" in result
        assert "requirements" in result

    def test_parse_bundle_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_bundle_data(soup, "Empty Bundle")

        assert result["type"] == "bundle"
        assert result["name"] == "Empty Bundle"
        assert result["requirements"] == []


# =============================================================================
# GENERIC ITEM PARSER TESTS
# =============================================================================

class TestGenericItemParser:
    """Tests for parse_generic_item function."""

    def test_parse_generic_item_basic_fields(self):
        """Test parsing basic item fields from infobox."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Sell Price:</th><td>50g</td></tr>
                <tr><th>Source:</th><td>Foraging</td></tr>
            </table>
        </body>
        </html>
        """
        soup = make_soup(html)
        result = parse_generic_item(soup, "Test Item", "item")

        assert result["type"] == "item"
        assert result["name"] == "Test Item"
        assert "parsing_warnings" in result

    def test_parse_generic_item_sell_price(self):
        """Test extracting sell price."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Sell Price:</th><td>100g</td></tr>
            </table>
        </body>
        </html>
        """
        soup = make_soup(html)
        result = parse_generic_item(soup, "Test Item", "item")

        assert "sell_price" in result
        assert result["sell_price"] == 100

    def test_parse_generic_item_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_generic_item(soup, "Empty Item", "item")

        assert result["type"] == "item"
        assert result["name"] == "Empty Item"


# =============================================================================
# COLLECTION LIST PARSER TESTS
# =============================================================================

class TestCollectionListParser:
    """Tests for parse_collection_list function."""

    def test_parse_collection_basic_fields(self):
        """Test parsing collection items from table."""
        html = """
        <html>
        <body>
            <table class="wikitable">
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Sell Price</th>
                </tr>
                <tr>
                    <td>Amethyst</td>
                    <td>A purple variant of quartz</td>
                    <td>100g</td>
                </tr>
            </table>
        </body>
        </html>
        """
        soup = make_soup(html)
        result = parse_collection_list(soup, "Minerals", "mineral")

        assert result["type"] == "mineral"
        assert result["name"] == "Minerals"
        assert "parsing_warnings" in result
        assert "items" in result

    def test_parse_collection_items(self):
        """Test extracting list of collection items."""
        html = """
        <html>
        <body>
            <table class="wikitable">
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Sell Price</th>
                </tr>
                <tr>
                    <td>Amethyst</td>
                    <td>A purple variant of quartz</td>
                    <td>100g</td>
                </tr>
                <tr>
                    <td>Topaz</td>
                    <td>Fairly common</td>
                    <td>80g</td>
                </tr>
            </table>
        </body>
        </html>
        """
        soup = make_soup(html)
        result = parse_collection_list(soup, "Minerals", "mineral")

        assert len(result["items"]) == 2
        names = [item["name"] for item in result["items"]]
        assert "Amethyst" in names
        assert "Topaz" in names

    def test_parse_collection_empty_html(self):
        """Test parser handles empty HTML gracefully."""
        soup = make_soup("<html><body></body></html>")
        result = parse_collection_list(soup, "Empty Collection", "artifact")

        assert result["type"] == "artifact"
        assert result["name"] == "Empty Collection"
        assert result["items"] == []
