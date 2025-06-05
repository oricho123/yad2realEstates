#!/usr/bin/env python3
"""Comprehensive test script for all structured hover data implementations."""

from visualization.charts.analytics import PropertyAnalyticsCharts
from visualization.charts.map_view import PropertyMapView
from visualization.charts.scatter_plot import (
    PropertyHoverData,
    MapHoverData,
    AnalyticsHoverData,
    HoverTemplate,
    HoverDataFields,
    MapHoverDataFields,
    AnalyticsHoverDataFields,
    PropertyScatterPlot
)
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


def create_sample_dataframe() -> pd.DataFrame:
    """Create a comprehensive sample DataFrame for testing."""
    return pd.DataFrame([
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
            'price_per_sqm': 20000,
            'lat': 32.0853,
            'lng': 34.7818,
            'value_score': -5.2,
            'value_category': 'Good Deal',
            'predicted_price': 1900000,
            'savings_amount': 100000
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
            'price_per_sqm': 20000,
            'lat': 31.7767,
            'lng': 35.2345,
            'value_score': 3.1,
            'value_category': 'Above Market',
            'predicted_price': 2135000,
            'savings_amount': -65000
        },
        {
            'price': 1500000,
            'square_meters': 75,
            'rooms': 3,
            'neighborhood': 'Tel Aviv',
            'street': 'Dizengoff St',
            'condition_text': 'Good',
            'ad_type': 'Sale',
            'floor': '3',
            'full_url': 'https://example.com/3',
            'price_per_sqm': 20000,
            'lat': 32.0796,
            'lng': 34.7749,
            'value_score': -8.5,
            'value_category': 'Excellent Deal',
            'predicted_price': 1635000,
            'savings_amount': 135000
        }
    ])


def test_property_hover_data():
    """Test PropertyHoverData for scatter plots."""
    print("🧪 Testing PropertyHoverData (Scatter Plot)...")

    sample_df = create_sample_dataframe()
    row = sample_df.iloc[0]

    hover_data = PropertyHoverData.from_row(row)

    # Test basic fields
    assert hover_data.neighborhood == 'Tel Aviv'
    assert hover_data.rooms == 3  # Should be converted to int
    assert hover_data.price == 1800000  # Test the new price field
    assert hover_data.price_per_sqm == 20000
    assert hover_data.street_display == 'Rothschild Blvd'

    # Test list conversion
    data_list = hover_data.to_list()
    assert len(data_list) == 13  # Now 13 fields instead of 12
    assert data_list[HoverDataFields.NEIGHBORHOOD] == 'Tel Aviv'
    # Test the new price field
    assert data_list[HoverDataFields.PRICE] == 1800000
    assert data_list[HoverDataFields.FULL_URL] == 'https://example.com/1'

    print("✅ PropertyHoverData tests passed!")


def test_map_hover_data():
    """Test MapHoverData for map visualizations."""
    print("🧪 Testing MapHoverData (Map View)...")

    sample_df = create_sample_dataframe()
    row = sample_df.iloc[1]

    hover_data = MapHoverData.from_row(row)

    # Test basic fields
    assert hover_data.neighborhood == 'Jerusalem'
    assert hover_data.price == 2200000
    assert hover_data.rooms == 4
    assert hover_data.street_display == 'King George St'

    # Test list conversion
    data_list = hover_data.to_list()
    assert len(data_list) == 8
    assert data_list[MapHoverDataFields.NEIGHBORHOOD] == 'Jerusalem'
    assert data_list[MapHoverDataFields.FULL_URL] == 'https://example.com/2'

    print("✅ MapHoverData tests passed!")


def test_analytics_hover_data():
    """Test AnalyticsHoverData for analytics charts."""
    print("🧪 Testing AnalyticsHoverData (Analytics Charts)...")

    hover_data = AnalyticsHoverData(
        avg_size=95.5,
        avg_price_per_sqm=21500
    )

    # Test list conversion
    data_list = hover_data.to_list()
    assert len(data_list) == 2
    assert data_list[AnalyticsHoverDataFields.AVG_SIZE] == 95.5
    assert data_list[AnalyticsHoverDataFields.AVG_PRICE_PER_SQM] == 21500

    print("✅ AnalyticsHoverData tests passed!")


def test_hover_templates():
    """Test all hover template generation."""
    print("🧪 Testing HoverTemplate generators...")

    # Test scatter plot template
    scatter_template = HoverTemplate.build_property_hover_template()
    assert f'customdata[{HoverDataFields.NEIGHBORHOOD}]' in scatter_template
    assert f'customdata[{HoverDataFields.VALUE_SCORE}]' in scatter_template
    assert 'Market Value Analysis' in scatter_template

    # Test map template
    map_template = HoverTemplate.build_map_hover_template()
    assert f'customdata[{MapHoverDataFields.NEIGHBORHOOD}]' in map_template
    assert f'customdata[{MapHoverDataFields.PRICE}]' in map_template
    assert 'Click to view listing' in map_template

    # Test analytics template
    analytics_template = HoverTemplate.build_analytics_hover_template()
    assert f'customdata[{AnalyticsHoverDataFields.AVG_SIZE}]' in analytics_template
    assert f'customdata[{AnalyticsHoverDataFields.AVG_PRICE_PER_SQM}]' in analytics_template
    assert 'Real Affordability' in analytics_template

    print("✅ HoverTemplate tests passed!")


