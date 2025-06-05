"""
Pytest configuration and fixtures for real estate analyzer tests.
"""
import pytest
import pandas as pd
import sys
from pathlib import Path

# Add the real_estate_analyzer directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "real_estate_analyzer"))

@pytest.fixture
def sample_property_data():
    """Create sample property data for testing."""
    return pd.DataFrame({
        'neighborhood': ['Tel Aviv Center', 'Ramat Aviv', 'Jaffa'],
        'street': ['Dizengoff St', 'Einstein St', 'Yefet St'],
        'price': [2500000, 3200000, 1800000],
        'square_meters': [90, 120, 75],
        'rooms': [3, 4, 2],
        'floor': [3, 5, 1],
        'condition_text': ['Good', 'Excellent', 'Renovated'],
        'ad_type': ['For Sale', 'For Sale', 'For Sale'],
        'price_per_sqm': [27778, 26667, 24000],
        'full_url': ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
    })

@pytest.fixture
def empty_dataframe():
    """Create an empty dataframe for testing edge cases."""
    from real_estate_analyzer import create_empty_dataframe
    return create_empty_dataframe()

@pytest.fixture
def mock_dash_app():
    """Create a mock Dash app for testing."""
    import dash
    return dash.Dash(__name__)