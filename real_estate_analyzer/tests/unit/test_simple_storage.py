"""Tests for SimpleStorageManager."""
import pandas as pd
from datetime import datetime
from src.storage.simple_storage import SimpleStorageManager
from src.data.models import PropertyDataFrame


class TestSimpleStorageManager:
    """Test suite for SimpleStorageManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.storage_manager = SimpleStorageManager()

    def test_initialization(self):
        """Test SimpleStorageManager initialization."""
        assert self.storage_manager.STORAGE_KEY == 'real_estate_data'
        assert self.storage_manager.get_storage_key() == 'real_estate_data'

    def test_prepare_data_for_storage_with_property_dataframe(self):
        """Test preparing PropertyDataFrame for storage."""
        # Create test data
        test_data = pd.DataFrame({
            'price': [1000000, 1500000],
            'square_meters': [100, 150],
            'rooms': [3, 4],
            'lat': [32.0, 32.1],
            'lng': [34.8, 34.9],
            'scraped_at': [datetime.now(), datetime.now()]
        })
        property_df = PropertyDataFrame(test_data)

        # Prepare for storage
        storage_payload = self.storage_manager.prepare_data_for_storage(
            property_df)

        # Verify structure
        assert 'data' in storage_payload
        assert 'property_count' in storage_payload
        assert 'saved_at' in storage_payload
        assert 'version' in storage_payload

        # Verify content
        assert storage_payload['property_count'] == 2
        assert storage_payload['version'] == '1.0'
        assert len(storage_payload['data']) == 2

    def test_prepare_data_for_storage_with_pandas_dataframe(self):
        """Test preparing regular pandas DataFrame for storage."""
        # Create test data
        test_data = pd.DataFrame({
            'price': [1000000, 1500000],
            'square_meters': [100, 150],
            'rooms': [3, 4]
        })

        # Prepare for storage
        storage_payload = self.storage_manager.prepare_data_for_storage(
            test_data)

        # Verify structure
        assert 'data' in storage_payload
        assert 'property_count' in storage_payload
        assert storage_payload['property_count'] == 2
        assert len(storage_payload['data']) == 2

    def test_prepare_data_for_storage_with_empty_dataframe(self):
        """Test preparing empty DataFrame for storage."""
        empty_df = PropertyDataFrame(pd.DataFrame())

        storage_payload = self.storage_manager.prepare_data_for_storage(
            empty_df)

        assert storage_payload['property_count'] == 0
        assert storage_payload['data'] == []

    def test_prepare_data_from_storage_with_valid_data(self):
        """Test converting storage data back to PropertyDataFrame."""
        # Create test storage data
        storage_data = {
            'data': [
                {
                    'price': 1000000,
                    'square_meters': 100,
                    'rooms': 3,
                    'lat': 32.0,
                    'lng': 34.8,
                    'scraped_at': '2024-01-01T10:00:00'
                },
                {
                    'price': 1500000,
                    'square_meters': 150,
                    'rooms': 4,
                    'lat': 32.1,
                    'lng': 34.9,
                    'scraped_at': '2024-01-01T11:00:00'
                }
            ],
            'property_count': 2,
            'saved_at': '2024-01-01T12:00:00',
            'version': '1.0'
        }

        # Convert back to PropertyDataFrame
        restored_df = self.storage_manager.prepare_data_from_storage(
            storage_data)

        # Verify restoration
        assert isinstance(restored_df, PropertyDataFrame)
        assert len(restored_df) == 2
        assert not restored_df.is_empty

        # Check data types
        data = restored_df.data
        assert pd.api.types.is_numeric_dtype(data['price'])
        assert pd.api.types.is_numeric_dtype(data['square_meters'])
        assert pd.api.types.is_datetime64_any_dtype(data['scraped_at'])

    def test_prepare_data_from_storage_with_empty_data(self):
        """Test converting empty storage data back to PropertyDataFrame."""
        storage_data = {
            'data': [],
            'property_count': 0,
            'saved_at': '2024-01-01T12:00:00',
            'version': '1.0'
        }

        restored_df = self.storage_manager.prepare_data_from_storage(
            storage_data)

        assert isinstance(restored_df, PropertyDataFrame)
        assert len(restored_df) == 0
        assert restored_df.is_empty

    def test_prepare_data_from_storage_with_invalid_data(self):
        """Test handling invalid storage data."""
        # Invalid storage data
        invalid_data = {'invalid': 'structure'}

        # Should return empty DataFrame without crashing
        restored_df = self.storage_manager.prepare_data_from_storage(
            invalid_data)

        assert isinstance(restored_df, PropertyDataFrame)
        assert restored_df.is_empty

    def test_save_data_method(self):
        """Test save_data method (preparation only)."""
        test_data = pd.DataFrame({'price': [1000000], 'rooms': [3]})

        # Should return True if preparation successful
        result = self.storage_manager.save_data(test_data)
        assert result is True

    def test_placeholder_methods(self):
        """Test placeholder methods that will be handled client-side."""
        # These methods should return expected defaults
        assert self.storage_manager.load_data() is None
        assert self.storage_manager.has_data() is False
        assert self.storage_manager.clear_data() is False

    def test_round_trip_conversion(self):
        """Test complete round-trip: DataFrame -> Storage -> DataFrame."""
        # Create original data
        original_data = pd.DataFrame({
            'price': [1000000, 1500000, 2000000],
            'square_meters': [100, 150, 200],
            'price_per_sqm': [10000, 10000, 10000],
            'rooms': [3, 4, 5],
            'lat': [32.0, 32.1, 32.2],
            'lng': [34.8, 34.9, 35.0],
            'scraped_at': [datetime(2024, 1, 1, 10, 0), datetime(2024, 1, 1, 11, 0), datetime(2024, 1, 1, 12, 0)]
        })
        original_property_df = PropertyDataFrame(original_data)

        # Convert to storage format
        storage_payload = self.storage_manager.prepare_data_for_storage(
            original_property_df)

        # Convert back to PropertyDataFrame
        restored_property_df = self.storage_manager.prepare_data_from_storage(
            storage_payload)

        # Verify data integrity
        assert len(restored_property_df) == len(original_property_df)
        assert not restored_property_df.is_empty

        # Compare key columns (allowing for minor floating point differences)
        restored_data = restored_property_df.data
        pd.testing.assert_series_equal(
            restored_data['price'], original_data['price'])
        pd.testing.assert_series_equal(
            restored_data['square_meters'], original_data['square_meters'])
        pd.testing.assert_series_equal(
            restored_data['rooms'], original_data['rooms'])
