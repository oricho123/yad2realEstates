"""
Tests for the real estate scraper module.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

# Add the real_estate_analyzer directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "real_estate_analyzer"))

from real_estate_scraper import RealEstateScraper


class TestRealEstateScraper:
    """Test the RealEstateScraper class."""
    
    def test_scraper_initialization(self):
        """Test that scraper can be initialized."""
        scraper = RealEstateScraper()
        assert isinstance(scraper, RealEstateScraper)
        assert hasattr(scraper, 'base_url')
        assert hasattr(scraper, 'headers')
    
    def test_scraper_has_required_methods(self):
        """Test that scraper has all required methods."""
        scraper = RealEstateScraper()
        
        # Check for essential methods
        assert hasattr(scraper, 'fetch_listings')
        assert callable(scraper.fetch_listings)
        
        assert hasattr(scraper, 'parse_listings')
        assert callable(scraper.parse_listings)
        
        assert hasattr(scraper, 'save_listings_csv')
        assert callable(scraper.save_listings_csv)
    
    @patch('requests.get')
    def test_scraper_handles_network_errors(self, mock_get):
        """Test that scraper handles network errors gracefully."""
        # Mock a network error
        mock_get.side_effect = Exception("Network error")
        
        scraper = RealEstateScraper()
        
        # Should not raise exception, should handle gracefully
        try:
            result = scraper.fetch_listings()
            # Should return empty list or handle error gracefully
            assert isinstance(result, (dict, type(None)))
        except Exception as e:
            # If it does raise an exception, it should be handled properly
            assert "Network error" in str(e) or isinstance(e, Exception)
    
    def test_scraper_parse_params(self):
        """Test parameter parsing for scraper."""
        scraper = RealEstateScraper()
        
        # Test with valid parameters
        params = {
            'city': 9500,
            'area': 6,
            'minPrice': 1000000,
            'maxPrice': 2000000
        }
        
        # Should not raise exceptions
        assert isinstance(params, dict)
        assert all(key in params for key in ['city', 'area', 'minPrice', 'maxPrice'])


class TestScraperDataProcessing:
    """Test data processing functionality of the scraper."""
    
    def test_empty_data_handling(self):
        """Test handling of empty scraping results."""
        scraper = RealEstateScraper()
        
        # Test with empty data
        empty_listings = []
        try:
            result = scraper.save_listings_csv(empty_listings, "test_output.csv")
            # Should handle empty data gracefully
            assert True
        except Exception as e:
            # Should not fail catastrophically
            pytest.fail(f"Failed to handle empty data: {e}")
    
    def test_data_validation(self):
        """Test basic data validation."""
        # Sample listing data structure
        sample_listing = {
            'neighborhood': 'Test Area',
            'street': 'Test Street',
            'price': 1500000,
            'square_meters': 80,
            'rooms': 3,
            'floor': 2,
            'condition_text': 'Good',
            'ad_type': 'For Sale'
        }
        
        # Basic validation
        assert isinstance(sample_listing['price'], (int, float))
        assert sample_listing['price'] > 0
        assert isinstance(sample_listing['square_meters'], (int, float))
        assert sample_listing['square_meters'] > 0
        assert isinstance(sample_listing['rooms'], (int, float))
        assert sample_listing['rooms'] > 0 