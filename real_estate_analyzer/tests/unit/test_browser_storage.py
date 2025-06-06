"""Unit tests for browser storage components."""
import unittest
from datetime import datetime, timedelta
import json
import pandas as pd


from src.storage.models import DatasetMetadata, StorageInfo, DatasetSummary
from src.storage.browser_storage import BrowserStorageManager, StorageQuotaError
from src.data.models import PropertyDataFrame


class TestDatasetMetadata(unittest.TestCase):
    """Test DatasetMetadata model."""

    def test_default_values(self):
        """Test default values are properly set."""
        metadata = DatasetMetadata()

        self.assertIsInstance(metadata.id, str)
        self.assertEqual(metadata.name, "Untitled Dataset")
        self.assertIsInstance(metadata.created_at, datetime)
        self.assertIsInstance(metadata.updated_at, datetime)
        self.assertEqual(metadata.scraped_params, {})
        self.assertEqual(metadata.property_count, 0)
        self.assertEqual(metadata.size_bytes, 0)
        self.assertEqual(metadata.tags, [])

    def test_custom_values(self):
        """Test custom values assignment."""
        custom_date = datetime(2023, 1, 1)
        metadata = DatasetMetadata(
            name="Test Dataset",
            created_at=custom_date,
            property_count=100,
            tags=["test", "sample"]
        )

        self.assertEqual(metadata.name, "Test Dataset")
        self.assertEqual(metadata.created_at, custom_date)
        self.assertEqual(metadata.property_count, 100)
        self.assertEqual(metadata.tags, ["test", "sample"])

    def test_to_dict(self):
        """Test dictionary conversion."""
        metadata = DatasetMetadata(name="Test")
        data = metadata.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data['name'], "Test")
        self.assertIn('id', data)
        self.assertIn('created_at', data)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'id': 'test-id',
            'name': 'Test Dataset',
            'property_count': 50,
            'tags': ['test']
        }

        metadata = DatasetMetadata.from_dict(data)

        self.assertEqual(metadata.id, 'test-id')
        self.assertEqual(metadata.name, 'Test Dataset')
        self.assertEqual(metadata.property_count, 50)
        self.assertEqual(metadata.tags, ['test'])


class TestStorageInfo(unittest.TestCase):
    """Test StorageInfo model."""

    def test_default_values(self):
        """Test default storage info values."""
        info = StorageInfo()

        self.assertEqual(info.total_datasets, 0)
        self.assertEqual(info.total_size_bytes, 0)
        self.assertEqual(info.estimated_quota_bytes, 0)
        # Check the actual default value from the model
        self.assertIsInstance(info.supports_local_storage, bool)
        self.assertIsInstance(info.supports_compression, bool)

    def test_usage_percentage_calculation(self):
        """Test usage percentage calculation."""
        info = StorageInfo(
            total_size_bytes=10 * 1024 * 1024,  # 10MB
            estimated_quota_bytes=50 * 1024 * 1024  # 50MB
        )

        self.assertEqual(info.usage_percentage, 20.0)

    def test_usage_percentage_zero_quota(self):
        """Test usage percentage with zero quota."""
        info = StorageInfo(total_size_bytes=1000, estimated_quota_bytes=0)
        self.assertEqual(info.usage_percentage, 0.0)


