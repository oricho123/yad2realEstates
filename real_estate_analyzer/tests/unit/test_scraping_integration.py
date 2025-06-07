"""Tests for scraping integration with browser storage."""

import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime

from src.scraping.yad2_scraper import Yad2Scraper, ScrapingParams, ScrapingResult
from src.storage.browser_storage import BrowserStorageManager
from src.storage.models import DatasetMetadata


class TestScrapingIntegration:
    """Test scraping integration with browser storage."""

    def test_scraper_initialization(self):
        """Test that scraper initializes without file directory."""
        scraper = Yad2Scraper()
        assert scraper is not None
        assert hasattr(scraper, 'logger')
        assert hasattr(scraper, 'base_url')
        assert hasattr(scraper, 'headers')

    def test_scraping_result_structure(self):
        """Test the new ScrapingResult structure."""
        # Test successful result
        listings_data = [
            {'id': '123', 'price': 1000000, 'rooms': 3,
                'scraped_at': '2024-01-01T12:00:00'},
            {'id': '456', 'price': 1200000, 'rooms': 4,
                'scraped_at': '2024-01-01T12:00:00'}
        ]

        params = ScrapingParams(city=9500, area=6)

        result = ScrapingResult(
            success=True,
            listings_data=listings_data,
            raw_data={'data': {'markers': []}},
            listings_count=2,
            scraped_params=params
        )

        assert result.success is True
        assert len(result.listings_data) == 2
        assert result.listings_count == 2
        assert result.raw_data is not None
        assert result.scraped_params == params
        assert result.error_message is None

    def test_prepare_for_storage(self):
        """Test data preparation for browser storage."""
        scraper = Yad2Scraper()

        # Test data with various data types
        listings = [
            {
                'id': '123',
                'price': 1000000,
                'rooms': 3.5,
                'scraped_at': datetime(2024, 1, 1, 12, 0, 0),
                'description': None,
                'area': 'Test Area'
            }
        ]

        storage_ready = scraper.prepare_for_storage(listings)

        assert len(storage_ready) == 1

        # Check listing
        first = storage_ready[0]
        assert first['id'] == '123'
        assert first['price'] == 1000000
        assert first['rooms'] == 3.5
        # Converted to ISO string
        assert first['scraped_at'] == '2024-01-01T12:00:00'
        assert first['description'] is None
        assert first['area'] == 'Test Area'

    @patch('src.scraping.yad2_scraper.requests.get')
    def test_scrape_success_integration(self, mock_get):
        """Test successful scraping with browser storage integration."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'markers': [
                    {
                        'orderId': '123',
                        'token': 'test-token-123',
                        'price': 1000000,
                        'additionalDetails': {
                            'roomsCount': 3,
                            'squareMeter': 80,
                            'property': {'text': 'Apartment'}
                        },
                        'address': {
                            'city': {'text': 'Tel Aviv'},
                            'area': {'text': 'Center'},
                            'coords': {'lat': 32.0853, 'lon': 34.7818}
                        },
                        'metaData': {'coverImage': 'test.jpg', 'images': []}
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        scraper = Yad2Scraper()
        params = ScrapingParams(
            city=9500, area=6, min_price=900000, max_price=1100000)

        result = scraper.scrape(params)

        assert result.success is True
        assert len(result.listings_data) == 1
        assert result.listings_count == 1
        assert result.raw_data is not None
        assert result.scraped_params == params
        assert result.error_message is None

        # Check listing data structure
        listing = result.listings_data[0]
        assert listing['id'] == '123'
        assert listing['token'] == 'test-token-123'
        assert listing['price'] == 1000000
        assert listing['rooms'] == 3
        assert listing['square_meters'] == 80
        assert listing['city'] == 'Tel Aviv'
        assert 'scraped_at' in listing
        assert 'price_per_sqm' in listing
        assert 'full_url' in listing

    def test_storage_manager_integration(self):
        """Test integration with BrowserStorageManager."""
        storage_manager = BrowserStorageManager()

        # Create sample scraped data
        listings_data = [
            {'id': '123', 'price': 1000000, 'rooms': 3,
                'scraped_at': '2024-01-01T12:00:00'},
            {'id': '456', 'price': 1200000, 'rooms': 4,
                'scraped_at': '2024-01-01T12:00:00'}
        ]

        df = pd.DataFrame(listings_data)

        # Create metadata
        metadata = DatasetMetadata(
            name="Test Dataset",
            scraped_params={'city': 9500, 'area': 6},
            property_count=2
        )

        # Prepare for storage
        storage_payload = storage_manager.prepare_dataset_for_storage(
            df, metadata)

        assert 'data' in storage_payload
        assert 'metadata' in storage_payload
        assert len(storage_payload['data']) == 2
        assert storage_payload['metadata']['name'] == "Test Dataset"
        assert storage_payload['metadata']['property_count'] == 2
