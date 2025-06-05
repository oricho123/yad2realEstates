#!/usr/bin/env python3
"""Test script for structured hover data implementation."""

from visualization.charts.scatter_plot import (
    PropertyHoverData,
    HoverTemplate,
    HoverDataFields,
    PropertyScatterPlot
)
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path for imports (3 levels up: tests/unit/../.. -> project root -> src)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_property_hover_data():
    """Test PropertyHoverData dataclass functionality."""
    print("🧪 Testing PropertyHoverData...")

    # Create a sample DataFrame row
    sample_data = {
        'neighborhood': 'Tel Aviv',
        'rooms': 3.5,
        'price': 1800000,
        'price_per_sqm': 25000,
        'condition_text': 'Good',
        'ad_type': 'Sale',
        'street': 'Dizengoff St',
        'floor': '5',
        'full_url': 'https://example.com',
        'value_score': -5.2,
        'value_category': 'Good Deal',
        'predicted_price': 2000000,
        'savings_amount': 100000
    }

    row = pd.Series(sample_data)
    hover_data = PropertyHoverData.from_row(row)

    # Test that we get the expected values
    assert hover_data.neighborhood == 'Tel Aviv'
    assert hover_data.rooms == 3  # Should be converted to int
    assert hover_data.price == 1800000  # Test the new price field
    assert hover_data.price_per_sqm == 25000
    assert hover_data.value_score == -5.2
    assert hover_data.street_display == 'Dizengoff St'

    # Test conversion to list
    data_list = hover_data.to_list()
    assert len(data_list) == 13  # Should have 13 fields now (was 12)
    assert data_list[HoverDataFields.NEIGHBORHOOD] == 'Tel Aviv'
    assert data_list[HoverDataFields.ROOMS] == 3
    # Test the new price field
    assert data_list[HoverDataFields.PRICE] == 1800000
    assert data_list[HoverDataFields.VALUE_SCORE] == -5.2

    print("✅ PropertyHoverData tests passed!")


def test_hover_template():
    """Test HoverTemplate functionality."""
    print("🧪 Testing HoverTemplate...")

    template = HoverTemplate.build_property_hover_template()

    # Test that template contains expected field references
    assert f'customdata[{HoverDataFields.NEIGHBORHOOD}]' in template
    assert f'customdata[{HoverDataFields.VALUE_SCORE}]' in template
    assert f'customdata[{HoverDataFields.PREDICTED_PRICE}]' in template

    # Test that template is not empty and contains expected sections
    assert '🏡' in template  # Property icon
    assert 'Property Details' in template
    assert 'Market Value Analysis' in template
    assert 'Value Score Explanation' in template

    print("✅ HoverTemplate tests passed!")


def test_enum_consistency():
    """Test that enum values match PropertyHoverData field order."""
    print("🧪 Testing enum consistency...")

    # Create a sample hover data object
    sample_data = {
        'neighborhood': 'Test',
        'rooms': 3,
        'price': 1500000,
        'price_per_sqm': 20000,
        'condition_text': 'Good',
        'ad_type': 'Sale',
        'street': 'Test St',
        'floor': '3',
        'full_url': 'https://test.com',
        'value_score': 0.0,
        'value_category': 'Fair Price',
        'predicted_price': 1500000,
        'savings_amount': 0
    }

    row = pd.Series(sample_data)
    hover_data = PropertyHoverData.from_row(row)
    data_list = hover_data.to_list()

    # Test that enum indices match the actual data positions
    assert data_list[HoverDataFields.NEIGHBORHOOD] == hover_data.neighborhood
    assert data_list[HoverDataFields.ROOMS] == hover_data.rooms
    assert data_list[HoverDataFields.PRICE] == hover_data.price
    assert data_list[HoverDataFields.PRICE_PER_SQM] == hover_data.price_per_sqm
    assert data_list[HoverDataFields.VALUE_SCORE] == hover_data.value_score
    assert data_list[HoverDataFields.VALUE_CATEGORY] == hover_data.value_category

    print("✅ Enum consistency tests passed!")


def test_integration_with_scatter_plot():
    """Test integration with PropertyScatterPlot."""
    print("🧪 Testing integration with PropertyScatterPlot...")

    # Create sample DataFrame
    sample_df = pd.DataFrame([
        {
            'price': 1800000,
            'square_meters': 90,
            'rooms': 3.5,
            'neighborhood': 'Tel Aviv',
            'street': 'Rothschild Blvd',
            'condition_text': 'Excellent',
            'ad_type': 'Sale',
            'floor': '4',
            'full_url': 'https://example.com/1',
            'price_per_sqm': 20000
        },
        {
            'price': 2200000,
            'square_meters': 110,
            'rooms': 4,
            'neighborhood': 'Jerusalem',
            'street': 'King George St',
            'condition_text': 'Good',
            'ad_type': 'Sale',
            'floor': '2',
            'full_url': 'https://example.com/2',
            'price_per_sqm': 20000
        }
    ])

    # Create scatter plot
    scatter_plot = PropertyScatterPlot(sample_df)
    fig = scatter_plot.create_enhanced_scatter_plot()

    # Test that figure is created successfully
    assert fig is not None
    assert len(fig.data) > 0  # Should have scatter plot data

    # Test that custom data is properly structured
    scatter_trace = fig.data[0]  # First trace should be the scatter plot
    assert hasattr(scatter_trace, 'customdata')
    assert scatter_trace.customdata is not None

    print("✅ Integration tests passed!")


def main():
    """Run all tests."""
    print("🚀 Testing Structured Hover Data Implementation")
    print("=" * 50)

    try:
        test_property_hover_data()
        test_hover_template()
        test_enum_consistency()
        test_integration_with_scatter_plot()

        print("\n🎉 All tests passed! The structured hover data implementation is working correctly.")
        print("\n📋 Benefits of the new implementation:")
        print("   ✅ Type-safe data structures with PropertyHoverData")
        print("   ✅ Named field access instead of magic numbers")
        print("   ✅ Centralized hover template generation")
        print("   ✅ Easy to maintain and extend")
        print("   ✅ Clear separation of concerns")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
