#!/usr/bin/env python3
"""Test script to verify UI fixes for Best Deals links and Summary Statistics."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data.models import PropertyDataFrame
from src.visualization.components.tables import PropertyTableComponents
from src.analysis.statistical import StatisticalCalculator
from src.dashboard.callbacks.visualization import VisualizationCallbackManager


def create_test_data_with_urls() -> PropertyDataFrame:
    """Create test property data with URLs."""
    np.random.seed(42)
    
    # Create realistic property data
    test_data = []
    for i in range(15):
        property_data = {
            'id': f'test_{i+1}',
            'price': np.random.randint(1200000, 2000000),
            'square_meters': np.random.randint(60, 120),
            'rooms': np.random.choice([2.5, 3, 3.5, 4, 4.5, 5]),
            'neighborhood': np.random.choice(['Center', 'North Tel Aviv', 'South Tel Aviv', 'Ramat Aviv', 'Jaffa']),
            'street': f'Test Street {i+1}',
            'condition_text': np.random.choice(['חדש/משופץ', 'במצב טוב', 'דרוש שיפוץ']),
            'ad_type': np.random.choice(['Private', 'Agency']),
            'lat': 32.0 + np.random.uniform(-0.1, 0.1),
            'lng': 34.7 + np.random.uniform(-0.1, 0.1),
            'full_url': f'https://www.yad2.co.il/item/{i+1000}' if i < 12 else '',  # Some without URLs
            'scraped_at': datetime.now()
        }
        
        # Calculate price per sqm
        property_data['price_per_sqm'] = property_data['price'] / property_data['square_meters']
        
        test_data.append(property_data)
    
    df = pd.DataFrame(test_data)
    return PropertyDataFrame(df)


def test_best_deals_table_links():
    """Test that best deals table includes clickable links."""
    print("🔗 Testing Best Deals Table Links...")
    
    # Create test data
    property_data = create_test_data_with_urls()
    
    # Create table components
    table_components = PropertyTableComponents(property_data.data)
    
    # Generate best deals table
    best_deals_table = table_components.create_best_deals_table(max_deals=5)
    
    # Verify table is created successfully
    if best_deals_table is None:
        print("❌ Best deals table creation failed")
        return False
    
    # Convert to string to check for URL elements
    table_html = str(best_deals_table)
    
    # Check for clickable elements
    has_links = 'target="_blank"' in table_html
    has_view_button = 'View Listing' in table_html
    has_url_pattern = 'yad2.co.il' in table_html
    
    print(f"✅ Best deals table created successfully")
    print(f"   - Contains clickable links: {'✅' if has_links else '❌'}")
    print(f"   - Contains 'View Listing' buttons: {'✅' if has_view_button else '❌'}")
    print(f"   - Contains property URLs: {'✅' if has_url_pattern else '❌'}")
    
    return has_links and has_view_button


def test_summary_statistics():
    """Test that summary statistics show non-zero values."""
    print("\n📊 Testing Summary Statistics...")
    
    # Create test data
    property_data = create_test_data_with_urls()
    
    # Calculate statistics using StatisticalCalculator
    stats_calculator = StatisticalCalculator(property_data.data)
    summary_stats = stats_calculator.calculate_summary_statistics()
    
    print(f"✅ Statistics calculated for {len(property_data.data)} properties")
    
    # Check key statistics
    price_stats = summary_stats.get('price_stats', {})
    size_stats = summary_stats.get('size_stats', {})
    data_quality = summary_stats.get('data_quality', {})
    
    avg_price = price_stats.get('avg_price', 0)
    avg_price_per_sqm = price_stats.get('avg_price_per_sqm', 0)
    avg_size = size_stats.get('avg_size', 0)
    avg_rooms = size_stats.get('avg_rooms', 0)
    completeness = data_quality.get('completeness_score', 0)
    
    print(f"   - Average Price: ₪{avg_price:,.0f} {'✅' if avg_price > 0 else '❌'}")
    print(f"   - Average Price/SQM: ₪{avg_price_per_sqm:,.0f} {'✅' if avg_price_per_sqm > 0 else '❌'}")
    print(f"   - Average Size: {avg_size:.0f}m² {'✅' if avg_size > 0 else '❌'}")
    print(f"   - Average Rooms: {avg_rooms:.1f} {'✅' if avg_rooms > 0 else '❌'}")
    print(f"   - Data Quality: {completeness:.0f}% {'✅' if completeness > 0 else '❌'}")
    
    # Test the visualization callback display function
    viz_callback = VisualizationCallbackManager(None)  # Mock app
    stats_display = viz_callback._create_summary_stats_display(summary_stats, len(property_data.data))
    
    # Check if display component was created
    display_html = str(stats_display)
    has_currency_symbol = '₪' in display_html
    has_percentage = '%' in display_html
    has_proper_formatting = ':,' in str(avg_price) or avg_price > 1000000
    
    print(f"   - Display component created: {'✅' if stats_display else '❌'}")
    print(f"   - Contains currency formatting: {'✅' if has_currency_symbol else '❌'}")
    print(f"   - Contains percentage values: {'✅' if has_percentage else '❌'}")
    
    all_values_positive = all([
        avg_price > 0,
        avg_price_per_sqm > 0,
        avg_size > 0,
        avg_rooms > 0,
        completeness > 0
    ])
    
    return all_values_positive


def test_summary_statistics_cards():
    """Test the summary statistics cards from PropertyTableComponents."""
    print("\n🃏 Testing Summary Statistics Cards...")
    
    # Create test data
    property_data = create_test_data_with_urls()
    
    # Create table components
    table_components = PropertyTableComponents(property_data.data)
    
    # Generate summary statistics cards
    summary_cards = table_components.create_summary_statistics_cards()
    
    # Verify cards are created successfully
    if summary_cards is None:
        print("❌ Summary statistics cards creation failed")
        return False
    
    # Convert to string to check for values
    cards_html = str(summary_cards)
    
    # Check for non-zero values
    has_currency = '₪' in cards_html
    has_numbers = any(str(i) in cards_html for i in range(1, 10))
    has_sqm = 'sqm' in cards_html
    
    print(f"✅ Summary statistics cards created successfully")
    print(f"   - Contains currency values: {'✅' if has_currency else '❌'}")
    print(f"   - Contains numeric values: {'✅' if has_numbers else '❌'}")
    print(f"   - Contains size units: {'✅' if has_sqm else '❌'}")
    
    # Test specific values in the data
    avg_price = property_data.data['price'].mean()
    print(f"   - Test data average price: ₪{avg_price:,.0f}")
    
    return has_currency and has_numbers


def run_all_ui_tests():
    """Run all UI fix tests."""
    print("🔧 Real Estate Analyzer UI Fixes Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Best Deals Table Links
    try:
        result1 = test_best_deals_table_links()
        test_results.append(("Best Deals Links", result1))
    except Exception as e:
        print(f"❌ Best Deals Links test failed: {e}")
        test_results.append(("Best Deals Links", False))
    
    # Test 2: Summary Statistics
    try:
        result2 = test_summary_statistics()
        test_results.append(("Summary Statistics", result2))
    except Exception as e:
        print(f"❌ Summary Statistics test failed: {e}")
        test_results.append(("Summary Statistics", False))
    
    # Test 3: Summary Statistics Cards
    try:
        result3 = test_summary_statistics_cards()
        test_results.append(("Summary Statistics Cards", result3))
    except Exception as e:
        print(f"❌ Summary Statistics Cards test failed: {e}")
        test_results.append(("Summary Statistics Cards", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All UI fixes working correctly!")
        return True
    else:
        print("⚠️  Some UI fixes need attention")
        return False


if __name__ == "__main__":
    success = run_all_ui_tests()
    sys.exit(0 if success else 1) 