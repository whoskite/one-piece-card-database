"""
Unit tests for utility functions.
"""
import os
import sys
import unittest

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.utils import clean_text, extract_card_id_parts, parse_cost


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_clean_text(self):
        """Test the clean_text function."""
        # Test with extra whitespace
        self.assertEqual(clean_text("  Hello  World  "), "Hello World")
        
        # Test with newlines
        self.assertEqual(clean_text("Hello\nWorld"), "Hello World")
        
        # Test with tabs
        self.assertEqual(clean_text("Hello\tWorld"), "Hello World")
        
        # Test with None
        self.assertEqual(clean_text(None), "")
        
        # Test with empty string
        self.assertEqual(clean_text(""), "")
    
    def test_extract_card_id_parts(self):
        """Test the extract_card_id_parts function."""
        # Test with standard card ID
        self.assertEqual(extract_card_id_parts("OP01-001 SR"), ("OP01", "001", "SR"))
        
        # Test with no rarity
        self.assertEqual(extract_card_id_parts("OP01-001"), ("OP01", "001", ""))
        
        # Test with different set code
        self.assertEqual(extract_card_id_parts("ST01-001 C"), ("ST01", "001", "C"))
        
        # Test with invalid format
        self.assertEqual(extract_card_id_parts("Invalid"), ("", "", ""))
    
    def test_parse_cost(self):
        """Test the parse_cost function."""
        # Test with numeric cost
        self.assertEqual(parse_cost("5"), 5)
        
        # Test with whitespace
        self.assertEqual(parse_cost(" 10 "), 10)
        
        # Test with dash
        self.assertEqual(parse_cost("-"), None)
        
        # Test with None
        self.assertEqual(parse_cost(None), None)
        
        # Test with empty string
        self.assertEqual(parse_cost(""), None)
        
        # Test with non-numeric string
        self.assertEqual(parse_cost("X"), None)


if __name__ == "__main__":
    unittest.main()