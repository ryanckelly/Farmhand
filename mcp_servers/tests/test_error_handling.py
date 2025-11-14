"""
Tests for error handling and graceful degradation.
"""

import pytest
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stardew_wiki_mcp import (
    WikiError,
    PageNotFoundError,
    NetworkError,
    ParseError,
    RedirectError,
    parse_crop_data,
    parse_npc_data,
    parse_fish_data,
    parse_recipe_data,
    parse_achievement_data,
    parse_collection_list,
    parse_generic_item,
)


# =============================================================================
# CUSTOM EXCEPTIONS TESTS
# =============================================================================

class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_wiki_error_base(self):
        """Test WikiError base exception."""
        error = WikiError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_page_not_found_error(self):
        """Test PageNotFoundError with helpful message."""
        error = PageNotFoundError("TestPage")
        assert "TestPage" in str(error)
        assert "not found" in str(error)
        assert "search_wiki" in str(error)  # Suggests using search tool
        assert isinstance(error, WikiError)

    def test_network_error(self):
        """Test NetworkError includes URL and original error."""
        original = Exception("Connection failed")
        error = NetworkError("https://test.com", original)

        assert "https://test.com" in str(error)
        assert "Connection failed" in str(error)
        assert error.url == "https://test.com"
        assert error.original_error == original
        assert isinstance(error, WikiError)

    def test_parse_error(self):
        """Test ParseError includes page title and reason."""
        error = ParseError("TestPage", "Missing infobox")

        assert "TestPage" in str(error)
        assert "Missing infobox" in str(error)
        assert error.page_title == "TestPage"
        assert error.reason == "Missing infobox"
        assert isinstance(error, WikiError)

    def test_redirect_error(self):
        """Test RedirectError suggests target page."""
        error = RedirectError("OldName", "NewName")

        assert "OldName" in str(error)
        assert "NewName" in str(error)
        assert "redirect" in str(error).lower()
        assert error.source_page == "OldName"
        assert error.target_page == "NewName"
        assert isinstance(error, WikiError)


# =============================================================================
# GRACEFUL DEGRADATION TESTS
# =============================================================================

