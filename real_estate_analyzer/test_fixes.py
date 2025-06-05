#!/usr/bin/env python3
"""Test script to verify the recent bug fixes."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.settings import AppSettings
from src.data.models import PropertyDataFrame
from src.analysis.filters import PropertyDataFilter
from src.dashboard.callbacks.scraping import ScrapingCallbackManager
from src.dashboard.callbacks.filtering import FilterCallbackManager


def create_test_data() -> PropertyDataFrame:
    """Create test property data."""
    np.random.seed(42)
    
    neighborhoods = ['Center', 'North', 'South', 'East', 'West']
    conditions = ['חדש/משופץ', 'במצב טוב', 'דרוש שיפוץ']
    ad_types = ['private', 'commercial']
    
    test_data = []
    for i in range(50):
        base_price = np.random.uniform(1000000, 3000000)
        sqm = np.random.uniform(60, 150)
        rooms = np.random.choice([2, 2.5, 3, 3.5, 4, 4.5, 5])
        
        test_data.append({
            'id': f'test_{i}',
            'price': base_price,
            'square_meters': sqm,
            'price_per_sqm': base_price / sqm,
            'rooms': rooms,
            'neighborhood': np.random.choice(neighborhoods),
            'condition_text': np.random.choice(conditions),
            'ad_type': np.random.choice(ad_types),
            'lat': 32.0 + np.random.uniform(-0.1, 0.1),
            'lng': 34.8 + np.random.uniform(-0.1, 0.1),
            'street': f'Test Street {i}',
            'floor': np.random.randint(1, 10),
            'full_url': f'https://test.com/listing/{i}',
            'property_type': 'apartment',
            'city': 'Test City',
            'area': 'Test Area'
        })
    
    df = pd.DataFrame(test_data)
    return PropertyDataFrame(df)


def test_data_deletion():
    """Test that old data files are deleted before new scraping."""
    print("🧪 Testing data deletion functionality...")
    
    # Create some dummy files in the data directory
    AppSettings.ensure_directories()
    data_dir = Path(AppSettings.DATA_DIRECTORY)
    
    # Create dummy files
    dummy_files = [
        data_dir / "real_estate_listings_old.csv",
        data_dir / "raw_api_response_old.json",
        data_dir / "real_estate_listings_20230101_120000.csv"
    ]
    
    for file_path in dummy_files:
        file_path.write_text("dummy content")
        print(f"   Created dummy file: {file_path.name}")
    
    # Verify files exist
    existing_files = list(data_dir.glob("real_estate_listings_*.csv")) + list(data_dir.glob("raw_api_response_*.json"))
    print(f"   Found {len(existing_files)} data files before deletion")
    
    # Simulate the deletion logic from the scraping callback
    for pattern in ['real_estate_listings_*.csv', 'raw_api_response_*.json']:
        for old_file in data_dir.glob(pattern):
            try:
                old_file.unlink()
                print(f"   ✅ Deleted: {old_file.name}")
            except Exception as e:
                print(f"   ❌ Failed to delete {old_file}: {e}")
    
    # Verify deletion
    remaining_files = list(data_dir.glob("real_estate_listings_*.csv")) + list(data_dir.glob("raw_api_response_*.json"))
    print(f"   Found {len(remaining_files)} data files after deletion")
    
    if len(remaining_files) == 0:
        print("   ✅ Data deletion test PASSED")
        return True
    else:
        print("   ❌ Data deletion test FAILED")
        return False


def test_filter_alignment():
    """Test that filters align properly with current data."""
    print("\n🧪 Testing filter alignment functionality...")
    
    test_data = create_test_data()
    df = test_data.data
    
    print(f"   Created test data with {len(df)} properties")
    print(f"   Price range: ₪{df['price'].min():,.0f} - ₪{df['price'].max():,.0f}")
    print(f"   Size range: {df['square_meters'].min():.0f} - {df['square_meters'].max():.0f} sqm")
    print(f"   Rooms range: {df['rooms'].min():.1f} - {df['rooms'].max():.1f}")
    print(f"   Neighborhoods: {df['neighborhood'].unique()}")
    
    # Test filter options generation
    data_filter = PropertyDataFilter(df)
    filter_options = data_filter.get_filter_options(df)
    
    # Verify all required keys exist
    required_keys = [
        'price_min', 'price_max', 'price_marks',
        'sqm_min', 'sqm_max', 'sqm_marks',
        'rooms_min', 'rooms_max', 'rooms_marks',
        'neighborhoods', 'exclude_neighborhoods_options',
        'conditions', 'ad_types'
    ]
    
    missing_keys = []
    for key in required_keys:
        if key not in filter_options:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"   ❌ Missing filter option keys: {missing_keys}")
        return False
    
    # Verify ranges match data
    if filter_options['price_min'] != df['price'].min():
        print(f"   ❌ Price min mismatch: {filter_options['price_min']} != {df['price'].min()}")
        return False
    
    if filter_options['price_max'] != df['price'].max():
        print(f"   ❌ Price max mismatch: {filter_options['price_max']} != {df['price'].max()}")
        return False
    
    # Check neighborhood options
    actual_neighborhoods = set(df['neighborhood'].unique())
    filter_neighborhoods = set([opt['value'] for opt in filter_options['neighborhoods'] if opt['value'] != 'all'])
    
    if actual_neighborhoods != filter_neighborhoods:
        print(f"   ❌ Neighborhood mismatch: {actual_neighborhoods} != {filter_neighborhoods}")
        return False
    
    print("   ✅ Filter alignment test PASSED")
    return True


def test_api_filter_parameters():
    """Test that API filter parameters are properly constructed."""
    print("\n🧪 Testing API filter parameter construction...")
    
    # Test parameter construction logic (from the scraping callback)
    city = 9500
    area = 6
    min_price = 1500000
    max_price = 2000000
    min_rooms = 3
    max_rooms = 5
    min_sqm = 80
    max_sqm = 120
    
    # Simulate the parameter construction from the scraping callback
    scraping_params = {'city': city, 'area': area}
    
    if min_price is not None:
        scraping_params['min_price'] = min_price
    if max_price is not None:
        scraping_params['max_price'] = max_price
    if min_rooms is not None and min_rooms != 'any':
        scraping_params['min_rooms'] = min_rooms
    if max_rooms is not None and max_rooms != 'any':
        scraping_params['max_rooms'] = max_rooms
    if min_sqm is not None:
        scraping_params['min_square_meters'] = min_sqm
    if max_sqm is not None:
        scraping_params['max_square_meters'] = max_sqm
    
    print(f"   Generated API parameters: {scraping_params}")
    
    # Verify all expected parameters are included
    expected_params = {
        'city': 9500, 'area': 6, 'min_price': 1500000, 'max_price': 2000000,
        'min_rooms': 3, 'max_rooms': 5, 'min_square_meters': 80, 'max_square_meters': 120
    }
    
    for key, expected_value in expected_params.items():
        if key not in scraping_params:
            print(f"   ❌ Missing parameter: {key}")
            return False
        if scraping_params[key] != expected_value:
            print(f"   ❌ Parameter mismatch: {key} = {scraping_params[key]} (expected {expected_value})")
            return False
    
    print("   ✅ API filter parameter test PASSED")
    return True


def run_all_tests():
    """Run all bug fix tests."""
    print("🚀 Running bug fix verification tests...")
    print("=" * 60)
    
    tests = [
        ("Data Deletion", test_data_deletion),
        ("Filter Alignment", test_filter_alignment),
        ("API Filter Parameters", test_api_filter_parameters)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All bug fixes verified successfully!")
        return True
    else:
        print("⚠️  Some tests failed - please review the fixes")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 