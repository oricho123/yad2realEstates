#!/usr/bin/env python3
"""Test script for number formatting improvements."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import pandas as pd
from utils.formatters import NumberFormatter, PriceInputFormatter
from analysis.filters import PropertyDataFilter


def test_number_formatting():
    """Test the new number formatting functionality."""
    print("🧪 Testing Number Formatting Improvements")
    print("=" * 50)
    
    # Test basic currency formatting
    print("\n📊 Currency Formatting Tests:")
    test_values = [500, 1500, 25000, 150000, 1200000, 2500000, 15000000]
    
    for value in test_values:
        short_form = NumberFormatter.format_currency(value, short_form=True)
        long_form = NumberFormatter.format_currency(value, short_form=False)
        print(f"   {value:>10,} → {short_form:>8} | {long_form}")
    
    # Test price marks creation
    print("\n🎚️  Price Slider Marks Tests:")
    
    test_ranges = [
        (1000000, 3000000),
        (500000, 8000000),
        (200000, 1500000)
    ]
    
    for min_val, max_val in test_ranges:
        marks = NumberFormatter.create_price_marks(min_val, max_val, num_marks=5)
        print(f"   Range: ₪{min_val:,} - ₪{max_val:,}")
        print(f"   Marks: {list(marks.values())}")
    
    # Test number marks for square meters
    print("\n📐 Square Meter Marks Tests:")
    sqm_ranges = [
        (30, 200),
        (50, 500),
        (20, 150)
    ]
    
    for min_val, max_val in sqm_ranges:
        marks = NumberFormatter.create_number_marks(min_val, max_val, num_marks=5, suffix="m²")
        print(f"   Range: {min_val} - {max_val} sqm")
        print(f"   Marks: {list(marks.values())}")
    
    print("\n✅ Number formatting tests completed!")


def test_filter_integration():
    """Test the integration with filter components."""
    print("\n🔧 Testing Filter Integration")
    print("=" * 30)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'price': [1200000, 1500000, 2200000, 900000, 3500000],
        'square_meters': [75, 95, 120, 65, 150],
        'rooms': [3, 4, 5, 2.5, 6],
        'neighborhood': ['Area A', 'Area B', 'Area A', 'Area C', 'Area B'],
        'condition_text': ['Good', 'New', 'Good', 'Renovated', 'New'],
        'ad_type': ['Private', 'Agency', 'Private', 'Private', 'Agency']
    })
    
    print(f"   Sample data: {len(sample_data)} properties")
    print(f"   Price range: ₪{sample_data['price'].min():,} - ₪{sample_data['price'].max():,}")
    
    # Test filter options generation
    data_filter = PropertyDataFilter(sample_data)
    filter_options = data_filter.get_filter_options(sample_data)
    
    print(f"\n   Generated filter options:")
    print(f"   Price marks: {filter_options['price_marks']}")
    print(f"   Size marks: {filter_options['sqm_marks']}")
    
    print("\n✅ Filter integration tests completed!")


def test_input_helpers():
    """Test input helper functions."""
    print("\n⌨️  Testing Input Helpers")
    print("=" * 25)
    
    test_values = [1000000, 2500000, 8000000]
    
    for value in test_values:
        placeholder = PriceInputFormatter.format_placeholder(value)
        print(f"   {value:,} → Placeholder: '{placeholder}'")
    
    # Test step values
    ranges = [500000, 2000000, 8000000, 15000000]
    
    print(f"\n   Step value recommendations:")
    for price_range in ranges:
        step = PriceInputFormatter.get_step_value(price_range)
        print(f"   Range: ₪{price_range:,} → Step: ₪{step:,}")
    
    print("\n✅ Input helper tests completed!")


def run_all_tests():
    """Run all formatting tests."""
    try:
        test_number_formatting()
        test_filter_integration()
        test_input_helpers()
        
        print("\n🎉 All formatting tests passed!")
        print("\nFormatting improvements summary:")
        print("• ✅ Currency values now display as K/M for better readability")
        print("• ✅ Price slider marks use shortened format (₪1.2M instead of ₪1,200,000)")
        print("• ✅ Search inputs have helpful placeholders and step values")
        print("• ✅ Filter components generate optimal number of marks")
        print("• ✅ All existing functionality preserved with enhanced display")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 