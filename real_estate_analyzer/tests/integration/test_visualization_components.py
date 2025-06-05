#!/usr/bin/env python3
"""Test script for Phase 2A visualization components."""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def create_test_data():
    """Create sample property data for testing."""
    np.random.seed(42)
    n_properties = 15
    
    # Generate realistic property data
    neighborhoods = ['Kiryat Bialik', 'Kiryat Yam', 'Kiryat Motzkin', 'Haifa Center', 'Neve Shaanan']
    conditions = ['חדש/משופץ', 'במצב טוב', 'דרוש שיפוץ']
    ad_types = ['פרטי', 'תיווך']
    
    data = {
        'price': np.random.normal(1400000, 200000, n_properties),
        'square_meters': np.random.normal(90, 20, n_properties),
        'rooms': np.random.choice([2, 2.5, 3, 3.5, 4, 4.5, 5], n_properties),
        'neighborhood': np.random.choice(neighborhoods, n_properties),
        'condition_text': np.random.choice(conditions, n_properties),
        'ad_type': np.random.choice(ad_types, n_properties),
        'street': [f"Street {i}" for i in range(n_properties)],
        'floor': np.random.choice(['קרקע', '1', '2', '3', '4'], n_properties),
        'lat': np.random.uniform(32.7, 32.9, n_properties),
        'lng': np.random.uniform(35.0, 35.2, n_properties),
        'full_url': [f"https://example.com/property/{i}" for i in range(n_properties)]
    }
    
    df = pd.DataFrame(data)
    
    # Ensure positive values
    df['price'] = df['price'].abs()
    df['square_meters'] = df['square_meters'].abs()
    
    # Calculate price per sqm
    df['price_per_sqm'] = df['price'] / df['square_meters']
    
    return df

def test_map_view():
    """Test PropertyMapView component."""
    print("🗺️  Testing PropertyMapView...")
    
    from visualization.charts.map_view import PropertyMapView
    
    test_data = create_test_data()
    map_view = PropertyMapView(test_data)
    
    # Test map creation
    fig = map_view.create_map_figure()
    assert fig is not None, "Map figure should be created"
    
    # Test summary
    summary = map_view.get_property_locations_summary()
    assert summary['total_properties'] == len(test_data), "Should have correct property count"
    assert summary['with_location'] > 0, "Should have properties with location data"
    
    # Test with empty data
    empty_map = PropertyMapView(pd.DataFrame())
    empty_fig = empty_map.create_map_figure()
    assert empty_fig is not None, "Should handle empty data gracefully"
    
    print("✅ PropertyMapView tests passed!")

def test_scatter_plot():
    """Test PropertyScatterPlot component."""
    print("📊 Testing PropertyScatterPlot...")
    
    from visualization.charts.scatter_plot import PropertyScatterPlot
    
    test_data = create_test_data()
    scatter_plot = PropertyScatterPlot(test_data)
    
    # Test scatter plot creation
    fig = scatter_plot.create_enhanced_scatter_plot()
    assert fig is not None, "Scatter plot figure should be created"
    
    # Test value analysis summary
    summary = scatter_plot.get_value_analysis_summary()
    assert summary['total_properties'] == len(test_data), "Should have correct property count"
    assert 'value_categories' in summary, "Should have value categories"
    
    print("✅ PropertyScatterPlot tests passed!")

def test_analytics_charts():
    """Test PropertyAnalyticsCharts component."""
    print("📈 Testing PropertyAnalyticsCharts...")
    
    from visualization.charts.analytics import PropertyAnalyticsCharts
    
    test_data = create_test_data()
    analytics = PropertyAnalyticsCharts(test_data)
    
    # Test analytics dashboard creation
    charts = analytics.create_analytics_dashboard()
    assert isinstance(charts, dict), "Should return dict of charts"
    assert 'price_histogram' in charts, "Should include price histogram"
    assert 'neighborhood_ranking' in charts, "Should include neighborhood ranking"
    
    # Test individual chart creation
    histogram = analytics.create_price_histogram()
    assert histogram is not None, "Price histogram should be created"
    
    # Test analytics summary
    summary = analytics.get_analytics_summary()
    assert summary['analytics_available'] == True, "Analytics should be available"
    
    print("✅ PropertyAnalyticsCharts tests passed!")