class TestBrowserStorageManager(unittest.TestCase):
    """Test BrowserStorageManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = BrowserStorageManager()

        # Mock property data
        import pandas as pd
        self.mock_properties = PropertyDataFrame(pd.DataFrame([
            {
                'id': '1',
                'city': 'Tel Aviv',
                'price': 1000000,
                'rooms': 3,
                'square_meters': 100,
                'property_type': 'apartment',
                'lat': 32.0853,
                'lng': 34.7818
            }
        ]))

    def test_initialization(self):
        """Test storage manager initialization."""
        self.assertIsInstance(self.storage, BrowserStorageManager)
        self.assertEqual(self.storage.storage_key, "real_estate_analyzer")
        self.assertEqual(self.storage.max_datasets, 10)
        self.assertEqual(self.storage.max_size_bytes, 50 * 1024 * 1024)

    def test_generate_dataset_name(self):
        """Test dataset name generation."""
        scraped_params = {
            'city': 9500,
            'min_price': 1000000,
            'max_price': 1500000,
            'min_rooms': 3,
            'max_rooms': 4
        }

        dataset_name = self.storage.generate_dataset_name(scraped_params)

        self.assertIsInstance(dataset_name, str)
        self.assertGreater(len(dataset_name), 0)
        self.assertIn('City', dataset_name)

    def test_create_dataset_summary(self):
        """Test dataset summary creation."""
        metadata = DatasetMetadata(
            name="Test Dataset",
            description="Test description",
            scraped_params={'city': 'Tel Aviv'},
            property_count=100
        )

        summary = self.storage.create_dataset_summary(
            self.mock_properties, metadata)

        self.assertIsInstance(summary, DatasetSummary)
        self.assertEqual(summary.metadata.name, "Test Dataset")
        self.assertEqual(summary.metadata.description, "Test description")

    def test_prepare_dataset_for_storage(self):
        """Test dataset preparation for storage."""
        metadata = DatasetMetadata(name="Test")

        payload = self.storage.prepare_dataset_for_storage(
            self.mock_properties, metadata
        )

        self.assertIsInstance(payload, dict)
        self.assertIn('metadata', payload)
        self.assertIn('data', payload)
        self.assertIn('version', payload)
        self.assertIn('stored_at', payload)

        # Check data is JSON serializable
        json.dumps(payload)  # Should not raise exception

    def test_calculate_storage_info(self):
        """Test storage info calculation."""
        metadata_list = [
            DatasetMetadata(name="Dataset 1",
                            property_count=50, size_bytes=1000),
            DatasetMetadata(name="Dataset 2",
                            property_count=30, size_bytes=800),
        ]

        storage_info = self.storage.calculate_storage_info(metadata_list)

        self.assertIsInstance(storage_info, StorageInfo)
        self.assertEqual(storage_info.total_datasets, 2)
        self.assertEqual(storage_info.total_size_bytes, 1800)

    def test_validate_storage_constraints_success(self):
        """Test storage constraints validation - success case."""
        # Should not raise exception for small dataset
        self.storage.validate_storage_constraints(
            new_dataset_size=1000,
            current_datasets_count=5
        )

    def test_validate_storage_constraints_max_datasets(self):
        """Test storage constraints validation - max datasets exceeded."""
        with self.assertRaises(StorageQuotaError) as cm:
            self.storage.validate_storage_constraints(
                new_dataset_size=1000,
                current_datasets_count=10  # At max limit
            )

        self.assertIn("Maximum number of datasets", str(cm.exception))

    def test_validate_storage_constraints_size_limit(self):
        """Test storage constraints validation - size limit exceeded."""
        large_size = 60 * 1024 * 1024  # 60MB (exceeds 50MB limit)

        with self.assertRaises(StorageQuotaError) as cm:
            self.storage.validate_storage_constraints(
                new_dataset_size=large_size,
                current_datasets_count=5
            )

        self.assertIn("Dataset size", str(cm.exception))

    def test_get_storage_recommendations(self):
        """Test storage recommendations generation."""
        storage_info = StorageInfo(
            total_datasets=5,
            total_size_bytes=1000,
            estimated_quota_bytes=10000
        )

        recommendations = self.storage.get_storage_recommendations(
            storage_info)

        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_cleanup_old_datasets(self):
        """Test old dataset cleanup identification."""
        old_date = datetime.now() - timedelta(days=35)
        recent_date = datetime.now() - timedelta(days=5)

        metadata_list = [
            DatasetMetadata(name="Old Dataset", created_at=old_date),
            DatasetMetadata(name="Recent Dataset", created_at=recent_date),
        ]

        cleanup_ids = self.storage.cleanup_old_datasets(
            metadata_list, max_age_days=30)

        self.assertIsInstance(cleanup_ids, list)
        # Only old dataset should be flagged
        self.assertEqual(len(cleanup_ids), 1)


class TestPropertyDataFrameExtensions(unittest.TestCase):
    """Test PropertyDataFrame JSON serialization extensions."""

    def setUp(self):
        """Set up test data."""
        self.properties = PropertyDataFrame(pd.DataFrame([
            {
                'id': '1',
                'city': 'Tel Aviv',
                'price': 1000000,
                'rooms': 3,
                'square_meters': 100,
                'scraped_at': datetime.now()
            },
            {
                'id': '2',
                'city': 'Haifa',
                'price': 800000,
                'rooms': 2,
                'square_meters': 80,
                'scraped_at': datetime.now()
            }
        ]))

    def test_to_json_storage(self):
        """Test JSON storage conversion."""
        json_str = self.properties.to_json_storage()

        self.assertIsInstance(json_str, str)

        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)

        # Check first property
        prop = parsed[0]
        self.assertEqual(prop['id'], '1')
        self.assertEqual(prop['city'], 'Tel Aviv')
        self.assertEqual(prop['price'], 1000000)

    def test_from_json_storage(self):
        """Test creation from JSON storage."""
        json_str = self.properties.to_json_storage()

        # Create new PropertyDataFrame from JSON
        restored = PropertyDataFrame.from_json_storage(json_str)

        self.assertIsInstance(restored, PropertyDataFrame)
        self.assertEqual(len(restored), 2)
        self.assertEqual(restored.data.iloc[0]['city'], 'Tel Aviv')
        self.assertEqual(restored.data.iloc[1]['city'], 'Haifa')

    def test_empty_dataframe_json(self):
        """Test JSON conversion of empty dataframe."""
        empty_df = PropertyDataFrame(pd.DataFrame())
        json_str = empty_df.to_json_storage()

        self.assertEqual(json_str, '[]')

        # Restore empty dataframe
        restored = PropertyDataFrame.from_json_storage(json_str)
        self.assertTrue(restored.is_empty)

    def test_datetime_serialization(self):
        """Test datetime serialization in JSON."""
        json_str = self.properties.to_json_storage()
        parsed = json.loads(json_str)

        # scraped_at should be ISO string
        scraped_at = parsed[0].get('scraped_at')
        if scraped_at:
            # Should be valid ISO format
            datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))


class TestStorageIntegration(unittest.TestCase):
    """Integration tests for storage components."""

    def test_full_storage_workflow(self):
        """Test complete storage workflow."""
        storage = BrowserStorageManager()

        # Create test data
        properties = PropertyDataFrame(pd.DataFrame([{
            'id': '1',
            'city': 'Tel Aviv',
            'price': 1000000,
            'rooms': 3,
            'square_meters': 100,
            'property_type': 'apartment',
            'lat': 32.0853,
            'lng': 34.7818
        }]))

        # Create metadata manually
        metadata = DatasetMetadata(
            name="Integration Test",
            property_count=1,
            scraped_params={'city': 'Tel Aviv'}
        )

        # Prepare for storage
        payload = storage.prepare_dataset_for_storage(properties, metadata)

        # Validate constraints
        storage.validate_storage_constraints(
            new_dataset_size=payload['metadata']['size_bytes'],
            current_datasets_count=0
        )

        # Create summary
        summary = storage.create_dataset_summary(properties, metadata)

        self.assertIsInstance(summary, DatasetSummary)
        self.assertEqual(summary.metadata.name, "Integration Test")
        self.assertIsInstance(payload, dict)
        self.assertIn('metadata', payload)
        self.assertIn('data', payload)


if __name__ == '__main__':
    unittest.main()