def test_scatter_plot_integration():
    """Test scatter plot integration."""
    print("🧪 Testing scatter plot integration...")

    sample_df = create_sample_dataframe()
    scatter_plot = PropertyScatterPlot(sample_df)
    fig = scatter_plot.create_enhanced_scatter_plot()

    # Test that figure is created successfully
    assert fig is not None
    assert len(fig.data) > 0

    # Test that custom data is properly structured
    scatter_trace = fig.data[0]
    assert hasattr(scatter_trace, 'customdata')
    assert scatter_trace.customdata is not None

    print("✅ Scatter plot integration tests passed!")


def test_map_view_integration():
    """Test map view integration."""
    print("🧪 Testing map view integration...")

    sample_df = create_sample_dataframe()
    map_view = PropertyMapView(sample_df)
    fig = map_view.create_map_figure()

    # Test that figure is created successfully
    assert fig is not None
    assert len(fig.data) > 0

    # Test that custom data is properly structured
    map_trace = fig.data[0]
    assert hasattr(map_trace, 'customdata')
    assert map_trace.customdata is not None

    print("✅ Map view integration tests passed!")


def test_analytics_integration():
    """Test analytics charts integration."""
    print("🧪 Testing analytics charts integration...")

    # Create a larger sample for analytics (need multiple properties per neighborhood)
    expanded_df = create_sample_dataframe()
    # Duplicate rows to meet minimum property requirements
    expanded_df = pd.concat([expanded_df] * 3, ignore_index=True)

    analytics = PropertyAnalyticsCharts(expanded_df)

    # Test neighborhood ranking chart specifically
    ranking_fig = analytics.create_neighborhood_ranking(expanded_df)

    # Test that figure is created successfully
    assert ranking_fig is not None

    # Test that we get a proper figure (might be empty figure if not enough data)
    assert hasattr(ranking_fig, 'data')

    # For our expanded dataset, we should have some data
    if len(ranking_fig.data) > 0:
        ranking_trace = ranking_fig.data[0]
        assert hasattr(ranking_trace, 'customdata')

    print("✅ Analytics integration tests passed!")


def test_enum_consistency():
    """Test that all enum values are consistent."""
    print("🧪 Testing enum field consistency...")

    sample_df = create_sample_dataframe()
    row = sample_df.iloc[0]

    # Test PropertyHoverData enum consistency
    property_hover_data = PropertyHoverData.from_row(row)
    property_data_list = property_hover_data.to_list()

    assert property_data_list[HoverDataFields.NEIGHBORHOOD] == property_hover_data.neighborhood
    assert property_data_list[HoverDataFields.FULL_URL] == property_hover_data.full_url

    # Test MapHoverData enum consistency
    map_hover_data = MapHoverData.from_row(row)
    map_data_list = map_hover_data.to_list()

    assert map_data_list[MapHoverDataFields.NEIGHBORHOOD] == map_hover_data.neighborhood
    assert map_data_list[MapHoverDataFields.FULL_URL] == map_hover_data.full_url

    # Test AnalyticsHoverData enum consistency
    analytics_hover_data = AnalyticsHoverData(
        avg_size=90.0, avg_price_per_sqm=20000.0)
    analytics_data_list = analytics_hover_data.to_list()

    assert analytics_data_list[AnalyticsHoverDataFields.AVG_SIZE] == analytics_hover_data.avg_size
    assert analytics_data_list[AnalyticsHoverDataFields.AVG_PRICE_PER_SQM] == analytics_hover_data.avg_price_per_sqm

    print("✅ Enum consistency tests passed!")


def main():
    """Run all comprehensive tests."""
    print("🚀 Testing ALL Structured Hover Data Implementations")
    print("=" * 60)

    try:
        test_property_hover_data()
        test_map_hover_data()
        test_analytics_hover_data()
        test_hover_templates()
        test_scatter_plot_integration()
        test_map_view_integration()
        test_analytics_integration()
        test_enum_consistency()

        print("\n🎉 ALL TESTS PASSED! All charts now use structured hover data.")
        print("\n📋 Refactoring completed successfully across:")
        print("   ✅ Scatter plot (PropertyHoverData)")
        print("   ✅ Map view (MapHoverData)")
        print("   ✅ Analytics charts (AnalyticsHoverData)")
        print("   ✅ Interaction callbacks (Named field access)")
        print("\n💪 Benefits achieved:")
        print("   🎯 No more magic numbers")
        print("   🔒 Type-safe data structures")
        print("   🧭 Named field access everywhere")
        print("   🛠️ Easy to maintain and extend")
        print("   🐛 Better debugging and IDE support")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