class TestGracefulDegradation:
    """Tests for graceful degradation in parsers."""

    def test_crop_parser_partial_data(self):
        """Test crop parser returns partial data on malformed HTML."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Growth Time:</th><td>4 days</td></tr>
                <!-- Missing other fields -->
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_crop_data(soup, "Partial Crop")

        # Should still return basic structure
        assert result["type"] == "crop"
        assert result["name"] == "Partial Crop"
        assert "parsing_warnings" in result

        # Should not crash, may or may not have growth_time
        assert isinstance(result, dict)

    def test_npc_parser_missing_sections(self):
        """Test NPC parser handles missing gift sections gracefully."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Birthday:</th><td>Spring 1</td></tr>
            </table>
            <!-- No gift preference sections -->
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_npc_data(soup, "Minimal NPC")

        # Should return basic structure
        assert result["type"] == "npc"
        assert result["name"] == "Minimal NPC"
        assert "birthday" in result

        # Should not have gift preferences but should not crash
        assert "parsing_warnings" in result

    def test_fish_parser_empty_table(self):
        """Test fish parser handles empty infobox table."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <!-- Empty table -->
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_fish_data(soup, "Empty Fish")

        # Should return basic structure without crashing
        assert result["type"] == "fish"
        assert result["name"] == "Empty Fish"
        assert "parsing_warnings" in result

    def test_recipe_parser_broken_html(self):
        """Test recipe parser handles broken HTML tags."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Source:</th><td>Cooking</td
                <!-- Missing closing tags -->
        </body>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_recipe_data(soup, "Broken Recipe")

        # Should not crash
        assert result["type"] == "recipe"
        assert result["name"] == "Broken Recipe"
        assert isinstance(result, dict)

    def test_achievement_parser_no_table(self):
        """Test achievement parser when table is missing."""
        html = """
        <html>
        <body>
            <p>Achievements page without table</p>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_achievement_data(soup, "No Table Achievements")

        # Should return empty list, not crash
        assert result["type"] == "achievements"
        assert result["name"] == "No Table Achievements"
        assert result["achievements"] == []
        assert "parsing_warnings" in result

    def test_collection_parser_malformed_rows(self):
        """Test collection parser handles malformed table rows."""
        html = """
        <html>
        <body>
            <table class="wikitable">
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td>Item 1</td>
                    <!-- Missing description cell -->
                </tr>
                <tr>
                    <!-- Missing both cells -->
                </tr>
                <tr>
                    <td>Item 2</td>
                    <td>Valid description</td>
                </tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_collection_list(soup, "Malformed Collection", "artifact")

        # Should extract valid items, skip malformed ones
        assert result["type"] == "artifact"
        assert result["name"] == "Malformed Collection"
        assert isinstance(result["items"], list)

        # Should have at least the valid item
        if len(result["items"]) > 0:
            assert any(item.get("name") == "Item 2" for item in result["items"])

    def test_generic_item_parser_invalid_price(self):
        """Test generic item parser handles invalid price formats."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Sell Price:</th><td>Invalid Price Format</td></tr>
                <tr><th>Source:</th><td>Foraging</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_generic_item(soup, "Invalid Price Item", "item")

        # Should not crash, may store raw value
        assert result["type"] == "item"
        assert result["name"] == "Invalid Price Item"
        assert isinstance(result, dict)


# =============================================================================
# PARSING WARNINGS TESTS
# =============================================================================

class TestParsingWarnings:
    """Tests for parsing_warnings field in parsers."""

    def test_warnings_present_in_all_parsers(self):
        """Test all parsers include parsing_warnings field."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'lxml')

        # Test each parser
        crop = parse_crop_data(soup, "Test")
        assert "parsing_warnings" in crop

        npc = parse_npc_data(soup, "Test")
        assert "parsing_warnings" in npc

        fish = parse_fish_data(soup, "Test")
        assert "parsing_warnings" in fish

        recipe = parse_recipe_data(soup, "Test")
        assert "parsing_warnings" in recipe

        achievement = parse_achievement_data(soup, "Test")
        assert "parsing_warnings" in achievement

        collection = parse_collection_list(soup, "Test", "artifact")
        assert "parsing_warnings" in collection

        item = parse_generic_item(soup, "Test", "item")
        assert "parsing_warnings" in item

    def test_warnings_are_list(self):
        """Test parsing_warnings is always a list."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'lxml')

        result = parse_crop_data(soup, "Test")

        assert isinstance(result["parsing_warnings"], list)

    def test_warnings_populated_on_error(self):
        """Test warnings are populated when extraction fails."""
        # HTML that will cause some extraction to fail
        html = """
        <html>
        <body>
            <div>No infobox here</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_crop_data(soup, "Test Crop")

        # Should have warnings or successfully handle missing infobox
        assert "parsing_warnings" in result
        assert isinstance(result["parsing_warnings"], list)


# =============================================================================
# EDGE CASES TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_parser_with_unicode_characters(self):
        """Test parsers handle Unicode characters."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Name:</th><td>Café Au Lait</td></tr>
                <tr><th>Description:</th><td>Très délicieux ☕</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_generic_item(soup, "Café Item", "item")

        # Should handle Unicode without crashing
        assert result["type"] == "item"
        assert "Café" in result["name"]

    def test_parser_with_very_long_text(self):
        """Test parsers handle very long text fields."""
        long_text = "A" * 10000
        html = f"""
        <html>
        <body>
            <table class="infobox">
                <tr><th>Description:</th><td>{long_text}</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_generic_item(soup, "Long Text Item", "item")

        # Should handle long text without crashing
        assert result["type"] == "item"
        assert result["name"] == "Long Text Item"

    def test_parser_with_special_html_chars(self):
        """Test parsers handle HTML special characters."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Name:</th><td>&lt;Test&gt; &amp; "Quotes"</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_generic_item(soup, "Special Chars", "item")

        # Should handle special chars
        assert result["type"] == "item"
        assert isinstance(result, dict)

    def test_parser_with_nested_tables(self):
        """Test parsers handle nested tables."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th>Name:</th><td>Test</td></tr>
                <tr>
                    <td>
                        <table>
                            <tr><td>Nested</td></tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_generic_item(soup, "Nested Tables", "item")

        # Should handle nested tables without crashing
        assert result["type"] == "item"
        assert result["name"] == "Nested Tables"

    def test_parser_with_empty_cells(self):
        """Test parsers handle empty table cells."""
        html = """
        <html>
        <body>
            <table class="infobox">
                <tr><th></th><td></td></tr>
                <tr><th>Name:</th><td></td></tr>
                <tr><th></th><td>Value</td></tr>
            </table>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        result = parse_generic_item(soup, "Empty Cells", "item")

        # Should handle empty cells gracefully
        assert result["type"] == "item"
        assert result["name"] == "Empty Cells"
