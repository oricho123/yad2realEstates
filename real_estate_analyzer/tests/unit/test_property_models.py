import pytest
import pandas as pd
from src.data.models import PropertyListing, PropertyDataFrame

def test_property_listing_creation():
    """Test creating a PropertyListing with basic data."""
    listing = PropertyListing(
        price=1500000,
        square_meters=100,
        rooms=3.5
    )
    assert listing.price == 1500000
    assert listing.square_meters == 100
    assert listing.price_per_sqm == 15000

def test_property_dataframe_empty():
    """Test creating an empty PropertyDataFrame."""
    empty_df = PropertyDataFrame(pd.DataFrame())
    assert empty_df.is_empty is True