def test_table_components():
    """Test PropertyTableComponents."""
    print("📋 Testing PropertyTableComponents...")
    
    from visualization.components.tables import PropertyTableComponents
    
    test_data = create_test_data()
    tables = PropertyTableComponents(test_data)
    
    # Test best deals table
    best_deals = tables.create_best_deals_table()
    assert best_deals is not None, "Best deals table should be created"
    
    # Test market insights
    insights = tables.create_market_insights_summary()
    assert insights is not None, "Market insights should be created"
    
    # Test summary stats
    stats = tables.create_summary_statistics_cards()
    assert stats is not None, "Summary statistics should be created"
    
    print("✅ PropertyTableComponents tests passed!")

def test_chart_factory():
    """Test PropertyVisualizationFactory."""
    print("🏭 Testing PropertyVisualizationFactory...")
    
    from visualization.charts.factory import PropertyVisualizationFactory
    
    test_data = create_test_data()
    factory = PropertyVisualizationFactory(test_data)
    
    # Test creating all charts
    all_charts = factory.create_all_charts()
    assert isinstance(all_charts, dict), "Should return dict of all charts"
    assert 'scatter_plot' in all_charts, "Should include scatter plot"
    assert 'map_view' in all_charts, "Should include map view"
    
    # Test creating specific chart type
    scatter = factory.create_chart_by_type('scatter_plot')
    assert scatter is not None, "Should create specific chart type"
    
    # Test dependencies
    deps = factory.get_chart_dependencies()
    assert deps['total_properties'] == len(test_data), "Should report correct property count"
    assert deps['has_location_data'] == True, "Should detect location data"
    
    # Test chart summaries
    summaries = factory.get_chart_summaries()
    assert 'map_view' in summaries, "Should include map view summary"
    
    # Test available chart types
    available = factory.get_available_chart_types()
    assert isinstance(available, dict), "Should return dict of available types"
    
    print("✅ PropertyVisualizationFactory tests passed!")

def test_chart_utils():
    """Test ChartUtils utility functions."""
    print("🛠️  Testing ChartUtils...")
    
    from visualization.charts.utils import ChartUtils
    
    test_data = create_test_data()
    
    # Test empty figure creation
    empty_fig = ChartUtils.create_empty_figure("Test Figure")
    assert empty_fig is not None, "Should create empty figure"
    
    # Test street display preparation
    street_display = ChartUtils.prepare_street_display(test_data)
    assert len(street_display) == len(test_data), "Should have same length as data"
    
    # Test trend line calculation
    x_data = test_data['square_meters'].values
    y_data = test_data['price'].values
    trend_line, success = ChartUtils.calculate_trend_line(x_data, y_data)
    assert success == True, "Should successfully calculate trend line"
    assert len(trend_line) == len(x_data), "Trend line should have same length"
    
    # Test currency formatting
    formatted = ChartUtils.format_currency(1500000)
    assert '₪' in formatted, "Should include currency symbol"
    
    print("✅ ChartUtils tests passed!")

def run_comprehensive_test():
    """Run all visualization component tests."""
    print("🚀 Starting Phase 2A Visualization Components Test Suite")
    print("=" * 60)
    
    try:
        test_map_view()
        test_scatter_plot()
        test_analytics_charts()
        test_table_components()
        test_chart_factory()
        test_chart_utils()
        
        print("=" * 60)
        print("🎉 All Phase 2A visualization tests passed successfully!")
        print("📊 Chart components are working correctly")
        print("🔧 Factory pattern implementation successful")
        print("✨ Ready for Phase 2B: Dashboard Restructuring")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 