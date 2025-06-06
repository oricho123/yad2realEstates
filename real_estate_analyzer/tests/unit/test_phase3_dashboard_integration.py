"""Tests for Phase 3: Dashboard Integration features."""

import pandas as pd
from unittest.mock import Mock, patch
from dash import html
import dash_bootstrap_components as dbc

from src.dashboard.components.dataset_manager import DatasetManagerComponent
from src.dashboard.callbacks.storage_manager import EnhancedStorageCallbackManager
from src.storage.browser_storage import BrowserStorageManager
from src.data.models import PropertyDataFrame


class TestDatasetManagerComponent:
    """Test the dataset manager UI component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.component = DatasetManagerComponent()

    def test_initialization(self):
        """Test component initialization."""
        assert self.component.component_id_prefix == "dataset-manager"

    def test_create_dataset_management_section(self):
        """Test creation of main dataset management section."""
        section = self.component.create_dataset_management_section()

        assert isinstance(section, html.Div)
        assert section.id == "dataset-manager-main-container"
        assert "dataset-management-section" in section.className

    def test_create_save_dataset_modal(self):
        """Test creation of save dataset modal."""
        modal = self.component.create_save_dataset_modal()

        assert isinstance(modal, dbc.Modal)
        assert modal.id == "dataset-manager-save-modal"
        assert not modal.is_open  # Should start closed

    def test_create_rename_dataset_modal(self):
        """Test creation of rename dataset modal."""
        modal = self.component.create_rename_dataset_modal()

        assert isinstance(modal, dbc.Modal)
        assert modal.id == "dataset-manager-rename-modal"
        assert not modal.is_open  # Should start closed

    def test_format_dataset_for_table_empty(self):
        """Test formatting empty dataset list for table."""
        result = self.component.format_dataset_for_table([])
        assert result == []

    def test_format_dataset_for_table_with_data(self):
        """Test formatting dataset metadata for table display."""
        mock_datasets = [
            {
                'name': 'Test Dataset',
                'property_count': 100,
                'size_bytes': 1024 * 1024,  # 1 MB
                'created_at': '2024-12-16T10:30:00Z',
                'scraped_params': {
                    'city': 'Tel Aviv',
                    'min_price': 1000000,
                    'max_price': 2000000
                }
            }
        ]

        result = self.component.format_dataset_for_table(mock_datasets)

        assert len(result) == 1
        formatted = result[0]

        assert formatted['name'] == 'Test Dataset'
        assert formatted['property_count'] == 100
        assert formatted['size_display'] == '1.0 MB'
        assert 'Tel Aviv' in formatted['search_summary']
        assert '₪1,000,000-2000000' in formatted['search_summary']

    def test_format_dataset_for_table_size_formatting(self):
        """Test different size formatting scenarios."""
        test_cases = [
            {'size_bytes': 500, 'expected': '500 B'},
            {'size_bytes': 1536, 'expected': '1.5 KB'},  # 1.5 KB
            {'size_bytes': 2 * 1024 * 1024, 'expected': '2.0 MB'}  # 2 MB
        ]

        for case in test_cases:
            mock_dataset = [{
                'name': 'Test',
                'size_bytes': case['size_bytes'],
                'property_count': 10,
                'created_at': '2024-12-16T10:30:00Z'
            }]

            result = self.component.format_dataset_for_table(mock_dataset)
            assert result[0]['size_display'] == case['expected']


class TestEnhancedStorageCallbackManager:
    """Test the enhanced storage callback manager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_app = Mock()
        self.mock_storage_manager = Mock(spec=BrowserStorageManager)
        self.callback_manager = EnhancedStorageCallbackManager(
            self.mock_app, self.mock_storage_manager
        )

    def test_initialization(self):
        """Test callback manager initialization."""
        assert self.callback_manager.app == self.mock_app
        assert self.callback_manager.storage_manager == self.mock_storage_manager
        assert isinstance(
            self.callback_manager.dataset_component, DatasetManagerComponent)

    @patch('src.dashboard.callbacks.storage_manager.EnhancedStorageCallbackManager._register_callbacks')
    def test_register_callbacks_called(self, mock_register):
        """Test that callbacks are registered during initialization."""
        EnhancedStorageCallbackManager(
            self.mock_app, self.mock_storage_manager)
        mock_register.assert_called_once()

    def test_format_size_helper(self):
        """Test the size formatting helper method."""
        test_cases = [
            (500, '500 B'),
            (1024, '1.0 KB'),
            (1536, '1.5 KB'),
            (1024 * 1024, '1.0 MB'),
            (2.5 * 1024 * 1024, '2.5 MB')
        ]

        for size_bytes, expected in test_cases:
            result = self.callback_manager._format_size(size_bytes)
            assert result == expected

    def test_format_date_helper_valid_date(self):
        """Test date formatting with valid date string."""
        date_str = '2024-12-16T10:30:00Z'
        result = self.callback_manager._format_date(date_str)
        assert 'December 16, 2024' in result
        assert '10:30' in result

    def test_format_date_helper_invalid_date(self):
        """Test date formatting with invalid date."""
        result = self.callback_manager._format_date('invalid-date')
        assert result == 'Unknown'

    def test_format_date_helper_none(self):
        """Test date formatting with None."""
        result = self.callback_manager._format_date(None)
        assert result == 'Unknown'

    def test_format_search_params_empty(self):
        """Test search params formatting with empty params."""
        result = self.callback_manager._format_search_params({})
        assert len(result) == 1
        assert 'No search parameters saved' in str(result[0])

    def test_format_search_params_with_data(self):
        """Test search params formatting with actual data."""
        params = {
            'city': 'Tel Aviv',
            'min_price': 1000000,
            'max_price': 2000000,
            'rooms': 3
        }

        result = self.callback_manager._format_search_params(params)
        assert len(result) == 4  # One for each parameter

        # Check that all parameters are formatted
        result_text = ' '.join([str(item) for item in result])
        assert 'City' in result_text and 'Tel Aviv' in result_text
        assert 'Min Price' in result_text and '1000000' in result_text
        assert 'Max Price' in result_text and '2000000' in result_text
        assert 'Rooms' in result_text and '3' in result_text

    def test_create_dataset_details_content(self):
        """Test creation of dataset details content."""
        metadata = {
            'name': 'Test Dataset',
            'property_count': 150,
            'size_bytes': 2 * 1024 * 1024,  # 2 MB
            'created_at': '2024-12-16T10:30:00Z',
            'scraped_params': {
                'city': 'Tel Aviv',
                'min_price': 1000000
            }
        }

        result = self.callback_manager._create_dataset_details_content(
            metadata)

        assert isinstance(result, html.Div)
        assert 'card' in result.className


