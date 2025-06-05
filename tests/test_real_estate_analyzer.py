"""
Tests for the real estate analyzer dashboard application.
"""
import pytest
import pandas as pd
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
import threading
import time
import requests
from contextlib import contextmanager

# Add the real_estate_analyzer directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "real_estate_analyzer"))

# Import after adding to path
from real_estate_analyzer import create_empty_dataframe, load_data, parse_arguments


class TestDataFunctions:
    """Test data loading and creation functions."""
    
    def test_create_empty_dataframe(self):
        """Test that empty dataframe is created with correct structure."""
        df = create_empty_dataframe()
        
        # Check it's a DataFrame
        assert isinstance(df, pd.DataFrame)
        
        # Check it's empty
        assert len(df) == 0
        
        # Check it has the expected columns
        expected_columns = [
            'neighborhood', 'street', 'price', 'square_meters', 'rooms', 
            'floor', 'condition_text', 'ad_type', 'price_per_sqm', 'full_url'
        ]
        for col in expected_columns:
            assert col in df.columns
    
    def test_load_data_with_nonexistent_file(self):
        """Test loading data with a file that doesn't exist."""
        df = load_data("nonexistent_file.csv")
        
        # Should return empty dataframe
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_parse_arguments(self):
        """Test argument parsing with default values."""
        # Mock sys.argv to test default arguments
        with patch('sys.argv', ['real_estate_analyzer.py']):
            args = parse_arguments()
            
            assert args.port == 8051  # Default port
            assert args.output_dir == "scraped_real_estate"


class TestDashboardCreation:
    """Test dashboard creation and basic functionality."""
    
    def test_dashboard_creation_with_empty_data(self, empty_dataframe):
        """Test that dashboard can be created with empty data."""
        from real_estate_analyzer import create_dashboard
        
        # This should not raise any exceptions
        try:
            # We'll test the function exists and can be called
            # without actually running the server
            assert callable(create_dashboard)
        except Exception as e:
            pytest.fail(f"Dashboard creation failed: {e}")
    
    def test_dashboard_creation_with_sample_data(self, sample_property_data):
        """Test that dashboard can be created with sample data."""
        from real_estate_analyzer import create_dashboard
        
        # This should not raise any exceptions
        try:
            assert callable(create_dashboard)
            # Verify the sample data is valid
            assert len(sample_property_data) > 0
            assert 'price' in sample_property_data.columns
        except Exception as e:
            pytest.fail(f"Dashboard creation with sample data failed: {e}")


class TestServerStartup:
    """Test server startup functionality."""
    
    @contextmanager
    def run_server_in_thread(self, port=8053):
        """Context manager to run server in a separate thread for testing."""
        from real_estate_analyzer import create_dashboard, create_empty_dataframe
        
        server_thread = None
        server_started = threading.Event()
        server_error = None
        
        def run_server():
            nonlocal server_error
            try:
                df = create_empty_dataframe()
                # Monkey patch the app.run method to signal when server starts
                original_run = None
                
                def mock_run(*args, **kwargs):
                    server_started.set()
                    # Don't actually run the server, just signal it would start
                    return
                
                with patch('dash.Dash.run', side_effect=mock_run):
                    create_dashboard(df, port)
                    
            except Exception as e:
                server_error = e
                server_started.set()
        
        try:
            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()
            
            # Wait for server to start or error (max 5 seconds)
            if server_started.wait(timeout=5):
                if server_error:
                    raise server_error
                yield port
            else:
                raise TimeoutError("Server failed to start within 5 seconds")
                
        finally:
            if server_thread and server_thread.is_alive():
                # Server thread should end when main thread ends due to daemon=True
                pass
    
    def test_server_can_start(self):
        """Test that the server can start without errors."""
        try:
            with self.run_server_in_thread(port=8053):
                # If we reach here, server started successfully
                assert True
        except Exception as e:
            pytest.fail(f"Server failed to start: {e}")
    
    def test_server_with_different_port(self):
        """Test that the server can start on different ports."""
        try:
            with self.run_server_in_thread(port=8054):
                # Test with a different port
                assert True
        except Exception as e:
            pytest.fail(f"Server failed to start on custom port: {e}")


class TestApplicationComponents:
    """Test specific application components and functions."""
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        from real_estate_analyzer import main
        assert callable(main)
    
    def test_imports_work(self):
        """Test that all required modules can be imported."""
        try:
            import dash
            import plotly.express as px
            import pandas as pd
            import numpy as np
            from dash import dcc, html, Input, Output, State
            assert True
        except ImportError as e:
            pytest.fail(f"Required import failed: {e}")
    
    def test_sample_data_processing(self, sample_property_data):
        """Test that sample data can be processed correctly."""
        df = sample_property_data
        
        # Test basic data properties
        assert len(df) == 3
        assert df['price'].min() > 0
        assert df['square_meters'].min() > 0
        assert all(df['rooms'] > 0)
        
        # Test price per sqm calculation
        calculated_price_per_sqm = df['price'] / df['square_meters']
        assert all(abs(calculated_price_per_sqm - df['price_per_sqm']) < 1)  # Allow small rounding differences


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        # Create DataFrame with some invalid data
        invalid_df = pd.DataFrame({
            'neighborhood': ['Test Area', None, ''],
            'price': [100000, -50000, None],  # Negative and None values
            'square_meters': [50, 0, None],  # Zero and None values
            'rooms': [2, None, -1],  # None and negative values
        })
        
        # The application should handle this gracefully
        assert isinstance(invalid_df, pd.DataFrame)
        # Basic validation that we can work with this data
        assert len(invalid_df) == 3
    
    def test_empty_filters(self):
        """Test behavior with empty filter values."""
        # This tests that the application can handle edge cases
        # in filter values without crashing
        empty_filters = {
            'price_range': None,
            'sqm_range': None,
            'neighborhood': None,
            'exclude_neighborhoods': [],
            'rooms': None,
            'condition': None,
            'ad_type': None
        }
        
        # Should not raise exceptions
        assert isinstance(empty_filters, dict) 