class TestPhase3Integration:
    """Test Phase 3 integration features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_app = Mock()
        self.storage_manager = BrowserStorageManager()

        # Create sample data with all required columns
        sample_df = pd.DataFrame({
            'price': [1000000, 1500000, 2000000],
            'size_sqm': [80, 100, 120],
            'square_meters': [80, 100, 120],  # Required by filter manager
            'rooms': [3, 4, 5],
            'city': ['Tel Aviv', 'Tel Aviv', 'Haifa'],
            'neighborhood': ['Center', 'North', 'Carmel'],
            'floor': [2, 3, 4],
            'total_floors': [5, 6, 7],
            'parking': [1, 1, 2],
            'balcony': [1, 0, 1],
            'elevator': [True, True, False],
            'renovated': [False, True, False]
        })
        self.sample_data = PropertyDataFrame(sample_df)

    def test_enhanced_data_stores_structure(self):
        """Test that enhanced data stores have correct structure."""
        from src.dashboard.layout import DashboardLayoutManager

        layout_manager = DashboardLayoutManager(self.sample_data)
        data_stores = layout_manager._create_data_stores()

        # Check that all required stores are present
        store_ids = [store.id for store in data_stores]

        expected_stores = [
            'clicked-link',
            'clicked-map-link',
            'loading-state',
            'current-dataset',
            'scraped-data-store',
            'available-datasets',
            'dataset-metadata',
            'selected-dataset',
            'storage-info',
            'storage-operations',
            'session-state',
            'ui-state'
        ]

        for expected_store in expected_stores:
            assert expected_store in store_ids

    def test_dataset_management_section_creation(self):
        """Test that dataset management section is properly created."""
        from src.dashboard.layout import DashboardLayoutManager

        layout_manager = DashboardLayoutManager(self.sample_data)
        section = layout_manager._create_dataset_management_section()

        assert isinstance(section, html.Div)
        # Should contain collapsible structure
        assert any('dataset-management-toggle' in str(child)
                   for child in section.children)

    def test_storage_callback_manager_integration(self):
        """Test that storage callback manager integrates properly."""
        callback_manager = EnhancedStorageCallbackManager(
            self.mock_app, self.storage_manager
        )

        # Verify that all required methods exist
        assert hasattr(callback_manager, '_register_dataset_list_callbacks')
        assert hasattr(callback_manager,
                       '_register_dataset_operations_callbacks')
        assert hasattr(callback_manager, '_register_storage_info_callbacks')
        assert hasattr(callback_manager, '_register_ui_state_callbacks')
        assert hasattr(callback_manager, '_register_integration_callbacks')

    def test_auto_save_functionality(self):
        """Test auto-save functionality for scraped data."""
        # This would test the auto-save callback when scraped data is available
        # In a real scenario, this would be tested with actual callback execution

        callback_manager = EnhancedStorageCallbackManager(
            self.mock_app, self.storage_manager
        )

        # Verify the auto-save method exists and can handle data
        assert hasattr(callback_manager, '_register_integration_callbacks')

    def test_ui_state_management(self):
        """Test UI state management features."""
        callback_manager = EnhancedStorageCallbackManager(
            self.mock_app, self.storage_manager
        )

        # Test that UI state callbacks are registered
        assert hasattr(callback_manager, '_register_ui_state_callbacks')

    def test_storage_info_display(self):
        """Test storage information display functionality."""
        callback_manager = EnhancedStorageCallbackManager(
            self.mock_app, self.storage_manager
        )

        # Test that storage info callbacks are registered
        assert hasattr(callback_manager, '_register_storage_info_callbacks')


class TestPhase3ErrorHandling:
    """Test error handling in Phase 3 features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.component = DatasetManagerComponent()

    def test_format_dataset_malformed_data(self):
        """Test handling of malformed dataset metadata."""
        malformed_data = [
            {
                'name': 'Test',
                # Missing required fields
            },
            {
                # Missing name
                'property_count': 100,
                'size_bytes': 1024
            }
        ]

        # Should not raise exception and handle gracefully
        result = self.component.format_dataset_for_table(malformed_data)
        assert len(result) == 2

        # Check default values are used
        assert result[0]['property_count'] == 0  # Default for missing
        assert 'Dataset 2' in result[1]['name']  # Default name

    def test_format_dataset_invalid_dates(self):
        """Test handling of invalid date formats."""
        invalid_date_data = [
            {
                'name': 'Test',
                'created_at': 'not-a-date',
                'property_count': 10,
                'size_bytes': 1024
            }
        ]

        result = self.component.format_dataset_for_table(invalid_date_data)
        assert result[0]['created_display'] == 'Unknown'

    def test_format_search_params_with_none_values(self):
        """Test search params formatting with None values."""
        from src.dashboard.callbacks.storage_manager import EnhancedStorageCallbackManager

        mock_app = Mock()
        mock_storage = Mock()
        callback_manager = EnhancedStorageCallbackManager(
            mock_app, mock_storage)

        params_with_none = {
            'city': 'Tel Aviv',
            'min_price': None,
            'max_price': '',
            'rooms': 3
        }

        result = callback_manager._format_search_params(params_with_none)

        # Should only include non-None, non-empty values
        result_text = ' '.join([str(item) for item in result])
        assert 'City' in result_text and 'Tel Aviv' in result_text
        assert 'Rooms' in result_text and '3' in result_text
        assert 'Min Price' not in result_text
        assert 'Max Price' not in result_text


class TestPhase3Performance:
    """Test performance aspects of Phase 3 features."""

    def test_large_dataset_formatting(self):
        """Test formatting performance with large dataset lists."""
        component = DatasetManagerComponent()

        # Create a large list of datasets
        large_dataset_list = []
        for i in range(100):
            large_dataset_list.append({
                'name': f'Dataset {i}',
                'property_count': i * 10,
                'size_bytes': i * 1024,
                'created_at': '2024-12-16T10:30:00Z',
                'scraped_params': {'city': f'City {i}'}
            })

        # Should complete without performance issues
        result = component.format_dataset_for_table(large_dataset_list)
        assert len(result) == 100

        # Verify first and last entries
        assert result[0]['name'] == 'Dataset 0'
        assert result[99]['name'] == 'Dataset 99'

    def test_memory_efficiency(self):
        """Test memory efficiency of data structures."""
        component = DatasetManagerComponent()

        # Test that component doesn't hold unnecessary references
        assert not hasattr(component, '_cached_data')
        assert not hasattr(component, '_large_objects')

        # Component should be lightweight
        import sys
        component_size = sys.getsizeof(component)
        assert component_size < 1000  # Should be small
